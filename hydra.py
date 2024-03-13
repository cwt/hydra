#!/usr/bin/env python
"""
Hydra: a command-line tool that allows users to execute commands on multiple
remote hosts at once via SSH. With Hydra, you can streamline your workflow,
automate repetitive tasks, and save time and effort.
"""

import argparse
import asyncio
import os
import sys
from itertools import cycle
from random import shuffle
from typing import Dict, List, Tuple, Optional

import asyncssh

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

try:
    import uvloop
except ImportError:
    uvloop = None


async def get_prompt(host_name: str, max_name_length: int) -> str:
    """Generate a formatted prompt for displaying the host's name."""
    if HOST_COLOR.get(host_name) is None:
        for color in COLORS_CYCLE:
            HOST_COLOR[host_name] = color
            break
    return f"{HOST_COLOR.get(host_name)}[{host_name.rjust(max_name_length)}]{RESET} "


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
            f"export COLUMNS={remote_width} && {ssh_command}",
            term_type="ansi",
            term_size=(
                remote_width,
                1000,
            ),  # Large height for long outputs
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
            f"export COLUMNS={remote_width} && {ssh_command}",
            term_type="ansi",
            term_size=(
                remote_width,
                1000,
            ),  # Large height for long outputs
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
    remote_width = local_display_width - len(prompt)
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

    await output_queue.put(
        f"{HOST_COLOR[host_name]}" + "-" * remote_width + f"{RESET}"
    )  # Signal end of output


async def print_output(
    host_name: str,
    max_name_length: int,
    separate_output: bool,
    allow_empty_line: bool,
):
    """Print the output from the remote host with the appropriate prompt."""
    output_queue = OUTPUT_QUEUES[host_name]
    prompt = await get_prompt(host_name, max_name_length)

    while True:
        output = await output_queue.get()
        if output is None:
            break
        if separate_output:
            for line in output.split("\n"):
                if allow_empty_line or line.strip():
                    print(f"{prompt}{line}")
        else:
            if allow_empty_line or output.strip():
                print(f"{prompt}{output}")


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

    for host_name, *_ in hosts_to_execute:
        asyncio.ensure_future(
            print_output(
                host_name,
                max_name_length,
                separate_output,
                allow_empty_line,
            )
        )

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
    args = parser.parse_args()

    HOST_FILE: str = args.host_file
    SSH_COMMAND: str = " ".join(args.command)
    try:
        LOCAL_DISPLAY_WIDTH = args.terminal_width or int(
            os.environ.get("COLUMNS", os.get_terminal_size().columns)
        )
    except OSError:
        LOCAL_DISPLAY_WIDTH = args.terminal_width or 80

    if uvloop:
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    asyncio.run(
        main(
            HOST_FILE,
            SSH_COMMAND,
            LOCAL_DISPLAY_WIDTH,
            args.separate_output,
            args.allow_empty_line,
        )
    )
