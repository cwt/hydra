#!/usr/bin/env python

import asyncio
import os
import sys
from typing import Dict, List, Tuple, Optional

import asyncssh
try:
    import uvloop
except ImportError:
    uvloop = None


async def get_prompt(name: str, max_name: int) -> str:
    return f"[{name.rjust(max_name)}] "


async def execute(
    name: str,  # Host alias name
    ip: str,  # IP address or hostname
    port: int,  # SSH port
    username: str,
    password: Optional[str],
    command: str,
    max_name: int,
    local_width: int,
) -> Tuple[str, str]:
    prompt = await get_prompt(name, max_name)
    remote_width = local_width - len(prompt)

    try:
        async with asyncssh.connect(
            host=ip,
            port=port,
            username=username,
            password=password,
            known_hosts=None,  # Set to None to disable host key checks
        ) as conn:
            result = await conn.run(
                f"export COLUMNS={remote_width} && {command}",
                term_type="ansi",
                term_size=(remote_width, 1000),  # Large height for long outputs
            )

        output = result.stdout.strip()
        return name, output

    except Exception as e:
        return name, f"Error connecting to {name}: {e}"


async def main(host_file: str, command: str, local_width: int) -> None:
    clients: Dict[str, asyncssh.SSHClientConnection] = {}
    hosts_to_execute: List[Tuple[str, str, int, str, Optional[str]]] = []

    with open(host_file, "r") as hosts:
        for line in hosts:
            line = line.strip()
            if line and not line.startswith("#"):
                name, ip, port, username, password = line.split(",")
                port = int(port)
                password = None if password == "#" else password
                hosts_to_execute.append((name, ip, port, username, password))

    max_name = max([len(name) for name, *_ in hosts_to_execute])

    results = await asyncio.gather(
        *[
            execute(name, ip, port, username, password, command, max_name, local_width)
            for name, ip, port, username, password in hosts_to_execute
        ]
    )

    results_dict = dict(results)

    for name, ip, port, username, password in hosts_to_execute:
        prompt = await get_prompt(name, max_name)
        output = results_dict[name]
        lines = output.split("\n")
        for line in lines:
            print(f"{prompt}{line}")

        if len(lines) > 1:
            print("-" * local_width)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} [hosts file] [command]")
        sys.exit(1)

    host_file: str = sys.argv[1]
    command: str = " ".join(sys.argv[2:])
    try:
        local_width = int(os.environ.get("COLUMNS", os.get_terminal_size().columns))
    except Exception:
        local_width = 80

    if uvloop:
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    asyncio.run(main(host_file, command, local_width))
