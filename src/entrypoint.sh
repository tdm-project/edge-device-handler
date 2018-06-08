#!/bin/sh

cd ${APP_HOME}
. venv/bin/activate
python src/htu21d_publisher.py $@
