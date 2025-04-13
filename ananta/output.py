from . import RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, RESET
from itertools import cycle
from random import shuffle
from typing import Dict
import asyncio
import re

COLORS = [RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN]
shuffle(COLORS)
COLORS_CYCLE = cycle(COLORS)
HOST_COLOR: Dict[str, str] = {}

# Pattern to match common cursor control and screen clear ANSI codes
ansi_cursor_control = re.compile(
    r"\x1b\[(\d+)?[ABEFCD]|"  # cursor movement
    r"\x1b\[\d+;\d+[HF]|"  # cursor position
    r"\x1b\[[?]\d+[hl]|"  # cursor visibility
    r"\x1b\[[sSu]|"  # cursor save/restore
    r"\x1b\[\d*J"  # screen clear
)


def adjust_cursor_with_prompt(
    line: str, prompt: str, allow_cursor_control: bool
) -> str:
    """Adjust the cursor control codes to display correctly with Ananta prompt."""
    if not allow_cursor_control:
        line = ansi_cursor_control.sub("", line)

    # If erase to the beginning of line, jump to col 0, add prompt, then return
    line = line.replace("\x1b[1K", f"\x1b[1K\x1b[s\x1b[G{prompt}\x1b[u")

    # If erase the whole line, jump to col 0, add prompt, then return
    line = line.replace("\x1b[2K", f"\x1b[2K\x1b[s\x1b[G{prompt}\x1b[u")

    # Add prompt to any carriage return
    line = line.replace("\r", f"\r{prompt}")

    return line.rstrip()


def _get_host_color(host_name: str) -> str:
    if HOST_COLOR.get(host_name) is None:
        HOST_COLOR[host_name] = next(COLORS_CYCLE)
    return HOST_COLOR[host_name]


def get_prompt(host_name: str, max_name_length: int, color: bool) -> str:
    """Generate a formatted prompt for displaying the host's name."""
    if color:
        return f"{_get_host_color(host_name)}[{host_name.rjust(max_name_length)}]{RESET} "
    return f"[{host_name.rjust(max_name_length)}] "


def get_end_marker(host_name: str, remote_width: int, color: bool) -> str:
    """Generate an ending line with color matched the host's color."""
    ending_line = "-" * remote_width
    if color:
        return f"{_get_host_color(host_name)}{ending_line}{RESET}"
    return ending_line


async def print_output(
    host_name: str,
    max_name_length: int,
    allow_empty_line: bool,
    allow_cursor_control: bool,
    separate_output: bool,
    print_lock: asyncio.Lock,
    output_queue: asyncio.Queue,
    color: bool,
):
    """Print the output from the remote host with the appropriate prompt."""
    prompt = get_prompt(host_name, max_name_length, color)

    while True:
        output = await output_queue.get()
        if output is None:
            break
        lines = output.split("\n")
        if separate_output:
            # Synchronize printing of the entire output
            async with print_lock:
                for line in lines:
                    adjusted_line = adjust_cursor_with_prompt(
                        line, prompt, allow_cursor_control
                    )
                    if allow_empty_line or adjusted_line.strip():
                        print(f"{prompt}{adjusted_line}{RESET}")
        else:
            for line in lines:
                adjusted_line = adjust_cursor_with_prompt(
                    line, prompt, allow_cursor_control
                )
                if allow_empty_line or adjusted_line.strip():
                    # Synchronize printing of a single line
                    async with print_lock:
                        print(f"{prompt}{adjusted_line}{RESET}")
