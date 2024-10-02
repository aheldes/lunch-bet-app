#!/bin/bash
if [ ! -f "venv/Scripts/activate" ]; then
  echo "Error: Virtual environment activation script not found."
  exit 1
fi

source venv/Scripts/activate

if [ ! -d "./be" ]; then
  echo "Error: Directory '.be' does not exist."
  exit 1
fi

cd ./be

uvicorn main:app --host 127.0.0.1 --port 8000 --reload
