import os
import requests
from http import HTTPStatus
import json
import traceback


class SlackClient(object):
    """
    Slackクライアントクラス
    """

    def __init__(self):
        """コンストラクタ"""
        self.__headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.environ['SLACK_BOT_TOKEN']}"
        }
        self.__endpoint = "https://slack.com/api/chat.postMessage"

    def post_message(self, text: str) -> None:
        """
        メッセージを送信する関数

        Parameters
        ----------
        text : str
            メッセージの文字列
        """
        payload = {
            "channel": os.environ["SLACK_CHANNEL"],
            "text": text,
        }
        response = requests.post(self.__endpoint, headers=self.__headers, data=json.dumps(payload)).json()

    def post_error(self):
        """
        エラーを送信するメソッド
        """
        # メッセージブロックのテンプレート
        def error_block_template(traceback_str) -> list: return [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "Traceback:",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"```{traceback_str}```"
                }
            }
        ]
        # トレースバック
        traceback_str = traceback.format_exc()
        # ペイロード
        payload = {
            "channel": os.environ["SLACK_CHANNEL"],
            "blocks": error_block_template(traceback_str),
        }
        # 送信
        response = requests.post(self.__endpoint, headers=self.__headers, data=json.dumps(payload)).json()


# インスタンス化
slack = SlackClient()
