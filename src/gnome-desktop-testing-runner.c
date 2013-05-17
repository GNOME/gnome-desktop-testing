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

#include <string.h>

#define TEST_SKIP_ECODE 77
#define TESTS_COMPLETE_MSGID   "4d013788dd704743b826436c951e551d"
#define ONE_TEST_FAILED_MSGID  "0eee66bf98514369bef9868327a43cf1"
#define ONE_TEST_SKIPPED_MSGID "ca0b037012363f1898466829ea163e7d"
#define ONE_TEST_SUCCESS_MSGID "142bf5d40e9742e99d3ac8c1ace83b36"

static int ntests = 0;
static int n_skipped_tests = 0;
static int n_failed_tests = 0;

static gboolean opt_list;

static GOptionEntry options[] = {
  { "list", 'l', 0, G_OPTION_ARG_NONE, &opt_list, "List matching tests", NULL },
  { NULL }
};

static gboolean
gather_all_tests_recurse (GFile         *dir,
                          const char    *prefix,
                          GPtrArray     *tests,
                          GCancellable  *cancellable,
                          GError       **error)
{
  gboolean ret = FALSE;
  gs_unref_object GFileEnumerator *dir_enum = NULL;
  gs_unref_object GFileInfo *info = NULL;
  gs_free char *suite_name = NULL;
  gs_free char *suite_prefix = NULL;
  GError *tmp_error = NULL;

  suite_name = g_file_get_basename (dir);
  suite_prefix = g_strconcat (prefix, suite_name, "/", NULL);
  
  dir_enum = g_file_enumerate_children (dir, "standard::name,standard::type", 0,
                                        cancellable, error);
  if (!dir_enum)
    goto out;
  while ((info = g_file_enumerator_next_file (dir_enum, cancellable, &tmp_error)) != NULL)
    {
      GFileType type = g_file_info_get_file_type (info);
      const char *name = g_file_info_get_name (info);
      gs_unref_object GFile *child = g_file_get_child (dir, name);

      if (type == G_FILE_TYPE_REGULAR && g_str_has_suffix (name, ".test"))
        {
          g_ptr_array_add (tests, g_object_ref (child));
        }
      else if (type == G_FILE_TYPE_DIRECTORY)
        {
          if (!gather_all_tests_recurse (child, suite_prefix, tests,
                                         cancellable, error))
            goto out;
        }
      g_clear_object (&info);
    }
  if (tmp_error != NULL)
    {
      g_propagate_error (error, tmp_error);
      goto out;
    }

  ret = TRUE;
 out:
  return ret;
}

static gboolean
run_test (GFile         *testbase,
          GFile         *test,
          GCancellable  *cancellable,
          GError       **error)
{
  static gsize initialized;
  static GRegex *slash_regex;

  gboolean ret = FALSE;
  GKeyFile *keyfile = NULL;
  gs_free char *testname = NULL;
  gs_free char *exec_key = NULL;
  gs_free char *test_tmpdir = NULL;
  gs_unref_object GFile *test_tmpdir_f = NULL;
  gs_free char *test_squashed_name = NULL;
  gs_free char *test_tmpname = NULL;
  gs_unref_object GSSubprocessContext *proc_context = NULL;
  gs_unref_object GSSubprocess *proc = NULL;
  GError *tmp_error = NULL;
  int test_argc;
  char **test_argv = NULL;
  gboolean test_success = TRUE;
  const char *test_path;
  int estatus;

  if (g_once_init_enter (&initialized))
    {
      slash_regex = g_regex_new ("/", 0, 0, NULL);
      g_assert (slash_regex != NULL);
      g_once_init_leave (&initialized, 1);
    }

  testname = g_file_get_relative_path (testbase, test);

  test_path = gs_file_get_path_cached (test);

  keyfile = g_key_file_new ();
  if (!g_key_file_load_from_file (keyfile, test_path, 0, error))
    goto out;

  exec_key = g_key_file_get_string (keyfile, "Test", "Exec", error);
  if (exec_key == NULL)
    goto out;

  if (!g_shell_parse_argv (exec_key, &test_argc, &test_argv, error))
    goto out;
  
  g_print ("Running test: %s\n", test_path);

  test_squashed_name = g_regex_replace_literal (slash_regex, testname, -1,
                                                0, "_", 0, NULL);
  test_tmpname = g_strconcat ("test-tmp-", test_squashed_name, "-XXXXXX", NULL);
  test_tmpdir = g_dir_make_tmp (test_tmpname, error);
  if (!test_tmpdir)
    goto out;

  proc_context = gs_subprocess_context_new (test_argv);
  gs_subprocess_context_set_cwd (proc_context, test_tmpdir);

  proc = gs_subprocess_new (proc_context, cancellable, error);
  if (!proc)
    goto out;
  if (!gs_subprocess_wait_sync (proc, &estatus, cancellable, error))
    goto out;
  if (!g_spawn_check_exit_status (estatus, &tmp_error))
    {
      if (g_error_matches (tmp_error, G_SPAWN_EXIT_ERROR, 77))
        {
          char *keys[] = { "MESSAGE_ID=" ONE_TEST_SKIPPED_MSGID, NULL };
          gs_free char *msg = g_strdup_printf ("Test %s skipped (exit code 77)", testname);
          gs_log_structured_print (msg, (const char* const*)keys);
          n_skipped_tests++;
        }
      else
        {
          char *keys[] = { "MESSAGE_ID=" ONE_TEST_FAILED_MSGID, NULL };
          gs_free char *msg = g_strdup_printf ("Test %s failed: %s", testname, tmp_error->message);
          gs_log_structured_print (msg, (const char* const*)keys);
          n_failed_tests++;
        }
      g_clear_error (&tmp_error);
    }
  else
    {
      char *keys[] = { "MESSAGE_ID=" ONE_TEST_SUCCESS_MSGID, NULL };
      gs_free char *msg = g_strdup_printf ("PASS: %s", testname);
      gs_log_structured_print (msg, (const char* const*)keys);
      ntests += 1;
    }
  
  test_tmpdir_f = g_file_new_for_path (test_tmpdir);
  if (!gs_shutil_rm_rf (test_tmpdir_f, cancellable, error))
    goto out;

  ret = TRUE;
 out:
  g_clear_pointer (&keyfile, g_key_file_free);
  g_clear_pointer (&test_argv, g_strfreev);
  return ret;
}

static gint
cmp_tests (gconstpointer a,
           gconstpointer b)
{
  const char *apath = gs_file_get_path_cached (*((GFile**)a));
  const char *bpath = gs_file_get_path_cached (*((GFile**)b));

  return strcmp (apath, bpath);
}

int
main (int argc, char **argv)
{
  gboolean ret = FALSE;
  GCancellable *cancellable = NULL;
  GError *local_error = NULL;
  GError **error = &local_error;
  int i, j;
  gs_unref_object GFile *prefix_root = NULL;
  gs_unref_ptrarray GPtrArray *tests = NULL;
  GOptionContext *context;

  context = g_option_context_new ("[PREFIX...] - Run installed tests");
  g_option_context_add_main_entries (context, options, NULL);

  if (!g_option_context_parse (context, &argc, &argv, error))
    goto out;

  prefix_root = g_file_new_for_path (DATADIR "/installed-tests");

  tests = g_ptr_array_new_with_free_func (g_object_unref);

  if (!gather_all_tests_recurse (prefix_root, "", tests,
                                 cancellable, error))
    goto out;

  g_ptr_array_sort (tests, cmp_tests);

  if (argc > 1)
    {
      for (j = 0; j < tests->len; j++)
        {
          gboolean matches = FALSE;
          GFile *test = tests->pdata[j];
          gs_free char *test_relname = g_file_get_relative_path (prefix_root, test);
          for (i = 1; i < argc; i++)
            {
              const char *prefix = argv[i];
              if (g_str_has_prefix (test_relname, prefix))
                {
                  matches = TRUE;
                  break;
                }
            }
          if (matches)
            {
              if (opt_list)
                g_print ("%s\n", test_relname);
              else if (!run_test (prefix_root, test, cancellable, error))
                goto out;
            }
        }
    }
  else
    {
      for (i = 0; i < tests->len; i++)
        {
          GFile *test = tests->pdata[i];
          gs_free char *test_relname = g_file_get_relative_path (prefix_root, test);
          if (opt_list)
            g_print ("%s\n", test_relname);
          else if (!run_test (prefix_root, test, cancellable, error))
            goto out;
        }
    }

  ret = TRUE;
 out:
  if (!opt_list)
    {
      char *keys[] = { "MESSAGE_ID=" TESTS_COMPLETE_MSGID, NULL };
      gs_free char *msg = g_strdup_printf ("SUMMARY: total: %u passed: %d skipped: %d failed: %d",
                                           tests->len, ntests, n_skipped_tests, n_failed_tests);
      gs_log_structured_print (msg, (const char *const*)keys);
    }
  if (!ret)
    {
      g_assert (local_error);
      g_printerr ("Caught exception during testing: %s", local_error->message);
      g_clear_error (&local_error);
      return 1;
    }
  
  return 0;
}
