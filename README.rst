===============
Gendo for Slack
===============

.. image:: https://img.shields.io/pypi/v/gendobot.svg
  :alt: Pypi
  :target: https://pypi.python.org/pypi/gendobot/

.. image:: https://img.shields.io/pypi/pyversions/gendobot.svg
  :alt: Python Versions
  :target: https://pypi.python.org/pypi/gendobot/

.. image:: https://travis-ci.org/nficano/gendo.svg?branch=master
   :alt: Build status
   :target: https://travis-ci.org/nficano/gendo

Description
===========

Gendo is a Slack bot/wrapper around Python's SlackClient, that allows anyone to
have a Slack bot up and running in minutes.


Installation
============

1. Clone the repository locally:

.. code:: bash

    git clone git@github.com:nficano/gendo.git


2. `cd` into the repo and install the dependencies:

.. code:: bash

    pip install -r requirements.txt


3. Duplicate/rename the sample config.yaml file.

.. code:: bash

    cp config.yaml.sample config.yaml


4. Edit the config file adding your Slack API token and channel name.
5. Run the client!

.. code:: bash

    python gendo.py

Todo
=====
add some fishing unit tests
