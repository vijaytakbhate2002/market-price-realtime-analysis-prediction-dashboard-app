import pandas as pd
import numpy as np
import pytest
import os
import sys
import json

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_PATH = os.path.join(PROJECT_ROOT, "src")
sys.path.extend([SRC_PATH, PROJECT_ROOT])

print(PROJECT_ROOT)

from data_processing_pipeline import processData
from inverse_data_processing_pipeline import inverseProcessData
configs = json.load(open(os.path.join(PROJECT_ROOT, "config.json")))


def test_process_pipelines():
    df = pd.read_csv(os.path.join(PROJECT_ROOT, "test_code/test_row_data.csv"))
    processed_data = processData(df)
    processed_data.to_csv(os.path.join(PROJECT_ROOT, "test_code/test_processed_data.csv"), index=False)
    assert processed_data.shape[0] == df.shape[0]
    assert processed_data.shape[1]  == df.shape[1]


def test_inverse_process_pipelines():
    df = pd.read_csv(os.path.join(PROJECT_ROOT, "test_code/test_processed_data.csv"))
    original_data = inverseProcessData(df)
    assert original_data.shape[0] == df.shape[0]
    assert original_data.shape[1]  == df.shape[1]

test_process_pipelines()
test_inverse_process_pipelines()
