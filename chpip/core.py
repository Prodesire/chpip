import os
import sys

import click
import configparser

from yaml import safe_load, safe_dump

PY2 = sys.version_info[0] == 2


class ChpipManager(object):

    def __init__(self):
        self._pip_dirname = os.path.expanduser('~/.pip')
        self._pip_path = os.path.join(self._pip_dirname, 'pip.conf')
        self._chpip_path = os.path.join(self._pip_dirname, '.chpip.yml')

    def _ensure_pip_dirname(self):
        if not os.path.exists(self._pip_dirname):
            os.makedirs(self._pip_dirname)

    def change_index(self, name=None):
        self._ensure_pip_dirname()
        if os.path.exists(self._chpip_path):
            with open(self._chpip_path, 'r') as f:
                chpip_data = safe_load(f.read()) or {}

        indexes = chpip_data.get('indexes')
        if not indexes:
            click.echo('There is no available index to change. Please use `chpip set-index` to set one.')
            return 1

        if name:
            if name not in indexes:
                click.echo('There is no index with name {}. Please use `chpip set-index` to set one.'.format(name))
                return 1
            next_index_url = indexes[name]['index_url']
        else:
            name = chpip_data.get('last_index_name')
            if not name:
                name = next(indexes.iterkeys() if PY2 else indexes.keys())
            next_index_url = indexes[name]['index_url']

        current_index_name = chpip_data.get('current_index_name')
        if not current_index_name:
            current_index_name = '.default'
            current_index_url = 'https://pypi.org/simple'
        else:
            current_index_url = indexes[current_index_name]['index_url']

        config = configparser.ConfigParser()
        config.read(self._pip_path)
        if not config.has_section('global'):
            config.add_section('global')
        config.set('global', 'index-url', next_index_url)
        with open(self._pip_path, 'w') as f:
            config.write(f)

        with open(self._chpip_path, 'w') as f:
            chpip_data['last_index_name'] = current_index_name
            chpip_data['current_index_name'] = name
            indexes = chpip_data['indexes']
            if current_index_name not in indexes:
                indexes[current_index_name] = {'index_url': current_index_url}
            f.write(safe_dump(chpip_data))

        last = 'last({})'.format(current_index_name.lstrip('.'))
        click.echo('Change Python package index to `{}` successful.'.format(name or last))
        return 0

    def set_index(self, name, index_url):
        if name.startswith('.'):
            click.echo('Index name `{}` cannot start with `.`.'.format(name))
            return 1

        if not index_url.startswith(('http://', 'https://')):
            click.echo('Invalid base URL `{}` for Python package index.'.format(index_url))
            return 1

        self._ensure_pip_dirname()
        with open(self._chpip_path, 'r') as f:
            chpip_data = safe_load(f.read()) or {}
            indexes = chpip_data.setdefault('indexes', {})
            indexes[name] = {'index_url': index_url}
        with open(self._chpip_path, 'w') as f:
            f.write(safe_dump(chpip_data))
            click.echo('Set Python package index with name `{}` successful.'.format(name))
        return 0
