#!/usr/bin/env bash
open -a Google\ Chrome --args --user-data-dir=test --unsafely-treat-insecure-origin-as-secure=http://localhost:8080
dev_appserver.py .