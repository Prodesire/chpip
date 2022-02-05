import sys
from chpip import __version__
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

PY2 = sys.version_info[0] == 2


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', 'Arguments to pass into py.test')]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        try:
            from multiprocessing import cpu_count
            self.pytest_args = ['-n', str(cpu_count())]
        except (ImportError, NotImplementedError):
            self.pytest_args = ['-n', '1']

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest

        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


test_requirements = []
for line in open('requirements-dev.txt'):
    requirement = line.strip()
    if requirement:
        test_requirements.append(requirement)

open_kwargs = {} if PY2 else {'encoding': 'utf-8'}
setup(
    name='chpip',
    version=__version__,
    description='A tool to manage the base URL of the Python package index.',
    long_description=open('README.md', **open_kwargs).read(),
    long_description_content_type='text/markdown',
    author='Prodesire',
    author_email='wangbinxin001@126.com',

    se='MIT License',
    url='https://github.com/Prodesire/chpip',
    cmdclass={'test': PyTest},
    tests_require=test_requirements,
    install_requires=[
        'click>=0.7.0',
        'pyyaml>=5.0.0,<7.0.0',
    ],
    packages=find_packages(),
    entry_points={
        'console_scripts': ['chpip=chpip.__main__:cli']
    },
    classifiers=[
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Software Development :: Libraries'
    ],
)
