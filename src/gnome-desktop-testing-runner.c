/* -*- mode: C; c-file-style: "gnu"; indent-tabs-mode: nil; -*-
 *
 * Copyright (C) 2011 Colin Walters <walters@verbum.org>
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the
 * Free Software Foundation, Inc., 59 Temple Place - Suite 330,
 * Boston, MA 02111-1307, USA.
 */


#include "config.h"
#include "libgsystem.h"
#include "gsystem-local-alloc.h"

#define TEST_SKIP_ECODE 77
#define TESTS_FAILED_MSGID     "0eee66bf98514369bef9868327a43cf1"
#define TESTS_SUCCESS_MSGID    "4d013788dd704743b826436c951e551d"
#define ONE_TEST_SUCCESS_MSGID "142bf5d40e9742e99d3ac8c1ace83b36"

static int ntests = 0;
static int n_skipped_tests = 0;
static int n_failed_tests = 0;

static gboolean
run_tests_in_directory (GFile         *file,
			GCancellable  *cancellable,
			GError       **error)
{
  gboolean ret = FALSE;
  gs_free char *suite_name = NULL;
  gs_unref_object GFileEnumerator *dir_enum = NULL;
  gs_unref_object GFileInfo *info = NULL;
  GKeyFile *keyfile = NULL;
  gs_free char *testname = NULL;
  gs_free char *exec_key = NULL;
  gs_free char *test_tmpdir = NULL;
  gs_unref_object GFile *child = NULL;
  gs_unref_object GFile *test_tmpdir_f = NULL;
  gs_free char *test_tmpname = NULL;
  gs_unref_object GSSubprocessContext *proc_context = NULL;
  gs_unref_object GSSubprocess *proc = NULL;
  GError *tmp_error = NULL;
  int test_argc;
  char **test_argv = NULL;
  gboolean test_success = TRUE;

  suite_name = g_file_get_basename (file);
  
  dir_enum = g_file_enumerate_children (file, "standard::name,standard::type",
					G_FILE_QUERY_INFO_NOFOLLOW_SYMLINKS,
					cancellable, error);
  if (!dir_enum)
    goto out;
  while ((info = g_file_enumerator_next_file (dir_enum, cancellable, &tmp_error)) != NULL)
    {
      const char *name = g_file_info_get_name (info);
      const char *child_path;
      int estatus;
      gboolean skipped = FALSE;
      gboolean failed = FALSE;
      GError *tmp_error = NULL;

      if (!g_str_has_suffix (name, ".test"))
	continue;
      
      g_clear_pointer (&testname, g_free);
      testname = g_strdup_printf ("%s/%s", suite_name, name);

      g_clear_object (&child);
      child = g_file_get_child (file, name);
      child_path = gs_file_get_path_cached (child);

      g_clear_pointer (&keyfile, g_key_file_free);
      keyfile = g_key_file_new ();
      if (!g_key_file_load_from_file (keyfile, child_path, 0, error))
	goto out;

      g_clear_pointer (&exec_key, g_free);
      exec_key = g_key_file_get_string (keyfile, "Test", "Exec", error);
      if (exec_key == NULL)
	goto out;

      g_clear_pointer (&test_argv, g_strfreev);
      if (!g_shell_parse_argv (exec_key, &test_argc, &test_argv, error))
	goto out;
      
      g_print ("Running test: %s\n", child_path);

      g_clear_pointer (&test_tmpname, g_free);
      test_tmpname = g_strconcat ("test-tmp-", name, "-XXXXXX", NULL);
      g_clear_pointer (&test_tmpdir, g_free);
      test_tmpdir = g_dir_make_tmp (test_tmpname, error);
      if (!test_tmpdir)
	goto out;

      g_clear_object (&proc_context);
      proc_context = gs_subprocess_context_new (test_argv);
      gs_subprocess_context_set_cwd (proc_context, test_tmpdir);
      g_clear_object (&proc);

      proc = gs_subprocess_new (proc_context, cancellable, error);
      if (!proc)
	goto out;
      if (!gs_subprocess_wait_sync (proc, &estatus, cancellable, error))
	goto out;
      if (!g_spawn_check_exit_status (estatus, &tmp_error))
	{
	  if (g_error_matches (tmp_error, G_SPAWN_EXIT_ERROR, 77))
	    {
	      g_print("Skipping test %s\n", child_path);
	      n_skipped_tests++;
	      skipped = TRUE;
	    }
	  else
	    {
	      char *keys[] = { "MESSAGE_ID=" TESTS_FAILED_MSGID, NULL };
	      gs_free char *msg = g_strdup_printf ("Test %s failed: %s", name, tmp_error->message);
	      gs_log_structured_print (msg, (const char* const*)keys);
	      failed = TRUE;
	    }
	  g_clear_error (&tmp_error);
	}
      else
	{
	  ntests += 1;
	}

      g_clear_object (&test_tmpdir_f);
      test_tmpdir_f = g_file_new_for_path (test_tmpdir);
      if (!gs_shutil_rm_rf (test_tmpdir_f, cancellable, error))
	goto out;

      g_clear_object (&info);

      /* For now, just exit on the first failing test */
      if (failed)
	{
	  n_failed_tests++;
	  break;
	}
      else
	{
	  char *keys[] = { "MESSAGE_ID=" ONE_TEST_SUCCESS_MSGID, NULL };
	  gs_free char *msg = g_strdup_printf ("PASS: %s", testname);
	  gs_log_structured_print (msg, (const char* const*)keys);
	}
    }
  if (tmp_error != NULL)
    {
      g_propagate_error (error, tmp_error);
      goto out;
    }
  
  ret = TRUE;
 out:
  g_clear_pointer (&keyfile, g_key_file_free);
  g_clear_pointer (&exec_key, g_free);
  g_clear_pointer (&test_argv, g_strfreev);
  return ret;
}

int
main (int argc, char **argv)
{
  gboolean ret = FALSE;
  GCancellable *cancellable = NULL;
  GError *local_error = NULL;
  GError **error = &local_error;
  int i;
  gs_unref_object GFile *prefix_root = NULL;
  GSList *testdirs = NULL;
  GSList *iter;

  prefix_root = g_file_new_for_path (DATADIR "/installed-tests");

  if (argc <= 1)
    {
      gs_unref_object GFileEnumerator *dir_enum = NULL;
      gs_unref_object GFileInfo *info = NULL;
      GError *tmp_error = NULL;

      dir_enum = g_file_enumerate_children (prefix_root, "standard::name,standard::type",
					    G_FILE_QUERY_INFO_NOFOLLOW_SYMLINKS,
					    cancellable, error);
      if (!dir_enum)
	goto out;

      while ((info = g_file_enumerator_next_file (dir_enum, cancellable, &tmp_error)) != NULL)
	{
	  if (g_file_info_get_file_type (info) == G_FILE_TYPE_DIRECTORY)
	    testdirs = g_slist_prepend (testdirs, g_file_get_child (prefix_root, g_file_info_get_name (info)));
	}
      if (tmp_error != NULL)
	{
	  g_propagate_error (error, tmp_error);
	  goto out;
	}
    }
  else
    {
      for (i = 1; i < argc; i++)
	{
	  testdirs = g_slist_prepend (testdirs, g_file_get_child (prefix_root, argv[i]));
	}
    }
  
  testdirs = g_slist_reverse (testdirs);

  for (iter = testdirs; iter; iter = iter->next)
    {
      GFile *path = iter->data;
      if (!run_tests_in_directory (path, cancellable, error))
	goto out;
    }

  {
    char *keys[] = { "MESSAGE_ID=" TESTS_SUCCESS_MSGID, NULL };
    gs_free char *msg = g_strdup_printf ("SUMMARY: passed: %d skipped: %d failed: %d",
					 ntests, n_skipped_tests, n_failed_tests);
    gs_log_structured_print (msg, (const char *const*)keys);
  }
  
  ret = TRUE;
 out:
  g_slist_foreach (testdirs, (GFunc)g_object_unref, NULL);
  g_slist_free (testdirs);
  if (!ret)
    {
      char *keys[] = { "MESSAGE_ID=" TESTS_FAILED_MSGID, NULL };
      gs_free char *msg = NULL;

      g_assert (local_error);

      msg = g_strdup_printf ("Caught exception during testing: %s", local_error->message);
      gs_log_structured_print (msg, (const char *const*)keys);
      g_clear_error (&local_error);
      return 1;
    }
  return 0;
}
