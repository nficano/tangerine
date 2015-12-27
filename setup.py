#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from setuptools import setup, find_packages
from gendo import __version__

pip_requirements = []
for line in open('requirements.txt').readlines():
    li = line.strip()
    if not li.startswith("#"):
        pip_requirements.append(line)

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('LICENSE.txt') as readme_file:
    license = readme_file.read()

setup(
    name='gendo',
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
        "Programming Language :: Python :: 2.7",
        "Topic :: Internet",
    ]
)
