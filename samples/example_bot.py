#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from tangerine import Tangerine

path = os.path.dirname(os.path.abspath(__file__))
path_to_yaml = os.path.join(path, 'config.yaml')
tangerine = Tangerine.config_from_yaml(path_to_yaml)


@tangerine.listen_for('cookies')
def cookies(user, message):
    return 'I *LOVE* COOOOOOOOKIES!!!!'


@tangerine.listen_for('morning')
def morning(user, message):
    # make sure message is "morning" and doesn't just contain it.
    if message.strip() == 'morning':
        return "mornin' @{user.username}"


if __name__ == '__main__':
    tangerine.run()
