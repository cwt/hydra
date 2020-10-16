#!/usr/bin/env python

import os
import paramiko
import sys

command = ' '.join(sys.argv[2:])
clients = dict()

with open(sys.argv[1], 'r') as hosts:
    for line in hosts:
        line = line.strip()
        if line and not line.startswith('#'):
            name, ip, port, username, password = line.split(',')
            clients[name] = paramiko.SSHClient()
            clients[name].set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if password == '#':
                clients[name].connect(
                    hostname=ip,
                    port=int(port),
                    username=username
                )
            else:
                clients[name].connect(
                    hostname=ip,
                    port=int(port),
                    username=username,
                    password=password
                )

for name in clients.keys():
    prompt = f'[{name}] '
    terminal_columns = os.get_terminal_size().columns
    remote_columns = terminal_columns - len(prompt)
    ssh_stdin, ssh_stdout, ssh_stderr = clients[name].exec_command(
        f'export COLUMNS={remote_columns} && {command}',
        get_pty=True
    )
    lines = 0
    for line in ssh_stdout:
        print(f'{prompt}{line.strip()}')
        lines += 1
    if lines > 1:
        print('-' * terminal_columns)

for name in clients.keys():
    if clients[name]._transport:
        clients[name].close()

