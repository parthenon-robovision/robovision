#!/usr/bin/python
import os
import sys

if 'IMAGERY_VAULT_PASSWORD' in os.environ:
    print os.environ['IMAGERY_VAULT_PASSWORD']

sys.stderr.write('***********\n')
sys.stderr.write('***Error*** Please set the environment variable IMAGERY_VAULT_PASSWORD\n')
sys.stderr.write('***********\n')
exit(1)
