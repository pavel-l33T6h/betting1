#!/bin/bash

exec uvicorn main:app --host 0.0.0.0 --port 8200 --log-level debug --workers 4 --access-log --log-config config.ini