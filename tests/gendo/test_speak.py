import mock

from gendo import Gendo

TEST_TEXT = ':muffpunch:'
TEST_TOKEN = '111'
TEST_CHANNEL = 'tests'


class TestSpeak(object):
  @mock.patch('gendo.bot.Gendo.speak')
  def test_speak(self, mock_speak):
    gendo = Gendo(__name__, TEST_TOKEN)
    gendo.speak(TEST_TEXT, TEST_CHANNEL)
    mock_speak.assert_called_with(TEST_TEXT, TEST_CHANNEL)

  @mock.patch('gendo.bot.SlackClient.api_call')
  def test_slack_call(self, mock_call):
    gendo = Gendo(__name__, TEST_TOKEN)
    gendo.speak(TEST_TEXT, TEST_CHANNEL)
    mock_call.assert_called_with(
      'chat.postMessage',
      as_user='true:',
      channel='tests',
      text=TEST_TEXT
    )
