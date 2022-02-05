import pytest

from chpip import exception
from chpip.core import DEFAULT_INDEX_NAME, DEFAULT_INDEX_URL


class TestChangeIndex(object):
    def test_set_invalid_index_name(self, chpip_manager):
        with pytest.raises(exception.InvalidIndexName):
            chpip_manager.set_index(DEFAULT_INDEX_NAME, DEFAULT_INDEX_URL)

    def test_set_invalid_index_url(self, chpip_manager):
        with pytest.raises(exception.InvalidIndexURL):
            chpip_manager.set_index('test', 'invalid')

    def test_set_index(self, chpip_manager):
        name1 = 't1'
        index_url1 = 'https://test1.com'
        chpip_manager.set_index(name1, index_url1)
        chpip_data = chpip_manager.get_chpip_data()
        assert chpip_data == {
            'indexes': {
                name1: {
                    'index_url': index_url1
                }
            }
        }

        name2 = 't2'
        index_url2 = 'https://test2.com'
        chpip_manager.set_index(name2, index_url2)
        chpip_data = chpip_manager.get_chpip_data()
        assert chpip_data == {
            'indexes': {
                name1: {
                    'index_url': index_url1
                },
                name2: {
                    'index_url': index_url2
                }
            }
        }

        index_url2_new = 'https://test2-new.com'
        chpip_manager.set_index(name2, index_url2_new)
        chpip_data = chpip_manager.get_chpip_data()
        assert chpip_data == {
            'indexes': {
                name1: {
                    'index_url': index_url1
                },
                name2: {
                    'index_url': index_url2_new
                }
            }
        }
