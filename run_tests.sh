#!/bin/bash
ssh \
-i deployment/keys/vagrant.key \
-o UserKnownHostsFile=/dev/null \
-o StrictHostKeyChecking=no \
-p 2222 vagrant@localhost \
-C 'sudo -u www-data bash -c "cd /srv/www && source Envs/imagery/bin/activate && cd imagery/tests && PYTHONPATH=/srv/www/imagery/app AWS_DEFAULT_REGION=us-west-2 IMAGERY_VISION_API_KEYS_FILE=/srv/imagery_credentials/vision_api.json GOOGLE_APPLICATION_CREDENTIALS=/srv/imagery_credentials/gcloud.json FLASK_DEBUG=1 pytest"'
