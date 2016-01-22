===============
Gendo for Slack
===============

.. image:: https://img.shields.io/pypi/v/gendobot.svg
  :target: https://pypi.python.org/pypi/gendobot/

.. image:: https://img.shields.io/pypi/dm/gendobot.svg
  :target: https://pypi.python.org/pypi/gendobot/

.. image:: https://img.shields.io/pypi/pyversions/gendobot.svg
  :target: https://pypi.python.org/pypi/gendobot/

.. image:: https://travis-ci.org/nficano/gendo.svg?branch=master
  :target: https://travis-ci.org/nficano/gendo

.. image:: https://coveralls.io/repos/nficano/gendo/badge.svg?branch=master&service=github&cb=321
  :target: https://coveralls.io/github/nficano/gendo?branch=master

Description
===========

Gendo is a lightweight Slackbot framework that abstracts away all the
boilerplate code required to write bots, allowing you to focus on the problem
at hand.


Installation
============

1. In a new project folder for your bot:

.. code:: bash

   $ mkdir myslackbot
   $ cd myslackbot

2. Install ``gendobot`` from *pypi*.

.. code:: bash

    $ pip install gendobot


3. Next make another file for your bot's logic:

.. code:: bash

    $ touch mybot.py


4. Also in your favourate text editor, edit *mybot.py* with the following:


.. code:: python

    #!/usr/bin/env python
    # -*- coding: utf-8 -*-
    from gendo import Gendo
    gendo = Gendo("xoxb-1234567890-replace-this-with-token-from-slack")


    @gendo.listen_for('morning')
    def morning(user, message):
        return "mornin' @{user.username}"

    if __name__ == '__main__':
       gendo.run()


5. Now try running it, run the following command then say "*morning*" in Slack.

.. code:: bash

    $ python mybot.py


Basic Usage
===========

To start your project, you'll first need to import gendo by adding
``from gendo import Gendo`` to the top of your file.

Next you'll need to create an instance of Gendo and configure your Slack token.
This can be done using a yaml config file or passing it explicitly to the
initialization.

.. code:: python

    # Option 1: YAML config:
    import os
    from gendo import Gendo

    path = os.path.dirname(os.path.abspath(__file__))
    path_to_yaml = os.path.join(path, 'config.yaml')
    gendo = Gendo.config_from_yaml(path_to_yaml)

.. code:: python

    # Option 2: Hardcoded slack token
    from gendo import Gendo
    gendo = Gendo("xoxb-1234567890-replace-this-with-token-from-slack")

Now its time to write your ``response`` functions, these functions get wrapped
with the ``listen_for`` decorator, which registers a pattern to watch the slack
conversation for and which python method should handle it once its said.

In the following example, the method is setup to listen for the word "*cookies*".
Notice that the decorator passes two arguments to the function, first the
``user`` object which contains information about the user who triggered the
event (in this case the Slack user who said the word cookies) and ``message``,
which is a string of the complete message.

.. code:: python

    @gendo.listen_for('cookies')
    def cookies(user, message):
        # do something when someone say's "cookies" here.


You can also set more complicated rules with callables, and you can stack them!
Here's an example.

.. code:: python

    def nicks_joke_rule(name, message):
        is_nick = name == 'nficano'
        is_telling_a_joke = message.lower().count('knock') == 2
        return is_nick and is_telling_a_joke


    def bens_joke_rule(name, message):
        is_ben = name == 'johnbenjaminlewis'
        is_telling_a_joke = message.lower().count('knock') == 2


    @gendo.listen_for(nicks_joke_rule)
    @gendo.listen_for(bens_joke_rule)
    def another_joke(name, message):
        if name == 'johnbenjaminlewis':
            return '@johnbenjaminlewis, nice try. But no.'
        elif name == 'nficano':
            return "@here Nick's telling a joke! Who's there?!?"

Finally your script needs to sit inside a loop, monitor whats said in a slack
channel and respond to the messages accordingly. To do this we add the
following to the end of your script:

.. code:: python

    if __name__ == '__main__':
       gendo.run()


Crontab
-----------------------

Sometimes you'll run into situations where you want Slack messages to be sent
periodically rather than in direct response to a keyword, for this Gendo ships
with a single-threaded Python implementation of Cron.

Let's pretend we want to send a message to everyone in a channel every five
minutes, simply add the following to your *mybot.py* file:

.. code:: python

    @gendo.cron('*/5 * * * *')
    def some_task():
        gendo.speak("Hay Ride!", "#general")


See https://en.wikipedia.org/wiki/Cron#Configuration_file for more details on
crontab syntax.
