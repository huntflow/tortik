#!/bin/sh

version=`dpkg-parsechangelog| grep Version | sed "s/^Version: \(.*\)/\1/"`
echo "version = '$version'" > debian/python-tortik/usr/share/pyshared/tortik/version.py

