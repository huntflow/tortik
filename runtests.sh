#!/bin/sh

cd $(dirname $0)
python -m tortik.test.runtests "$@"