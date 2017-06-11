#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from setuptools import setup, find_packages
try:
    from itertools import ifilter
except:
    ifilter = filter
import pip
requirements = pip.req.parse_requirements(
    "requirements.txt",
    session=pip.download.PipSession()
)

pip_requirements = [str(r.req) for r in requirements]

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('LICENSE.txt') as readme_file:
    license = readme_file.read()

setup(
    name='gendobot',
    author='Nick Ficano',
    author_email='nficano@gmail.com',
    version='2.4.0',
    packages=find_packages(exclude=['tests*']),
    url='http://nickficano.com',
    description="a lightweight Slackbot framework for Python",
    zip_safe=False,
    install_requires=pip_requirements,
    long_description=readme,
    license=license,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: MacOS",
        "Operating System :: Microsoft",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",        
        "Programming Language :: Python",
        "Topic :: Communications :: Chat",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries",
    ]
)
