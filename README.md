# Ananta (formerly Hydra)

Ananta is a *powerful* command-line tool that unleashes simultaneous SSH command execution across multiple remote hosts. It streamlines workflows, automates repetitive tasks, and enhances efficiency for system administrators and developers managing distributed systems.

## Namesake

Ananta, inspired by Ananta Shesha or Ananta Nagaraja (อนันตนาคราช), is a many-headed serpentine demigod from Hindu mythology that has taken deep root in Thai culture.

This project used to be named Hydra, the many-headed serpent in Greek mythology. However, due to numerous Hydra and hydra-* projects on PyPI (see the old project at https://pypi.org/project/hydra-ssh/), I renamed it to Ananta-shorter and more unique!

## Features

- Execute commands across multiple remote hosts concurrently
- Supports flexible CSV-based host list configuration
- SSH authentication with public key support
- Lightweight and intuitive command-line interface
- Color-coded output for easy host differentiation
- Option to separate host outputs without interleaving
- Handles cursor control codes for commands requiring specific layouts (e.g., `fastfetch`, `neofetch`)

## Installation

### System Requirements

- Python 3.10 or higher
- `pip` package manager
- Required dependencies: `asyncssh`, `argparse`, `asyncio`
- Optional: `uvloop` (Unix-like systems) or `winloop` (Windows) for enhanced performance

### Installing via pip

Install Ananta directly using pip:

```
$ pip install ananta --user
```

**Note:** Ensure Python 3.10 or higher is installed on your system.

**Note:** If you previously used `hydra-ssh`, switch to `pip install ananta` for the latest updates!

## Usage

### Hosts File Format

Create a hosts file in CSV format with the following structure:

```csv
#alias,ip,port,username,key_path
host-1,10.0.0.1,22,user,/home/user/.ssh/id_ed25519
host-2,10.0.0.2,22,user,#
```

- Lines starting with `#` are ignored.
- `key_path`:
  - Specify the path to an SSH private key.
  - Use `#` to use the default key provided via the `-K` option.
  - If `#` is used without `-K`, Ananta attempts to use common SSH keys from `~/.ssh/`.

### Running Commands

Execute a command on remote hosts with:

```
$ ananta [hosts file] [command]
```

Example:

```
$ ananta hosts.csv "uptime"
```

### Options

- `-N, --no-color`: Disable colorized output
- `-S, --separate-output`: Display output from each host separately
- `-W, --terminal-width`: Manually set terminal width
- `-E, --allow-empty-line`: Permit printing of empty lines
- `-C, --allow-cursor-control`: Enable cursor control codes (e.g., for `fastfetch` or `neofetch`)
- `-V, --version`: Display Ananta version
- `-K, --default-key`: Specify path to default SSH private key

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

