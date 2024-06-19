#!/usr/bin/env sh

echo "INFO : Syncing .python-version with the container"
printf '%s\n' $PYTHON_VERSION > .python-version

echo "INFO : Starting a daemon to keep the container running"
tail -f /dev/null
