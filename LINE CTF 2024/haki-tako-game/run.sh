#!/bin/bash

cd $(dirname $0)

# Install pycryptodome
if ! python3.12 -c "import pkg_resources; pkg_resources.require('pycryptodome')" 2>/dev/null; then
    echo 'Installing pycryptodome...'
    python3.12 -m pip install pycryptodome
else
    echo 'pycryptodome is already installed.'
fi

# Run challenge_server.py
python3.12 challenge_server.py &
server_pid=$!

sleep 5

# Run solve.py
python3.12 solve.py >debug.log

# Kill challenge_server.py
kill $server_pid

exit 0
