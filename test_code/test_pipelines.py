import pandas as pd
import numpy as np
import pytest
import os
import sys
import json

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_PATH = os.path.join(PROJECT_ROOT, "src")
sys.path.extend([SRC_PATH, PROJECT_ROOT])

from data_processing_pipeline import processData
from inverse_data_processing_pipeline import inverseProcessData
configs = json.load(open(os.path.join(PROJECT_ROOT, "config.json")))

@pytest.fixture(scope="session")
def test_process_pipelines():
    df = pd.read_csv(os.path.join(PROJECT_ROOT, "test_row_data.xlsx"))
    processed_data = processData(df)
    assert processed_data.shape[0] == df.shape[0]
    assert processed_data.columns[1]  == df.shape[1]
