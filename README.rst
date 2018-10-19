===============
Tangerine for Slack
===============

.. image:: https://img.shields.io/pypi/v/tangerinebot.svg
  :target: https://pypi.python.org/pypi/tangerinebot/

.. image:: https://img.shields.io/pypi/pyversions/tangerinebot.svg
  :target: https://pypi.python.org/pypi/tangerinebot/

.. image:: https://travis-ci.org/nficano/tangerine.svg?branch=master
  :target: https://travis-ci.org/nficano/tangerine

.. image:: https://coveralls.io/repos/nficano/tangerine/badge.svg?branch=master&service=github&cb=321
  :target: https://coveralls.io/github/nficano/tangerine?branch=master

Description
===========

Tangerine is a lightweight Slackbot framework that abstracts away all the
boilerplate code required to write bots, allowing you to focus on the problem
at hand.


Installation
============

1. In a new project folder for your bot:

.. code:: bash

   $ mkdir myslackbot
   $ cd myslackbot

2. Install ``tangerinebot`` from *pypi*.

.. code:: bash

    $ pip install tangerinebot


3. Next make another file for your bot's logic:

.. code:: bash

    $ touch mybot.py


4. Also in your favourate text editor, edit *mybot.py* with the following:


.. code:: python

    #!/usr/bin/env python
    # -*- coding: utf-8 -*-
    from tangerine import Tangerine
    tangerine = Tangerine("xoxb-1234567890-replace-this-with-token-from-slack")


    @tangerine.listen_for('morning')
    def morning(user, message):
        return "mornin' @{user.username}"

    if __name__ == '__main__':
       tangerine.run()


5. Now try running it, run the following command then say "*morning*" in Slack.

.. code:: bash

    $ python mybot.py


Basic Usage
===========

To start your project, you'll first need to import tangerine by adding
``from tangerine import Tangerine`` to the top of your file.

Next you'll need to create an instance of Tangerine and configure your Slack token.
This can be done using a yaml config file or passing it explicitly to the
initialization.

.. code:: python

    # Option 1: YAML config:
    import os
    from tangerine import Tangerine

    path = os.path.dirname(os.path.abspath(__file__))
    path_to_yaml = os.path.join(path, 'config.yaml')
    tangerine = Tangerine.config_from_yaml(path_to_yaml)

.. code:: python

    # Option 2: Hardcoded slack token
    from tangerine import Tangerine
    tangerine = Tangerine("xoxb-1234567890-replace-this-with-token-from-slack")

Now its time to write your ``response`` functions, these functions get wrapped
with the ``listen_for`` decorator, which registers a pattern to watch the slack
conversation for and which python method should handle it once its said.

In the following example, the method is setup to listen for the word "*cookies*".
Notice that the decorator passes two arguments to the function, first the
``user`` object which contains information about the user who triggered the
event (in this case the Slack user who said the word cookies) and ``message``,
which is a string of the complete message.

.. code:: python

    @tangerine.listen_for('cookies')
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


    @tangerine.listen_for(nicks_joke_rule)
    @tangerine.listen_for(bens_joke_rule)
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
       tangerine.run()


Crontab
=======

Sometimes you'll run into situations where you want Slack messages to be sent
periodically rather than in direct response to a keyword, for this Tangerine ships
with a single-threaded Python implementation of Cron.

Let's pretend we want to send a message to everyone in a channel every five
minutes, simply add the following to your *mybot.py* file:

.. code:: python

    @tangerine.cron('*/5 * * * *')
    def some_task():
        tangerine.speak("Hay Ride!", "#general")


See https://en.wikipedia.org/wiki/Cron#Configuration_file for more details on
crontab syntax.

Development
===========

Development of "tangerine" is facilitated exclusively on GitHub. Contributions in the form of patches, tests and feature creation and/or requests are very welcome and highly encouraged. Please open an issue if this tool does not function as you'd expect.


How to release updates
----------------------

If this is the first time you're releasing to pypi, you'll need to run: ``pip install -r tests/dev_requirements.txt``.

Once complete, execute the following commands:

.. code:: bash

    git checkout master

    # Increment the version number and tag the release.
    bumpversion [major|minor|patch]

    # Upload the distribution to PyPi
    python setup.py sdist bdist_wheel upload

    # Since master often contains work-in-progress changes, increment the version
    # to a patch release to prevent inaccurate attribution.
    bumpversion --no-tag patch

    git push origin master --tags
