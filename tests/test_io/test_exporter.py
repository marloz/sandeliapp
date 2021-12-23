from datetime import datetime
from tests.dir import TEST_DATA_PATH
from tests.test_io.test_loader import My_Data

from src.io.exporter import Exporter

import pandas as pd
from pandas.testing import assert_frame_equal
import csv

import os

DATA_PATH = os.path.join(*[TEST_DATA_PATH, 'io', 'exporter'])


def test_exporter(tmpdir):
    entity = My_Data(my_data_id='id999', my_data_name='fuzz buzz')
    exporter = Exporter(entity)
    exporter._timestamp = datetime(2020, 1, 1)

    output_path = tmpdir.mkdir("tmpdir").join("output.csv")
    # Add columns, since exporter skips header, since data is appended
    columns = ['my_data_id', 'my_data_name', 'timestamp']
    with open(output_path, 'w') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(columns)

    exporter.export(output_path)
    actual = pd.read_csv(output_path)
    expected = pd.read_csv(os.path.join(DATA_PATH, 'expected.csv'))
    assert_frame_equal(actual, expected)
