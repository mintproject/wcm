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

`wcm` WINGS Component Manager is a cli utility to `publish` and `download` WINGS component to a WINGS instance.

```bash
$ wcm --help
Usage: wcm [OPTIONS] COMMAND [ARGS]...

Options:
  -v, --verbose
  --help         Show this message and exit.

Commands:
  configure  Configure credentials
  download   Download a component from the wings server.
  init       Initialize a directory for a new component.
  list       Lists all the components in the current wings instance
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

The `download` sub command will download a component from the current wings server.

```bash
$ wcm download --help
Usage: wcm download [OPTIONS] COMPONENT_ID
Download a component from wings server. Data stored in .yaml file and source code downloaded to folder within same directory. file-path can be specified to download into a specific directory

Options:
   -p, --profile <profile-name>
   -f, --file-path TEXT
   --help                        Show this message and exit.
```

The `list` sub command lists all the component's names from the current wings server

```bash
$ wcm list --help
Usage: wcm list [OPTIONS]
Lists all the components in the current wings instance

Options:
-p, --profile <profile-name>
--help                        Show this message and exit.
```

## Example usage

Once wcm is installed, configure your credentials to use a wings server

```bash
C:\Users\Admin>wcm configure
WINGS Server URL: 
WINGS Export URL: http://localhost:8080
WINGS User: myUsername
WINGS Password:
WINGS Domain: wings-domain
Success 

```

Now you can begin using wcm. First list the components on the wings instance you specified on the credentials

```bash
C:\Users\Admin>wcm list
[Economic]
  └─┐
    ├─ economic-v6
    ├─ economictest-v5
    ├─ economicnodata-v6
    ├─ economic-different-data-v6
    └─ economicwcmtest 
                                                                                                                                                                                                                 
[Hydrological]
   └─┐                                                                                                                   
     ├─ HAND-1
     ├─ hand_final-v1
     ├─ hand-v1
     └─ handnodata-v1.0.1 

Done
```

Next, you can download one of these components. Let's choose economic-v6. First you need to navigate into the directory you want to download the component to. Alternatively you could also use the -f <filepath> argument to specify a filepath for the component to be downloaded to

```bash
C:\Users\Admin\Desktop\down>ls

C:\Users\Admin\Desktop\down>wcm download economic-v5
2019-08-13 14:52:02,082 root         INFO     Downloading component
2019-08-13 14:52:02,226 root         INFO     Generated YAML 
2019-08-13 14:52:02,256 root         INFO     Download complete
Download complete  

C:\Users\Admin\Desktop\down>ls
economic-v6       
```

When you download a component it comes in three parts. The wings-component.yaml file which stores the components data. The src folder which stores the sorce code. And the data folder, which at the moment is just a placeholder

After downloading the economic-v5 component, you may edit some of the source code. To upload a new version (6.1 in the example), use the publish command

```bash
C:\Users\Admin\Desktop\down>ls
economic-v6.1

C:\Users\Admin\Desktop\down>wcm publish economic-v6.1
2019-08-13 15:04:08,540 root         INFO     Publishing component
Success                                                                                                                 

```

Now lets check the list command to make sure it was published

```bash
C:\Users\Admin\Desktop\down>wcm list
[Economic]
  └─┐
    ├─ economic-v6
    ├─ economictest-v5
    ├─ economicnodata-v6
    ├─ economic-different-data-v6
    ├─ economicwcmtest
    └─ economic-v6.1

[Hydrological]
  └─┐
    ├─ HAND-1
    ├─ hand_final-v1
    ├─ hand-v1
    └─ handnodata-v1.0.1

Done
```

And now the economic-v6.1 component has been uploaded to WINGS


