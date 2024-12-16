#!/usr/bin/env python
"""
Hydra: a command-line tool that allows users to execute commands on multiple
remote hosts at once via SSH. With Hydra, you can streamline your workflow,
automate repetitive tasks, and save time and effort.
"""

VERSION = "0.9"

import argparse
import asyncio
import os
import sys
from itertools import cycle
from random import shuffle
from typing import Dict, List, Tuple, Optional

import asyncssh

COLOR = True

# ANSI escape codes for text colors
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
RESET = "\033[0m"

COLORS = [RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN]
shuffle(COLORS)
COLORS_CYCLE = cycle(COLORS)
HOST_COLOR: Dict[str, str] = {}
OUTPUT_QUEUES: Dict[
    str, asyncio.Queue
] = {}  # Dictionary to hold separate output queues for each host

# Large height for long outputs
LINES = 1000

try:
    if sys.platform == "win32":
        import winloop as uvloop
    else:
        import uvloop
except ImportError:
    uvloop = None


async def get_prompt(host_name: str, max_name_length: int) -> str:
    """Generate a formatted prompt for displaying the host's name."""
    if COLOR:
        if HOST_COLOR.get(host_name) is None:
            HOST_COLOR[host_name] = next(COLORS_CYCLE)
        return f"{HOST_COLOR.get(host_name)}[{host_name.rjust(max_name_length)}]{RESET} "
    return f"[{host_name.rjust(max_name_length)}] "


async def establish_ssh_connection(
    ip_address: str,
    ssh_port: int,
    username: str,
    password: Optional[str],
) -> asyncssh.SSHClientConnection:
    """Establish an SSH connection with the given credentials."""
    try:
        conn = await asyncssh.connect(
            host=ip_address,
            port=ssh_port,
            username=username,
            password=password,
            known_hosts=None,  # Set to None to disable host key checks
        )
        return conn
    except asyncssh.Error as error:
        raise ConnectionError(f"Error connecting: {error}")


async def execute_command(
    conn: asyncssh.SSHClientConnection,
    ssh_command: str,
    remote_width: int,
) -> str:
    """Execute the given command on the remote host through the SSH connection."""
    try:
        result = await conn.run(
            command=f"env COLUMNS={remote_width} LINES={LINES} {ssh_command}",
            term_type="ansi" if COLOR else "dumb",
            term_size=(remote_width, LINES),
            env={},
        )
        return result.stdout
    except asyncssh.Error as error:
        raise RuntimeError(f"Error executing command: {error}")
    finally:
        conn.close()


async def stream_command_output(
    conn: asyncssh.SSHClientConnection,
    ssh_command: str,
    remote_width: int,
    output_queue: asyncio.Queue,
) -> None:
    """Stream the output of the command from the remote host to the output queue."""
    try:
        async with conn.create_process(
            command=f"env COLUMNS={remote_width} LINES={LINES} {ssh_command}",
            term_type="ansi" if COLOR else "dumb",
            term_size=(remote_width, 1000),
            env={},
        ) as process:
            async for line in process.stdout:
                line = line.rstrip()
                await output_queue.put(line)  # Put output into the host's output queue
    except asyncssh.Error as error:
        await output_queue.put(f"Error executing command: {error}")


async def execute(
    host_name: str,
    ip_address: str,
    ssh_port: int,
    username: str,
    password: Optional[str],
    ssh_command: str,
    max_name_length: int,
    local_display_width: int,
    separate_output: bool,
) -> None:
    """Establish an SSH connection and execute a command on a remote host."""
    prompt = await get_prompt(host_name, max_name_length)
    remote_width = local_display_width - max_name_length - 3
    output_queue = OUTPUT_QUEUES[host_name]  # Get the host-specific output queue

    try:
        conn = await establish_ssh_connection(ip_address, ssh_port, username, password)
    except ConnectionError as error:
        await output_queue.put(f"Error connecting to {host_name}: {error}")
        return

    try:
        if separate_output:
            output = await execute_command(conn, ssh_command, remote_width)
            await output_queue.put(output)  # Put output into the host's output queue
        else:
            await stream_command_output(conn, ssh_command, remote_width, output_queue)
    except RuntimeError as error:
        await output_queue.put(f"Error executing command on {host_name}: {error}")

    # Signal end of output
    ending_line = "-" * remote_width
    if COLOR:
        await output_queue.put(f"{HOST_COLOR.get(host_name)}{ending_line}{RESET}")
    else:
        await output_queue.put(ending_line)


async def print_output(
    host_name: str,
    max_name_length: int,
    allow_empty_line: bool,
):
    """Print the output from the remote host with the appropriate prompt."""
    output_queue = OUTPUT_QUEUES[host_name]
    prompt = await get_prompt(host_name, max_name_length)

    while True:
        output = await output_queue.get()
        if output is None:
            break
        output = output.replace("\x1b[K", "\x1b[K\r\n")
        for line in output.split("\r\n"):
            if line.startswith("\x1b["):
                line = line.replace("\x1b[1E", f"\x1b[1E{prompt}")
                line = line.replace("\x1b[1F", f"\x1b[1F{prompt}")
                line = line.replace("\x1b[?25l", "")
                line = line.replace("\x1b[?25h", "")
            if allow_empty_line or line.strip():
                print(f"{prompt}{line.rstrip()}{RESET}")


async def main(
    host_file: str,
    ssh_command: str,
    local_display_width: int,
    separate_output: bool,
    allow_empty_line: bool,
) -> None:
    """Main entry point of the script."""
    hosts_to_execute: List[Tuple[str, str, int, str, Optional[str]]] = []

    with open(host_file, "r", encoding="utf-8") as hosts:
        for line in hosts:
            line = line.strip()
            if line and not line.startswith("#"):
                (
                    host_name,
                    ip_address,
                    ssh_port,
                    username,
                    password,
                ) = line.split(",")
                ssh_port = int(ssh_port)
                password = None if password == "#" else password
                hosts_to_execute.append(
                    (
                        host_name,
                        ip_address,
                        ssh_port,
                        username,
                        password,
                    )
                )

    max_name_length = max(len(name) for name, *_ in hosts_to_execute)

    for host_name, *_ in hosts_to_execute:
        OUTPUT_QUEUES[
            host_name
        ] = asyncio.Queue()  # Create an output queue for each host

    print_tasks = [
        print_output(
            host_name,
            max_name_length,
            allow_empty_line,
        )
        for host_name, *_ in hosts_to_execute
    ]
    asyncio.ensure_future(asyncio.gather(*print_tasks))

    tasks = [
        execute(
            host_name,
            ip_address,
            ssh_port,
            username,
            password,
            ssh_command,
            max_name_length,
            local_display_width,
            separate_output,
        )
        for host_name, ip_address, ssh_port, username, password in hosts_to_execute
    ]

    await asyncio.gather(*tasks)

    # Put None in each host's output queue to signal the end of printing
    for host_name in OUTPUT_QUEUES:
        await OUTPUT_QUEUES[host_name].put(None)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Execute commands on multiple remote hosts via SSH."
    )
    parser.add_argument("host_file", help="File containing host information")
    parser.add_argument(
        "command",
        nargs="+",
        help="Command to execute on remote hosts",
    )
    parser.add_argument(
        "-N",
        "--no-color",
        action="store_true",
        help="Disable host coloring",
    )
    parser.add_argument(
        "-S",
        "--separate-output",
        action="store_true",
        help="Print output from each host without interleaving",
    )
    parser.add_argument(
        "-W",
        "--terminal-width",
        type=int,
        help="Set terminal width",
    )
    parser.add_argument(
        "-A",
        "--allow-empty-line",
        action="store_true",
        help="Allow printing the empty line",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="store_true",
        help="Show the version of Hydra",
    )
    args = parser.parse_args()

    host_file: str = args.host_file
    ssh_command: str = " ".join(args.command)
    try:
        local_display_width = args.terminal_width or int(
            os.environ.get("COLUMNS", os.get_terminal_size().columns)
        )
    except OSError:
        local_display_width = args.terminal_width or 80

    if uvloop:
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    if args.version:
        print(
            f"Hydra-{VERSION} powered by {asyncio.get_event_loop_policy().__module__}"
        )
    COLOR = not args.no_color
    asyncio.run(
        main(
            host_file,
            ssh_command,
            local_display_width,
            args.separate_output,
            args.allow_empty_line,
        )
    )
