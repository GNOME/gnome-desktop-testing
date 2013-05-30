/* -*- mode: C; c-file-style: "gnu"; indent-tabs-mode: nil; -*-
 *
 * Copyright (C) 2013 Colin Walters <walters@verbum.org>
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

#include <gio.h>
#include <json-glib.h>
#include "libgsystem.h"

static gboolean
export_one_coredump (GDataOutputStream  *dataout,
                     const char         *coredump_pid_str,
                     GError            **error)
{
  gboolean ret = FALSE;
  gs_unref_object GSSubproessContext *proc_context = NULL;
  gs_unref_object GSSubproess *proc = NULL;
  char *coredumpctl_argv = { "systemd-coredumpctl", "dump", NULL /* pid */, NULL };
  gs_unref_object GInputStream *dump_stdin = NULL;
  GBytes *bytes = NULL;

  coredumpctl_argv[2] = coredump_pid_str;
  proc_context = gs_subprocess_context_new (coredumpctl_argv);
  gs_subprocess_context_set_stdout_disposition (proc_context, GS_SUBPROCESS_STREAM_DISPOSITION_PIPE);

  proc = gs_subprocess_new (proc_context, NULL, error);
  if (!proc)
    goto out;

  dump_stdin = gs_subprocess_get_stdout (proc);
  while ((bytes = g_data_input_stream_read_bytes (dump_stdin, 4096,
                                                  cancellable, error)) != NULL)
    {
      GVariant *
      g_clear_pointer (&bytes, g_bytes_unref);
    }

  ret = TRUE;
 out:
  g_clear_pointer (&bytes, g_bytes_unref);
  return ret;
}

int
main (int argc, char **argv)
{
  GError *local_error = NULL;
  GError **error = &local_error;
  gs_unref_object GCancellable *cancellable = NULL;
  char* journal_argv[] = { "journalctl", "-o", "json", "-b", "--no-tail",
			   "_MESSAGE_ID=fc2e22bc6ee647b6b90729ab34a250b1", NULL };
  gs_unref_object GInputStream *journal_in = NULL;
  gs_unref_object GFile *virtio_file = NULL;
  gs_unref_object GUnixOutputStream *virtio = NULL;
  gs_unref_object GDataOutputStream *dataout = NULL;
  gs_unref_object GDataInputStream *datain = NULL;
  const char *virtio_path = "/dev/virtio-ports/org.gnome.ostree.coredump";

  virtio_file = g_file_new_for_path (virtio_path);
  if (!g_file_query_exists (virtio_file, NULL))
    {
      g_set_error (error, G_IO_ERROR, G_IO_ERROR_FAILED,
                   "Unable to find virtio channel %s", virtio_path);
      goto out;
    }
  virtio = g_file_append_to (virtio_file, 0, cancellable, error);
  dataout = g_data_output_stream_new (virtio);

  if (!g_spawn_async_with_pipes (NULL, journal_argv, NULL,
				 G_SPAWN_SEARCH_PATH | G_SPAWN_DO_NOT_REAP_CHILD,
				 NULL, NULL,
				 &pid, NULL,
				 &stdout_fd, NULL, error))
    goto out;

  journal_in = g_unix_input_stream_new (stdout_fd, TRUE);
  datain = g_data_input_stream_new (journal_in);
  
  while (TRUE)
    {
      gsize len;
      GError *tmp_error = NULL;
      gs_free char *line = g_data_input_stream_read_line_utf8 (datain, &len, NULL, &tmp_error);
      gs_unref_object JsonParser *parser = NULL;
      JsonNode *root;
      JsonObject *rootobj;
      const char *coredump_pid_str;
      guint64 coredump_pid;

      if (tmp_error != NULL)
	{
	  g_propagate_error (error, tmp_error);
	  goto out;
	}

      parser = json_parser_new ();
      if (!json_parser_load_from_data (parser, line, len, error))
        goto out;
      
      root = json_parser_get_root (parser);
      if (json_node_get_node_type (root) != JSON_NODE_OBJECT)
        continue;
      rootobj = json_node_get_object (root);
      
      coredump_pid_str = json_object_get_string_member (rootobj, "COREDUMP_PID");
      if (coredump_pid_str == NULL)
        continue;
      
      coredump_pid = g_ascii_strtoull (coredump_pid_str, NULL, 10);
      if (!export_one_coredump (dataout, coredump_pid))
        goto out;
    }

 out:
  if (local_error)
    {
      g_printerr ("%s\n", local_error->message);
      g_clear_error (&local_error);
      return 1;
    }
  return 0;
}
