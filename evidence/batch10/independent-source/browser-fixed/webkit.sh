#!/bin/sh
B=/tmp/castle2d-browsers/webkit-2215/minibrowser-wpe
export WEBKIT_EXEC_PATH="$B/bin" WEBKIT_INJECTED_BUNDLE_PATH="$B/lib" WEBKIT_INSPECTOR_RESOURCES_PATH="$B/share"
export LD_LIBRARY_PATH="/workspace/scratch/e622c1e9421e/memo-webkit-libs/usr/lib/x86_64-linux-gnu:/tmp/castle2d-libs/root/usr/lib/x86_64-linux-gnu:$B/lib:$B/sys/lib"
exec "$B/bin/MiniBrowser" "$@"
