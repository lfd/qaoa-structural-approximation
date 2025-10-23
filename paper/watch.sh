#!/bin/bash

while ! inotifywait -e modify $@ ; do 
    make
done
