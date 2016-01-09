import pytest
from gendo import Gendo
from hamcrest import *  # noqa
from slackclient import SlackClient
from sys import version_info
from unittest.mock import patch, mock_open


class TestGendo():
    @pytest.fixture
    def confdata(self):
        data = {}
        data['gendo'] = {"channel": "testchannel",
                         "auth_token": "testauthtoken"}
        return data

    @pytest.fixture
    def gi(self, confdata):
        return Gendo(settings=confdata)

    @pytest.fixture
    def conffile(self, confdata):
        return mock_open(read_data=str(confdata))

    def test_init_settings(self, confdata, gi):
        assert_that(gi.settings, equal_to(confdata))

    def test_init_sleep(self, confdata, gi):
        assert_that(gi.sleep, equal_to(0.5))

    def test_init_client(self, confdata, gi):
        assert_that(gi.client, is_(SlackClient))

    @pytest.mark.skipif(
            version_info < (3, 0),
            reason='builtins.open exists only in python 3.0+')
    def test_config_from_yaml(self, gi, conffile):
        with patch('builtins.open', conffile):
            g = Gendo.config_from_yaml(conffile)
        assert_that(gi.settings, equal_to(g.settings))

    def test_listen_for(self, gi):
        decorator = gi.listen_for('test_rule')

        def function_for_decorator(user, message):
            pass
        f = decorator(function_for_decorator)  # noqa
        assert_that(gi.listeners, equal_to([('test_rule',
                    function_for_decorator, {}, {})]))

    """ TODO(sbog): rewrite this when cron tasks will be fixed
    def test_cron(self, gi):
        schedule = "*/5 * * * *"
        decorator = gi.cron(schedule)

        def function_for_decorator(user, message):
            pass
        f = decorator(function_for_decorator)  # noqa
        assert_that(gi.scheduled_tasks, equal_to([Task(schedule,
                    function_for_decorator)]))
    """

    def test_add_listener(self, gi):
        gi.add_listener('test_rule', None, {}, {'a': 'b'})
        assert_that(gi.listeners, equal_to([('test_rule', None, {},
                    {'a': 'b'})]))

    @patch('gendo.bot.SlackClient.api_call')
    def test_user_info(self, mock_call, gi):
        mock_call.return_value = bytes('{"a":"b"}', 'utf-8')
        gi.get_user_info('fake_user_id')
        mock_call.assert_called_with(
          'users.info',
          user='fake_user_id'
          )

    @patch('gendo.bot.Gendo.get_user_info')
    def test_user_name(self, mock_call, gi):
        rv = {}
        rv['user'] = {'name': 'test_user'}
        mock_call.return_value = rv
        user = gi.get_user_name('fake_user_id')
        assert_that(user, equal_to('test_user'))
