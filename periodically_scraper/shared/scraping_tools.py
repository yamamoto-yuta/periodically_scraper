from http import HTTPStatus
import requests
from time import sleep
from random import random
from typing import Tuple


def get_html(url: str, N_RETRY: int = 3) -> Tuple[str, int]:
    """指定URLのHTMLを取得する

    Parameters
    ----------
    url : str
        リクエストを送りたいURL
    N_RETRY : int, optional
        スクレイピング失敗時のリトライ回数, by default 3

    Returns
    -------
    str
        HTML文書
    int
        HTTP status code
    """
    for _ in range(N_RETRY):
        sleep(random())
        response = requests.get(url)
        if response.status_code == HTTPStatus.OK:
            return response.text, response.status_code
        elif response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
            continue
        elif response.status_code == HTTPStatus.NOT_FOUND:
            return "", response.status_code
        else:
            return "", response.status_code
    else:
        return "", response.status_code
