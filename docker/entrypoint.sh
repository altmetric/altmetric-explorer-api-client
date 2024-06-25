#!/usr/bin/env sh

echo "INFO : Syncing .python-version with the container"
printf '%s\n' $PYTHON_VERSION > .python-version

echo "INFO : Starting jupyter lab at http://localhost:8888"
jupyter lab --allow-root --no-browser --ip 0.0.0.0 --LabApp.token=''
