# -*- coding: utf-8 -*-
 
 
"""setup.py: setuptools control."""
 
 
import re
from setuptools import setup

projectName="mazingame"
scriptFile="%s/%s.py" % (projectName,projectName)
description="A game of maze."


version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open(scriptFile).read(),
    re.M
    ).group(1)
 
 
with open("README.rst", "rb") as f:
    long_descr = f.read().decode("utf-8")
 
 
setup(
    name = projectName,
    packages = [projectName],
    entry_points = {
        "console_scripts": ['%s = %s.%s:main' % (projectName,projectName,projectName)]
        },
    version = version,
    description = description,
    long_description = long_descr,
    author = "Sami Salkosuo",
    author_email = "dev@rnd-dev.com",
    url = "https://github.com/samisalkosuo/mazingame",
    license='MIT',
    classifiers=[
    "Environment :: Console :: Curses",
    "License :: OSI Approved :: MIT License",
    "Natural Language :: English",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 2 :: Only",
    "Topic :: Games/Entertainment"
    ],
    )