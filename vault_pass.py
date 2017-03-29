#!/usr/bin/python
''' Used by ansible-vault to retrieve the vault password from the environment
variable IMAGERY_VAULT_PASSWORD during deploy.'''

import os
import sys

if 'IMAGERY_VAULT_PASSWORD' in os.environ:
    print os.environ['IMAGERY_VAULT_PASSWORD']
    exit(0)

sys.stderr.write('***********\n')
sys.stderr.write('***Error*** Please set the environment variable IMAGERY_VAULT_PASSWORD\n')
sys.stderr.write('***********\n')
exit(1)
