#!/bin/sh

cd ${APP_HOME}
. venv/bin/activate
export PYTHONPATH="./src"
python tests/test_configs.py $@
