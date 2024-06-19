#!/bin/bash

###########################################################
# Usage:
#   1. Set the value of the cookie vapor_session to the constant VAPOR_SESSION.
#   2. Exec `./run.sh`
#   3. Monitor `exec.log` generated in the current directory and wait until the string `LINECTF` is output.
#   4. Enter `ctrl+c` to stop the script.
#
###########################################################

cd $(dirname $0)

# Set the value of the cookie vapor_session.
VAPOR_SESSION="tMj1H1pzcCC+YRkT4Rz6NFcfypk1jZ2ktmTgsvJW5BM="

sed -i -E "s/(vapor_session\": \")[^\"]+/\1${VAPOR_SESSION}/" solve.py

delete_tmp_files() {
    echo "Stopped loop"
    rm symlink.txt
    rm tmp.zip
    exit 0
}

trap delete_tmp_files SIGINT

rm exec.log

while true; do
    python solve.py >>exec.log 2>&1
done
