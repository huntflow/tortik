#!/usr/bin/env python

import subprocess
import re

from setuptools import setup, find_packages, Command

changedata = subprocess.Popen(["dpkg-parsechangelog"], shell=False, stdout=subprocess.PIPE).communicate()[0]
version = re.search("Version: (?P<ver>\d+\..*)", changedata).groupdict()["ver"]

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
    cmdclass={'test': TestCommand},
    install_requires=[
        "lxml >= 2.2.4",
        "tornado >= 2.0",
        "tornado_util >= 0.1",
    ]
)