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

typedef struct {
  int pending_tests;
  GError *test_error;

  GCancellable *cancellable;
  GPtrArray *tests;

  int parallel;
  int test_index;
} TestRunnerApp;

typedef enum {
  TEST_STATE_UNLOADED,
  TEST_STATE_LOADED,
  TEST_STATE_EXECUTING,
  TEST_STATE_COMPLETE_SUCCESS,
  TEST_STATE_COMPLETE_SKIPPED,
  TEST_STATE_COMPLETE_FAILED,
} TestState;

typedef enum {
  TEST_TYPE_UNKNOWN,
  TEST_TYPE_SESSION
} TestType;

typedef struct {
  volatile gint refcount;
  GFile *prefix_root;
  GFile *path;
  GFile *tmpdir;

  char *name;
  char **argv;

  TestState state;
  TestType type;
} Test;

static void
test_unref (Test *test)
{
  if (!g_atomic_int_dec_and_test (&test->refcount))
    return;
  g_strfreev (test->argv);
  g_clear_object (&test->tmpdir);
  g_object_unref (test->prefix_root);
  g_object_unref (test->path);
}

static Test*
test_ref (Test *test)
{
  g_atomic_int_inc (&test->refcount);
  return test;
}

static gboolean
load_test (GFile         *prefix_root,
           GFile         *path,
           Test         **out_test,
           GCancellable  *cancellable,
           GError       **error)
{
  gboolean ret = FALSE;
  GKeyFile *keyfile = NULL;
  Test *test = g_new0 (Test, 1);
  int test_argc;
  gs_free char *exec_key = NULL;
  gs_free char *type_key = NULL;
  const char *test_path;

  g_assert (test->state == TEST_STATE_UNLOADED);

  test->prefix_root = g_object_ref (prefix_root);
  test->path = g_object_ref (path);

  test->name = g_file_get_relative_path (test->prefix_root, test->path);

  test_path = gs_file_get_path_cached (test->path);

  keyfile = g_key_file_new ();
  if (!g_key_file_load_from_file (keyfile, test_path, 0, error))
    goto out;

  exec_key = g_key_file_get_string (keyfile, "Test", "Exec", error);
  if (exec_key == NULL)
    goto out;

  if (!g_shell_parse_argv (exec_key, &test_argc, &test->argv, error))
    goto out;

  type_key = g_key_file_get_string (keyfile, "Test", "Type", error);
  if (type_key == NULL)
    goto out;
  if (strcmp (type_key, "session") == 0)
    {
      test->type = TEST_TYPE_SESSION;
    }
  else
    {
      g_set_error (error, G_IO_ERROR, G_IO_ERROR_FAILED,
                   "Unknown test type '%s'", type_key);
      goto out;
    }
  
  test->state = TEST_STATE_LOADED;

  ret = TRUE;
 out:
  g_prefix_error (error, "Test '%s': ", test->name);
  g_clear_pointer (&keyfile, g_key_file_free);
  if (!ret)
    test_unref (test);
  else
    *out_test = test;
  return ret;
}

static TestRunnerApp *app;

static gboolean opt_list;
static int opt_parallel = 1;
static char * opt_report_directory;
static char **opt_dirs;

static GOptionEntry options[] = {
  { "dir", 'd', 0, G_OPTION_ARG_STRING_ARRAY, &opt_dirs, "Only run tests from these dirs (default: all system data dirs)", NULL },
  { "list", 'l', 0, G_OPTION_ARG_NONE, &opt_list, "List matching tests", NULL },
  { "parallel", 'p', 0, G_OPTION_ARG_INT, &opt_parallel, "Specify parallelization to PROC processors; 0 will be dynamic)", "PROC" },
  { "report-directory", 0, 0, G_OPTION_ARG_FILENAME, &opt_report_directory, "Create a subdirectory per failing test in DIR", "DIR" },
  { NULL }
};

static gboolean
run_test_async (Test                *test,
                GCancellable        *cancellable,
                GAsyncReadyCallback  callback,
                gpointer             user_data);
static void
on_test_run_complete (GObject      *object,
                      GAsyncResult *result,
                      gpointer      user_data);

static gboolean
gather_all_tests_recurse (GFile         *prefix_root,
                          GFile         *dir,
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
          Test *test;
          if (!load_test (prefix_root, child, &test, cancellable, error))
            goto out;
          g_ptr_array_add (tests, test);
        }
      else if (type == G_FILE_TYPE_DIRECTORY)
        {
          if (!gather_all_tests_recurse (prefix_root, child, suite_prefix, tests,
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

static void
on_test_exited (GObject       *obj,
                GAsyncResult  *result,
                gpointer       user_data)
{
  GError *local_error = NULL;
  GError **error = &local_error;
  GError *tmp_error = NULL;
  int estatus;
  GSSubprocess *proc = GS_SUBPROCESS (obj);
  GTask *task = G_TASK (user_data);
  GCancellable *cancellable = g_task_get_cancellable (task);
  Test *test;
  GFile *test_tmpdir_f;
  gboolean failed = FALSE;

  test = g_object_get_data ((GObject*)task, "gdtr-test");

  g_assert (test->state == TEST_STATE_EXECUTING);

  if (!gs_subprocess_wait_finish (proc, result, &estatus, error))
    goto out;
  if (!g_spawn_check_exit_status (estatus, &tmp_error))
    {
      if (g_error_matches (tmp_error, G_SPAWN_EXIT_ERROR, 77))
        {
          test->state = TEST_STATE_COMPLETE_SKIPPED;
          gs_log_structured_print_id_v (ONE_TEST_SKIPPED_MSGID,
                                        "Test %s skipped (exit code 77)", test->name);
        }
      else
        {
          test->state = TEST_STATE_COMPLETE_FAILED;
          gs_log_structured_print_id_v (ONE_TEST_FAILED_MSGID,
                                        "Test %s failed: %s", test->name, tmp_error->message); 
          failed = TRUE;
        }
      /* Individual test failures don't count as failure of the whole process */
      g_clear_error (&tmp_error);
    }
  else
    {
      gs_log_structured_print_id_v (ONE_TEST_SUCCESS_MSGID, "PASS: %s", test->name);
      test->state = TEST_STATE_COMPLETE_SUCCESS;
    }
  
  /* Keep around temporaries from failed tests */
  if (!(failed && opt_report_directory))
    {
      if (!gs_shutil_rm_rf (test->tmpdir, cancellable, error))
        goto out;
    }

 out:
  if (local_error)
    g_task_return_error (task, local_error);
  else
    g_task_return_boolean (task, TRUE);
}

static gboolean
run_test_async (Test                *test,
                GCancellable        *cancellable,
                GAsyncReadyCallback  callback,
                gpointer             user_data)
{
  static gsize initialized;
  static GRegex *slash_regex;

  GError *local_error = NULL;
  GError **error = &local_error;
  gs_free char *testname = NULL;
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
  gboolean failed = FALSE;
  const char *test_path;
  int estatus;
  GTask *task;

  g_assert (test->state == TEST_STATE_LOADED);

  if (g_once_init_enter (&initialized))
    {
      slash_regex = g_regex_new ("/", 0, 0, NULL);
      g_assert (slash_regex != NULL);
      g_once_init_leave (&initialized, 1);
    }
  
  task = g_task_new (test->path, cancellable, callback, user_data); 

  g_print ("Running test: %s\n", test->name);

  test_squashed_name = g_regex_replace_literal (slash_regex, test->name, -1,
                                                0, "_", 0, NULL);
  if (!opt_report_directory)
    {
      test_tmpname = g_strconcat ("test-tmp-", test_squashed_name, "-XXXXXX", NULL);
      test_tmpdir = g_dir_make_tmp (test_tmpname, error);
      if (!test_tmpdir)
        goto out;
      test->tmpdir = g_file_new_for_path (test_tmpdir);
    }
  else
    {
      test_tmpdir = g_build_filename (opt_report_directory, test_squashed_name, NULL);
      test->tmpdir = g_file_new_for_path (test_tmpdir);
      if (!gs_shutil_rm_rf (test_tmpdir_f, cancellable, error))
        goto out;
      if (!gs_file_ensure_directory (test_tmpdir_f, TRUE, cancellable, error))
        goto out;
    }

  proc_context = gs_subprocess_context_new (test->argv);
  gs_subprocess_context_set_cwd (proc_context, test_tmpdir);

  proc = gs_subprocess_new (proc_context, cancellable, error);
  if (!proc)
    goto out;

  test->state = TEST_STATE_EXECUTING;

  g_object_set_data_full ((GObject*)task, "gdtr-test",
                          test_ref (test), (GDestroyNotify)test_unref);
  
  gs_subprocess_wait (proc, cancellable, on_test_exited, task);

 out:
  if (local_error)
    {
      g_task_report_error (test->path, callback, user_data, run_test_async, local_error);
    }
}

static gboolean
run_test_async_finish (GFile         *test,
                       GAsyncResult  *result,
                       GError       **error)
{
  g_return_val_if_fail (g_task_is_valid (result, test), FALSE);
  return g_task_propagate_boolean (G_TASK (result), error);
}

static void
reschedule_tests (GCancellable *cancellable)
{
  while (app->pending_tests < app->parallel
         && app->test_index < app->tests->len)
    {
      Test *test = app->tests->pdata[app->test_index];
      run_test_async (test, cancellable,
                      on_test_run_complete, NULL);
      app->pending_tests++;
      app->test_index++;
    }
}

static void
on_test_run_complete (GObject      *object,
                      GAsyncResult *result,
                      gpointer      user_data)
{
  GError *local_error = NULL;
  GError **error = &local_error;

  if (!run_test_async_finish ((GFile*)object, result, error))
    goto out;

 out:
  if (local_error)
    {
      if (!app->test_error)
        app->test_error = g_error_copy (local_error);
      g_clear_error (&local_error);
    }
  else
    {
      app->pending_tests--;
      reschedule_tests (app->cancellable);
    }
}

static gint
cmp_tests (gconstpointer adata,
           gconstpointer bdata)
{
  Test **a_pp = (gpointer)adata;
  Test **b_pp = (gpointer)bdata;
  Test *a = *a_pp;
  Test *b = *b_pp;
  const char *apath = gs_file_get_path_cached (a->path);
  const char *bpath = gs_file_get_path_cached (b->path);

  return strcmp (apath, bpath);
}

int
main (int argc, char **argv)
{
  gboolean ret = FALSE;
  GCancellable *cancellable = NULL;
  GError *local_error = NULL;
  GError **error = &local_error;
  guint total_tests = 0;
  int i, j;
  GOptionContext *context;
  TestRunnerApp appstruct;
  GPtrArray *test_paths;
  const char *const *datadirs_iter;
  int n_passed, n_skipped, n_failed;

  memset (&appstruct, 0, sizeof (appstruct));
  app = &appstruct;

  context = g_option_context_new ("[PREFIX...] - Run installed tests");
  g_option_context_add_main_entries (context, options, NULL);

  if (!g_option_context_parse (context, &argc, &argv, error))
    goto out;

  if (opt_parallel == 0)
    app->parallel = g_get_num_processors ();
  else
    app->parallel = opt_parallel;

  app->tests = g_ptr_array_new_with_free_func ((GDestroyNotify)test_unref);

  if (opt_dirs)
    datadirs_iter = (const char *const*) opt_dirs;
  else
    datadirs_iter = g_get_system_data_dirs ();
  
  for (; *datadirs_iter; datadirs_iter++)
    {
      const char *datadir = *datadirs_iter;
      gs_unref_object GFile *datadir_f = g_file_new_for_path (datadir);
      gs_unref_object GFile *prefix_root = g_file_get_child (datadir_f, "installed-tests");
      
      if (!g_file_query_exists (prefix_root, NULL))
        continue;

      if (!gather_all_tests_recurse (prefix_root, prefix_root, "", app->tests,
                                     cancellable, error))
        goto out;
    }

  g_ptr_array_sort (app->tests, cmp_tests);

  if (argc > 1)
    {
      j = 0;
      while (j < app->tests->len)
        {
          gboolean matches = FALSE;
          Test *test = app->tests->pdata[j];
          for (i = 1; i < argc; i++)
            {
              const char *prefix = argv[i];
              if (g_str_has_prefix (test->name, prefix))
                {
                  matches = TRUE;
                  break;
                }
            }
          if (!matches)
            g_ptr_array_remove_index_fast (app->tests, j);
          else
            j++;
        }
    }

  total_tests = app->tests->len;

  if (opt_list)
    {
      for (i = 0; i < app->tests->len; i++)
        {
          Test *test = app->tests->pdata[i];
          g_print ("%s (%s)\n", test->name, gs_file_get_path_cached (test->prefix_root));
        }
    }
  else
    {
      reschedule_tests (app->cancellable);

      while (app->pending_tests && !app->test_error)
        g_main_context_iteration (NULL, TRUE);

      if (app->test_error)
        g_propagate_error (error, app->test_error);
    }

  ret = TRUE;
 out:
  if (!ret)
    {
      g_assert (local_error);
      /* Reusing ONE_TEST_FAILED_MSGID is not quite right, but whatever */
      gs_log_structured_print_id_v (ONE_TEST_FAILED_MSGID,
                                    "Caught exception during testing: %s", local_error->message); 
      g_clear_error (&local_error);
    }
  if (!opt_list)
    {
      n_passed = n_skipped = n_failed = 0;
      for (i = 0; i < app->tests->len; i++)
        {
          Test *test = app->tests->pdata[i];
          switch (test->state)
            {
            case TEST_STATE_COMPLETE_SUCCESS:
              n_passed++;
              break;
            case TEST_STATE_COMPLETE_SKIPPED:
              n_skipped++;
              break;
            case TEST_STATE_COMPLETE_FAILED:
              n_failed++;
              break;
            default:
              break;
            }
        }
      gs_log_structured_print_id_v (TESTS_COMPLETE_MSGID,
                                    "SUMMARY%s: total: %u passed: %d skipped: %d failed: %d",
                                    ret ? "" : " (incomplete)",
                                    total_tests, n_passed, n_skipped, n_failed);
    }
  g_clear_pointer (&app->tests, g_ptr_array_unref);
  if (!ret)
    return 1;
  return 0;
}
