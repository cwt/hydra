#!/usr/bin/env python

import os
import sys
import paramiko

COMMAND = ' '.join(sys.argv[2:])
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

max_name = max([len(name) for name in clients])
for name in clients:
    prompt = f'[{name.rjust(max_name)}] '
    terminal_columns = 80
    try:
        terminal_columns = int(
            os.environ.get('COLUMNS', os.get_terminal_size().columns)
        )
    except Exception:
        pass
    remote_columns = terminal_columns - len(prompt)
    ssh_stdin, ssh_stdout, ssh_stderr = clients[name].exec_command(
        f'export COLUMNS={remote_columns} && {COMMAND}',
        get_pty=True
    )
    ssh_stdin.close()
    lines = 0
    for line in ssh_stdout:
        print(f'{prompt}{line.strip()}')
        lines += 1
    if lines > 1:
        print('-' * terminal_columns)
    if getattr(clients[name], '_transport', None):
        clients[name].close()

