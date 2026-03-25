@echo off
set PYTHONPATH=C:\Users\pc\Desktop\news-pipeline
set e2febadf954f472b8b38d2e6e3f0fe81

echo Running pipeline...
python pipeline/flow.py

echo Starting API...
python -m uvicorn api.main:app --reload