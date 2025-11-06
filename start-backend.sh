#!/bin/bash
cd "/Users/macbook2024/Library/CloudStorage/Dropbox/AAA Backup/A Working/Arjun Final Fine Tuning"
.venv/bin/python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
