import datetime
import os
from gendo import Gendo

path = os.path.dirname(os.path.abspath(__file__))
path_to_yaml = os.path.join(path, 'config.yaml')
gendo = Gendo.config_from_yaml(path_to_yaml)


@gendo.listen_for('cookies')
def cookies(user, message):
    return "I *LOVE* COOOOOOOOKIES!!!!"


@gendo.listen_for('morning')
def morning(user, message):
    # make sure message is morning and doesn't just contain it.
    if message.strip() == "morning":
        now = datetime.datetime.now()
        if now.time() < datetime.time(12):
            return "mornin' @{user.username}"

if __name__ == '__main__':
    gendo.run()
