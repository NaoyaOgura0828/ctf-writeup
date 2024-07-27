#!/bin/bash

raw_output=$(objdump -d ../simpleoverwrite/chall | grep win)

raw_address=$(echo ${raw_output} | grep -oP '^[0-9]+')

formatted_address=$(echo ${raw_address} | sed 's/^0*//' | sed 's/^/0x/')

echo ${formatted_address}

exit 0
