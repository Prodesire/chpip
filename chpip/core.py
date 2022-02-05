import os
import sys
import configparser

from chpip import exception
from chpip.utils import ordered_load, ordered_dump

PY2 = sys.version_info[0] == 2
WIN = sys.platform == 'win32'
DEFAULT_INDEX_NAME = 'default'
DEFAULT_INDEX_URL = 'https://pypi.org/simple'


class ChpipManager(object):

    def __init__(self, pip_dirname=None):
        if WIN:
            appdata_path = os.getenv('APPDATA')
            self.pip_dirname = os.path.join(appdata_path, 'pip') if not pip_dirname else pip_dirname
            self.pip_path = os.path.join(self.pip_dirname, 'pip.ini')
        else:
            self.pip_dirname = os.path.expanduser('~/.config/pip') if not pip_dirname else pip_dirname
            self.pip_path = os.path.join(self.pip_dirname, 'pip.conf')
        self.chpip_path = os.path.join(self.pip_dirname, '.chpip.yml')

    def _ensure_pip_dirname(self):
        if not os.path.exists(self.pip_dirname):
            os.makedirs(self.pip_dirname)

    def change_index(self, name=None):
        chpip_data = self.get_chpip_data()
        indexes = chpip_data.get('indexes')
        if not indexes:
            raise exception.NoAvailableIndex()

        if name:
            if name not in indexes:
                raise exception.IndexNameNotFound(name=name)
            next_index_url = indexes[name]['index_url']
        else:
            name = chpip_data.get('last_index_name')
            if not name:
                name = next(indexes.iterkeys() if PY2 else iter(indexes.keys()))
            next_index_url = indexes[name]['index_url']

        current_index_name = chpip_data.get('current_index_name')
        if not current_index_name:
            current_index_name = DEFAULT_INDEX_NAME
            current_index_url = DEFAULT_INDEX_URL
        else:
            current_index_url = indexes[current_index_name]['index_url']

        self._ensure_pip_dirname()
        config = self.get_pip_config()
        if not config.has_section('global'):
            config.add_section('global')
        config.set('global', 'index-url', next_index_url)
        with open(self.pip_path, 'w') as f:
            config.write(f)

        with open(self.chpip_path, 'w') as f:
            chpip_data['last_index_name'] = current_index_name
            chpip_data['current_index_name'] = name
            indexes = chpip_data['indexes']
            if current_index_name not in indexes:
                indexes[current_index_name] = {'index_url': current_index_url}
            f.write(ordered_dump(chpip_data))
        return name

    def set_index(self, name, index_url):
        if name == DEFAULT_INDEX_NAME:
            raise exception.InvalidIndexName(name=name)

        if not index_url.startswith(('http://', 'https://')):
            raise exception.InvalidIndexURL(url=index_url)

        chpip_data = self.get_chpip_data()
        self._ensure_pip_dirname()
        with open(self.chpip_path, 'w') as f:
            indexes = chpip_data.setdefault('indexes', {})
            indexes[name] = {'index_url': index_url}
            f.write(ordered_dump(chpip_data))
        return name

    def get_pip_config(self):
        config = configparser.ConfigParser()
        config.read(self.pip_path)
        return config

    def get_chpip_data(self):
        if os.path.exists(self.chpip_path):
            with open(self.chpip_path, 'r') as f:
                chpip_data = ordered_load(f.read()) or {}
        else:
            chpip_data = {}
        return chpip_data

    def show(self):
        chpip_data = self.get_chpip_data()
        if not chpip_data:
            return ''

        current_index_name = chpip_data.get('current_index_name')
        indexes = chpip_data.get('indexes') or {}
        lines = []
        for name in indexes:
            index_data = indexes[name]
            index_url = index_data.get('index_url')
            if name == current_index_name:
                line = '* {} ({})'.format(name, index_url)
            else:
                line = '  {} ({})'.format(name, index_url)
            lines.append(line)
        return '\n'.join(lines)
