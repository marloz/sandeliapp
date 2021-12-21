from tests.dir import TEST_DATA_PATH

from src.io import loader
from src.entities import Entity

from pandas.core.frame import DataFrame
from pandas.testing import assert_frame_equal

from pydantic.dataclasses import dataclass
import os
import pytest

DATA_PATH = os.path.join(*[TEST_DATA_PATH, 'io', 'loader'])


def test_fill_table_info_from_alias():
    actual = loader.fill_table_info_from_alias(alias='my_data',
                                               data_path=DATA_PATH)
    expected = {'alias': 'my_data',
                'path': os.path.join(DATA_PATH, 'my_data.csv'),
                'id_column': 'my_data_id',
                'entity_name_column': 'my_data_name',
                'sort_column': 'timestamp'}
    assert actual == expected


@dataclass
class My_Data(Entity):
    my_data_id: str
    my_data_name: str


class TestLoader:

    @pytest.fixture(scope='class')
    def loader(self):
        entities_to_load = ['my_data', 'your_data']
        return loader.preload_data(entities_to_load, data_path=DATA_PATH)

    def test_preload_data(self, loader):
        expected = DataFrame([
            ('id1', 'foo', '2021-12-03 12:34:29.085482'),
            ('id2', 'buzz', '2021-12-05 12:34:29.085482')
        ], columns=['my_data_id', 'my_data_name', 'timestamp'])
        assert isinstance(loader.data['your_data'], DataFrame)
        assert_frame_equal(loader.data['my_data'].reset_index(drop=True),
                           expected)

    @pytest.mark.parametrize(
        'entity_identifier, indentifier_type, expected',
        [
            ('id1', 'id', {'my_data_id': 'id1',
                           'my_data_name': 'foo'}),
            ('buzz', 'name', {'my_data_id': 'id2',
                              'my_data_name': 'buzz'})
        ]
    )
    def test_get_single_entity_instance(
            self, loader, entity_identifier, indentifier_type, expected
    ):
        actual = loader.get_single_entity_instance(
            My_Data, entity_identifier, indentifier_type)
        assert actual == My_Data(**expected)
