#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from setuptools import setup, find_packages
from itertools import ifilter
from os import path
from ast import parse
import pip
requirements = pip.req.parse_requirements("requirements.txt",
                                          session=pip.download.PipSession())

pip_requirements = [str(r.req) for r in requirements]

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('LICENSE.txt') as readme_file:
    license = readme_file.read()

with open(path.join('gendo', '__init__.py')) as f:
    __version__ = parse(next(ifilter(
        lambda line: line.startswith('__version__'), f))).body[0].value.s

setup(
    name='gendobot',
    author='Nick Ficano',
    author_email='nficano@gmail.com',
    version=__version__,
    packages=find_packages(exclude=['tests*']),
    url='http://nickficano.com',
    description="a lightweight Slackbot framework for Python",
    zip_safe=False,
    install_requires=pip_requirements,
    long_description=readme,
    license=license,
    classifiers=[
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python",
        "Topic :: Internet",
    ]
)
