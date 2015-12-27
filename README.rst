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

1. In a new project folder for your bot:

.. code:: bash

   mkdir myslackbot
   cd myslackbot

2. Install gendobot from *pypi*.

.. code:: bash

    pip install gendobot

3. Make a new file for your bot's config:

.. code:: bash

    touch config.yaml

4. In your favorite text editor, edit *config.yaml* with the following:

.. code:: yaml

    gendo:
      channel: "#general"
      auth_token: "xoxb-1234567890-replace-this-with-token-from-slack"


4. Next make another file for your bot's logic:

.. code:: bash

    touch mybot.py


5. Also in your favorite text editor, edit *mybot.py* with the following:


.. code:: python

    #!/usr/bin/env/python
    # -*- coding: utf-8 -*-
    import os
    from gendo import Gendo

    path = os.path.dirname(os.path.abspath(__file__))
    path_to_yaml = os.path.join(path, 'config.yaml')
    gendo = Gendo.config_from_yaml(path_to_yaml)


    @gendo.listen_for('morning')
    def morning(user, message):
        return "mornin' @{user.username}"

    if __name__ == '__main__':
       gendo.run()


6. Now try running it, run the following command then say "morning" in Slack.

.. code:: bash

    python mybot.py
