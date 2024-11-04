#!/bin/bash

# checking if the 'lines' topic exists
kcat -b kafka:9092 -t lines -e -C -o end &> /dev/null

if [ "$?" -eq "1" ]; then
   echo "Loading sample events into kafka"
   kcat -b kafka:9092 -t lines -P -K: -l lines-1.tsv
fi

exec uvicorn main:app --host 0.0.0.0 --port 8100 --log-level debug --workers 1 --access-log --log-config config.ini