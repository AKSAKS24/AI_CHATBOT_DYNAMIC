#!/bin/bash
echo "Starting SAP Dynamic Backend..."
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload