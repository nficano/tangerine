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

Gendo is a lightweight Slackbot framework that abstracts away all the
boilerplate code required to write bots, allowing you to focus on the problem
at hand.


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


7. Next let's add a task that runs every 5 minutes, simply add the following to
   your *mybot.py* file:

.. code:: python

    @gendo.cron('*/5 * * * *')
    def some_task():
        gendo.speak("Hay Ride!", "#general")


See https://en.wikipedia.org/wiki/Cron#Configuration_file for more details on
the syntax for crontab.



Basic Usage
===========

To start your project, you'll first need to import gendo by adding
``from gendo import Gendo`` to the top of your file.

Next you'll need to create an instance of Gendo and configure your Slack token.
This can be done using a yaml config file or passing it explicitly to the init.

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
Notice that the decorator passes 2 arguments to the function, first the
``user`` object which contains information about the user who triggered the
event (in this case the Slack user who said the word cookies) and ``message``,
which is a string of the complete message.

.. code:: python

   @gendo.listen_for('cookies')
    def cookies(user, message):
        # do something when someone say's "cookies" here.

Finally your script needs to sit inside a loop, monitor whats said in a slack
channel and respond to the messages accordingly. To do this we add the
following to the end of your script:

.. code:: python

    if __name__ == '__main__':
       gendo.run()
