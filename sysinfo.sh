#!/bin/bash

./hydra.py hosts.all 'source /etc/os-release ; echo CPU: $(nproc) x $(lscpu |grep "^Model name" |tr -s " " |cut -d ":" -f2) Mem: $(free -h |grep ^Mem |tr -s " " |cut -d " " -f2) OS: $PRETTY_NAME'
