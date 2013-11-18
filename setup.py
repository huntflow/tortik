#!/usr/bin/env python

import subprocess
import re
import os

from setuptools import setup, find_packages, Command

changedata = subprocess.Popen(["dpkg-parsechangelog"], shell=False, stdout=subprocess.PIPE).communicate()[0]
version = re.search("Version: (?P<ver>\d+\..*)", changedata).groupdict()["ver"]

def find_package_data(package, *directories):
    data_files = []
    current_dir = os.path.abspath(os.curdir)
    package_dir = os.path.dirname(__import__(package, fromlist=[""]).__file__)
    os.chdir(package_dir)

    for directory in directories:
        for dirpath, dirnames, filenames in os.walk(directory):
            [data_files.append(os.path.join(dirpath, f)) for f in filenames]

    os.chdir(current_dir)

    return data_files

class TestCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        subprocess.check_call(["python", "-m", "tortik.test.runtests"])

setup(
    name="tortik",
    version=version,
    description="Tortik - python tornado framework",
    long_description=open("README.md").read(),
    url="https://github.com/hhru/tortik",
    packages=find_packages(exclude=['tortik.test']),
    package_data={
        "tortik": find_package_data("tortik", "templates"),
    },
    cmdclass={'test': TestCommand},
    install_requires=[
        "lxml >= 2.2.4",
        "tornado >= 2.0",
        "tornado_util >= 0.1",
    ]
)