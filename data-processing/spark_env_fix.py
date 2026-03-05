import os
import sys

VENV_PY = r"C:\BDA\movie-recommendation-system\data-processing\venv\Scripts\python.exe"

os.environ["PYSPARK_PYTHON"] = VENV_PY
os.environ["PYSPARK_DRIVER_PYTHON"] = VENV_PY
os.environ["PYSPARK_WORKER_PYTHON"] = VENV_PY

print("Environment forced to use:", os.environ["PYSPARK_PYTHON"])