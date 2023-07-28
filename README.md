# Hydra

Hydra is a command-line tool that allows users to execute commands on multiple remote hosts at once via SSH. With Hydra, you can streamline your workflow, automate repetitive tasks, and save time and effort.

## Features

- Execute commands on multiple remote hosts simultaneously
- Flexible and configurable host list format (CSV)
- Supports SSH and public key authentication
- Clean, lightweight, and easy-to-use command-line interface

## Installation

### System Requirements

- Python 3.8 or higher
- pip package manager

### Installing via Mercurial

Clone the project via Mercurial:

```
$ hg clone https://hg.sr.ht/~cwt/hydra
$ cd hydra
$ pip install -r requirements.txt --user
```

### Installing via Download

Alternatively, you can download the latest code:

```
$ curl https://hg.sr.ht/~cwt/hydra/archive/tip.tar.gz |tar zxf -
$ cd hydra-tip
$ pip install -r requirements.txt --user
```

## Usage

Create a hosts file in CSV format:

```csv
#alias,ip,port,username,password
host-1,10.0.0.1,user,pass
host-2,10.0.0.2,user,#
```

notes:

- Any line starts with `#` will be ignored.
- One `#` in the password field means it will connect to the host via public key instead of password.

command:

```
$ ./hydra.py [hosts file] [command]
```

## License

```
The MIT License (MIT)

Copyright (c) 2023 cwt(at)bashell(dot)com

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
