#!/bin/sh
ssh -i deployment/keys/vagrant.key -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -p 2222 -L 5000:127.0.0.1:5000 vagrant@localhost -C 'sudo -u imagery bash -c "killall python; cd /srv/www && source Envs/imagery/bin/activate && cd imagery/app && GOOGLE_APPLICATION_CREDENTIALS=/srv/imagery_credentials/gcloud.json FLASK_DEBUG=1 FLASK_APP=app.py flask run"'
