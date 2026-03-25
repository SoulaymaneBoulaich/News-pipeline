@echo off
set PYTHONPATH=C:\Users\pc\Desktop\news-pipeline
set Your_API_KEY

echo Running pipeline...
python pipeline/flow.py

echo Starting API...
python -m uvicorn api.main:app --reload
