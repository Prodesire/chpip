# chpip

[![PyPI version](https://badge.fury.io/py/chpip.svg)](https://badge.fury.io/py/chpip)
[![PyPI Supported Python Versions](https://img.shields.io/pypi/pyversions/chpip.svg)](https://pypi.python.org/pypi/chpip/)
[![Run Tests](https://github.com/Prodesire/chpip/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/Prodesire/chpip/actions/workflows/tests.yml)

A tool to manage the base URL of the Python package index.

## Installation

```bash
$ pip install chpip
```

## Usage

### Set pip index URL

Set the base URL of the Python package index with name.

```bash
$ chpip set -n ustc -i https://mirrors.ustc.edu.cn/pypi/web/simple
```

For more information about the options, please refer to the `chpip set` command.

```bash
$ chpip set --help
Usage: chpip set [OPTIONS]

Options:
  -n, --name TEXT       Name of the Python package index.  [required]
  -i, --index-url TEXT  Base URL of the Python Package Index. This should
                        point to a repository compliant with PEP 503 (the
                        simple repository API) or a local directory laid out
                        in the same format.  [required]
  --help                Show this message and exit.
```

### Change pip index URL

Change the base URL of the Python package index without name which means switching between the two indexes in turn.

```bash
$ chpip
Change Python package index to `ustc` successful.
$ chpip
Change Python package index to `default` successful.
```

Change the base URL of the Python package index with name.

```bash
$ chpip -n ustc
Change Python package index to `ustc` successful.
```

### Show pip index URLs

Show all base URLs of the Python package index. Current index is marked with `*`.

```bash
$ chpip show
  default (https://pypi.org/simple)
* ustc (https://mirrors.ustc.edu.cn/pypi/web/simple)
```

### List commonly used pip index URLs

List the commonly used URLs of the Python package index, which can be set by executing the `chpip set` command.

```bash
$ chpip list
  aliyun (https://mirrors.aliyun.com/pypi/simple)
  douban (https://pypi.doubanio.com/simple)
  netease (https://mirrors.163.com/pypi/simple)
  pypi (https://pypi.org/simple)
  tencent (https://mirrors.cloud.tencent.com/pypi/simple)
  tsinghua (https://pypi.tuna.tsinghua.edu.cn/simple)
  ustc (http://pypi.mirrors.ustc.edu.cn/simple)
```