# WCM - WINGS Component Manager

[![Build Status](https://travis-ci.org/mintproject/wcm.svg?branch=master)](https://travis-ci.org/mintproject/wcm)
[![PyPI version](https://badge.fury.io/py/wcm.svg)](https://pypi.org/project/wcm/)
[![Python 3.5](https://img.shields.io/pypi/pyversions/wcm.svg)](https://www.python.org/downloads/release/python-350/)
[![Downloads](https://img.shields.io/pypi/dm/wcm.svg)](https://pypi.org/project/wcm/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)


## Installation

```bash
pip install wcm
```


## CLI

`wcm` WINGS Component Manager is a cli utility to `publish` WINGS component to a WINGS instance.

```bash
$ wcm --help
Usage: wcm [OPTIONS] COMMAND [ARGS]...

Options:
  -v, --verbose
  --help         Show this message and exit.

Commands:
  configure  Configure credentials
  init       Initialize a directory for a new component.
  publish    Deploy the pacakge to the wcm.
  version    Show wcm version.
```

The `configure` sub command is used to setup credentials used by `wcm` to interact with WINGS server(s).

```bash
$ wcm configure --help
Usage: wcm configure [OPTIONS]

  Configure credentials

Options:
  -p, --profile <profile-name>
  --help              Show this message and exit.
```

The `init` sub command is used to initialze a new WINGS component on the file-system.

```bash
$ wcm init --help
Usage: wcm init [OPTIONS] [COMPONENT]

  Initialize a directory for a new component.

Options:
  -y, --yes
  --help     Show this message and exit.
```

The `publish` sub command publishes a component to a WINGS server.

```bash
$ wcm publish --help
Usage: wcm publish [OPTIONS] [COMPONENT]

  Deploy the pacakge to the wcm.

Options:
  -d, --debug / -nd, --no-debug
  -n, --dry-run
  --help                         Show this message and exit.
```
