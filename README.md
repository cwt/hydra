# Ananta (formerly Hydra)

Ananta is a *powerful* command-line tool designed to simplify simultaneous SSH command execution across multiple remote hosts. It enhances workflows, automates repetitive tasks, and improves efficiency for system administrators and developers managing distributed systems.

## Namesake

Ananta draws inspiration from Ananta Shesha or Ananta Nagaraja (อนันตนาคราช), the many-headed serpentine demigod from Hindu mythology deeply rooted in Thai culture.

Initially, this project was named Hydra, referencing the many-headed serpent in Greek mythology. However, due to the abundance of projects named Hydra or hydra-* on PyPI (e.g., the previous project at [https://pypi.org/project/hydra-ssh/](https://pypi.org/project/hydra-ssh/)), it was renamed to Ananta. The commands you now use are `ananta`, which is shorter, more distinctive, and easier to remember than `hydra-ssh`.

## Features

- Concurrent execution of commands across multiple remote hosts
- Flexible CSV-based host list configuration
- SSH authentication with public key support
- Lightweight and user-friendly command-line interface
- Color-coded output for easy host differentiation
- Option to separate host outputs for clarity
- Support for cursor control codes for specific layouts (e.g., `fastfetch`, `neofetch`)

## Installation

### System Requirements

- Python 3.10 or higher
- `pip` package manager
- Required dependencies: `asyncssh`, `argparse`, `asyncio`
- Optional: `uvloop` (Unix-based systems) or `winloop` (Windows) for enhanced performance

### Installing via pip

Install Ananta using pip:

```bash
pip install ananta --user
```

Install Ananta using pip with `uvloop` or `winloop` for *speed* enhancement:
```bash
pip install ananta[speed] --user
```

**Note:** Ensure Python 3.10 or higher is installed on your system.  
If you previously used `hydra-ssh`, update your command to `pip install ananta` to access the latest version.

## Usage

### Hosts File Format

Create a hosts file in CSV format with the following structure:

```csv
#alias,ip,port,username,key_path,tags(optional - colon separated)
host-1,10.0.0.1,22,user,/home/user/.ssh/id_ed25519
host-2,10.0.0.2,22,user,#,web
host-3,10.0.0.3,22,user,#,arch:web
host-4,10.0.0.4,22,user,#,ubuntu:db
```

- Lines beginning with `#` are ignored.
- **`key_path` details:**
  - Provide the path to an SSH private key.
  - Use `#` to indicate the default key specified via the `-K` option.
  - If `#` is used without `-K`, Ananta will attempt to use commonly available SSH keys from `~/.ssh/`.

### Running Commands

Run commands on remote hosts with:

```bash
ananta <options> [hosts file] [command]
```

**Example:**

```console
$ ananta hosts.csv uptime
$ ananta -S sensors
$ ananta -CS hosts.csv fastfetch
$ ananta -t web,db hosts.csv uptime
$ ananta -t arch hosts.csv sudo pacman -Syu --noconfirm
```

### Options

**Single letter option is case-insensitive.**

- `-N, --no-color`: Disable colorized output
- `-S, --separate-output`: Display output from each host separately
- `-T, --host-tags`: Host's tag(s) (comma separated)
- `-W, --terminal-width`: Manually set terminal width
- `-E, --allow-empty-line`: Permit printing of empty lines
- `-C, --allow-cursor-control`: Enable cursor control codes (e.g., for `fastfetch` or `neofetch`)
- `-V, --version`: Display the Ananta version
- `-K, --default-key`: Specify the default SSH private key path

### Demo

[![asciicast](https://asciinema.org/a/711115.svg)](https://asciinema.org/a/711115)

[![asciicast](https://asciinema.org/a/711116.svg)](https://asciinema.org/a/711116)

## License

```text
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

