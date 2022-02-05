import pytest

from chpip import exception
from chpip.core import DEFAULT_INDEX_NAME, DEFAULT_INDEX_URL


class TestChangeIndex(object):
    TEST_INDEX_NAME = 'test'
    TEST_INDEX_URL = 'https://test.com'

    def test_change_no_available_indexes(self, chpip_manager):
        with pytest.raises(exception.NoAvailableIndex):
            chpip_manager.change_index()

    def test_change_index_not_found(self, chpip_manager):
        chpip_manager.set_index(self.TEST_INDEX_NAME, self.TEST_INDEX_URL)
        with pytest.raises(exception.IndexNameNotFound):
            chpip_manager.change_index('not_found')

    def test_change_index_without_name(self, chpip_manager):
        chpip_manager.set_index(self.TEST_INDEX_NAME, self.TEST_INDEX_URL)
        name = chpip_manager.change_index()
        assert name == self.TEST_INDEX_NAME
        pip_conf = chpip_manager.get_pip_config()
        assert pip_conf['global']['index-url'] == self.TEST_INDEX_URL

        name = chpip_manager.change_index()
        assert name == DEFAULT_INDEX_NAME
        pip_conf = chpip_manager.get_pip_config()
        assert pip_conf['global']['index-url'] == DEFAULT_INDEX_URL

        name = chpip_manager.change_index()
        assert name == self.TEST_INDEX_NAME
        pip_conf = chpip_manager.get_pip_config()
        assert pip_conf['global']['index-url'] == self.TEST_INDEX_URL

    def test_change_index_with_name(self, chpip_manager):
        chpip_manager.set_index(self.TEST_INDEX_NAME, self.TEST_INDEX_URL)
        name = chpip_manager.change_index(self.TEST_INDEX_NAME)
        assert name == self.TEST_INDEX_NAME
        pip_conf = chpip_manager.get_pip_config()
        assert pip_conf['global']['index-url'] == self.TEST_INDEX_URL

        name = chpip_manager.change_index(DEFAULT_INDEX_NAME)
        assert name == DEFAULT_INDEX_NAME
        pip_conf = chpip_manager.get_pip_config()
        assert pip_conf['global']['index-url'] == DEFAULT_INDEX_URL

        name = chpip_manager.change_index(DEFAULT_INDEX_NAME)
        assert name == DEFAULT_INDEX_NAME
        pip_conf = chpip_manager.get_pip_config()
        assert pip_conf['global']['index-url'] == DEFAULT_INDEX_URL
