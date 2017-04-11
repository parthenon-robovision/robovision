# Imagery
To deploy, please make sure the IMAGERY_VAULT_PASSWORD environment variable is
set.

## Dev setup
1. `git clone git+ssh://repository.parthenonsoftware.com/gitprojects/imagery`
2. From within imagery/ : `vagrant up`
3. Point your browser at localhost:8080 .
4. Enjoy.

To run tests `./run_tests.sh`.

## SyntaxNet
SyntaxNet lives in a docker image that is fetched on deploy. A modified version
of syntaxnet/demo.sh is used to run syntaxnet in a container (through stdin
and stdout as usual).

The container is based on brianlow/syntaxnet-docker . The docker container runs
as www-data.
