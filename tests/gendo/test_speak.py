import mock

from tangerine import Tangerine

TEST_TEXT = ':muffpunch:'
TEST_TOKEN = '111'
TEST_CHANNEL = 'tests'


class TestSpeak(object):
    @mock.patch('tangerine.bot.Tangerine.speak')
    def test_speak(self, mock_speak):
        tangerine = Tangerine(TEST_TOKEN)
        tangerine.speak(TEST_TEXT, TEST_CHANNEL)
        mock_speak.assert_called_with(TEST_TEXT, TEST_CHANNEL)

    @mock.patch('tangerine.bot.SlackClient.api_call')
    def test_slack_call(self, mock_call):
        tangerine = Tangerine(TEST_TOKEN)
        tangerine.speak(TEST_TEXT, TEST_CHANNEL)
        mock_call.assert_called_with(
          'chat.postMessage',
          as_user='true:',
          channel='tests',
          text=TEST_TEXT
        )
