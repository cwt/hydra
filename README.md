# Hydra

Hydra is a command-line tool that allows users to execute commands on multiple remote hosts at once via SSH. With Hydra, you can streamline your workflow, automate repetitive tasks, and save time and effort.

## Features

- Execute commands on multiple remote hosts simultaneously
- Flexible and configurable host list format (CSV)
- Supports SSH and public key authentication
- Clean, lightweight, and easy-to-use command-line interface
- Color-coded output for easy host identification
- Option to separate output for each host without interleaving
- Support for cursor control codes for commands requiring special layout (e.g., `fastfetch`, `neofetch`)

## Installation

### System Requirements

- Python 3.10 or higher
- pip package manager
- Required dependencies: `asyncssh`, `argparse`, `asyncio`
- Optional: `uvloop` for improved performance on Unix-like systems

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
$ curl https://hg.sr.ht/~cwt/hydra/archive/tip.tar.gz | tar zxf -
$ cd hydra-tip
$ pip install -r requirements.txt --user
```

**Note:** Ensure you have Python 3.10 or higher installed.

## Usage

### Hosts File Format

Create a hosts file in CSV format with the following structure:

```csv
#alias,ip,port,username,key_path
host-1,10.0.0.1,22,user,/home/user/.ssh/id_25519
host-2,10.0.0.2,22,user,#
```

- Lines starting with `#` are ignored.
- In the `key_path` field:
  - Specify the path to the SSH private key file.
  - Use `#` to indicate that the default key specified via the `-K` option should be used.
  - If no key is specified and `#` is used without `-K`, Hydra will attempt to use common SSH keys in `~/.ssh/`.

### Running Commands

To execute a command on the remote hosts, use:

```
$ ./hydra.py [hosts file] [command]
```

For example:

```
$ ./hydra.py hosts.csv "ls -l"
```

### Options

- `-N, --no-color`: Disable host coloring.
- `-S, --separate-output`: Print output from each host without interleaving.
- `-W, --terminal-width`: Set terminal width manually.
- `-E, --allow-empty-line`: Allow printing empty lines.
- `-C, --allow-cursor-control`: Allow cursor control codes for commands like `fastfetch` or `neofetch`.
- `-V, --version`: Show the version of Hydra.
- `-K, --default-key`: Path to default SSH private key.

## License

```
The MIT License (MIT)

Copyright (c) 2023-2025 cwt(at)bashell(dot)com

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

