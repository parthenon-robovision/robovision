#!/usr/bin/python
# ssh -i deployment/keys/vagrant.key -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -p 2222 -L 5000:127.0.0.1:5000 vagrant@localhost -C 'sudo -u imagery bash -c "killall python; cd /srv/www && source Envs/imagery/bin/activate && cd imagery/app && AWS_DEFAULT_REGION=us-west-2 IMAGERY_VISION_API_KEYS_FILE=/srv/imagery_credentials/vision_api.json GOOGLE_APPLICATION_CREDENTIALS=/srv/imagery_credentials/gcloud.json FLASK_DEBUG=1 FLASK_APP=app.py flask run"'

import argparse
from subprocess import call

parser = argparse.ArgumentParser(description='Imagery swiss army knife.')
parser.add_argument('command', help='run_dev_server or run_tests.')
args = parser.parse_args()

SSH = [
    '-i', 'deployment/keys/vagrant.key',
    '-o', 'UserKnownHostsFile=/dev/null',
    '-o', 'StrictHostKeyChecking=no',
    '-p', '2222',
    '-L', '5000:127.0.0.1:5000',
    'vagrant@localhost',
    '-C',
]

BASH = [
    'sudo',
    '-u', 'imagery',
    'bash', '-c',
]

ENVS = [
    'PYTHONPATH=/srv/www/imagery/app',
    'AWS_DEFAULT_REGION=us-west-2',
    'IMAGERY_VISION_API_KEYS_FILE=/srv/imagery_credentials/vision_api.json',
    'GOOGLE_APPLICATION_CREDENTIALS=/srv/imagery_credentials/gcloud.json',
    'FLASK_DEBUG=1',
    'FLASK_APP=app.py'
]

DEV_SERVER_COMMAND = [
    'killall python;',
    'cd /srv/www &&',
    'source Envs/imagery/bin/activate &&',
    'cd imagery/app &&',
    ' '.join(ENVS),
    'flask run'
]

RUN_TESTS_COMMAND = [
    'cd /srv/www &&',
    'source Envs/imagery/bin/activate &&',
    'cd imagery/tests &&',
    ' '.join(ENVS), # !!! reversal problem
    'pytest'
]

if args.command == 'run_dev_server':
    call('''ssh {} '{} "{}"' '''.format(' '.join(SSH), ' '.join(BASH), ' '.join(DEV_SERVER_COMMAND)), shell=True)
elif args.command == 'run_tests':
    call('''ssh {} '{} "{}"' '''.format(' '.join(SSH), ' '.join(BASH), ' '.join(RUN_TESTS_COMMAND)), shell=True)
