#!/usr/bin/env bash
set -e

if [ "$EUID" -ne 0 ]; then
    echo "This script uses functionality which requires root privileges"
    exit 1
fi

# Start the build with an empty ACI
acbuild --debug begin ./library-python-3.4-alpine.aci

# In the event of the script exiting, end the build
acbuildEnd() {
    export EXIT=$?
    acbuild --debug end && exit $EXIT 
}
trap acbuildEnd EXIT

# Name the ACI
acbuild --debug set-name wasv.me/intercom

# Copy requirements.txt
acbuild --debug copy requirements.txt /app/requirements.txt
acbuild --debug copy server/server.py /app/server.py

# Run pip install
acbuild --debug run -- pip install -r /app/requirements.txt

# Add a port for http traffic over port 80
acbuild --debug port add telnet tcp 42420
acbuild --debug port add output tcp 42124

# Set environment variable
acbuild --debug environment add PYTHONUNBUFFERED 1

# Run nginx in the foreground
acbuild --debug set-exec -- /usr/local/bin/python /app/server.py

# Save the ACI
acbuild --debug write --overwrite intercom-latest-linux-amd64.aci
