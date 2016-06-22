# -*- coding: utf-8 -*-
 
 
"""setup.py: setuptools control."""
 
 
import re
from setuptools import setup, find_packages

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
    packages = find_packages(),
    entry_points = {
        "console_scripts": ['%s = %s.%s:main' % (projectName,projectName,projectName)]
        },
    install_requires = ['mazepy>=0.2'],
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
    "Topic :: Games/Entertainment",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3 :: Only"
    ]
    )
