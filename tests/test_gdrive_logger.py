import os
from pathlib import Path

import pytest

from periodically_scraper.shared.gdrive_client import GDriveClient
from periodically_scraper.shared.gdrive_logger import GDriveLogger
from periodically_scraper.shared.utils_for_test import get_target_test_folder_id


@pytest.fixture
def fixture_initialize():
    """initialize() のFixture"""
    # 期待する結果
    gdrive_log_filename = "test_gdrive_logger.log"

    # 前処理
    gdrive = GDriveClient()
    test_log_folder_id = get_target_test_folder_id(gdrive, __name__, test_initialize.__name__)

    # テストしたい処理
    logger = GDriveLogger(gdrive, test_log_folder_id)
    file = logger.initialize(gdrive_log_filename)

    # 比較
    yield file, gdrive_log_filename, logger.log_config["handlers"]["fileHandler"]["filename"]

    # 後処理
    file.Trash()


def test_initialize(fixture_initialize):
    """initialize() のテスト"""
    file, gdrive_log_filename, local_log_filename = fixture_initialize

    assert file["title"] == gdrive_log_filename, "ログファイル名が一致しません"


@pytest.fixture
def fixture_info():
    """info() のFixture"""
    # テスト用入力
    logged_text = "test"

    # 前処理
    gdrive = GDriveClient()
    test_log_folder_id = get_target_test_folder_id(gdrive, __name__, test_info.__name__)
    logger = GDriveLogger(gdrive, test_log_folder_id)
    logger.initialize()

    # テストしたい処理
    file = logger.info(logged_text)

    # 比較
    yield file, logged_text

    # 後処理
    file.Trash()


def test_info(fixture_info):
    """info() のテスト"""
    file, logged_text = fixture_info

    assert file.GetContentString().split()[-1] == logged_text, "書き込まれたメッセージが一致しません"


@pytest.fixture
def fixture_error():
    """error() のFixture"""
    # テスト用入力
    logged_text = "test"

    # 前処理
    gdrive = GDriveClient()
    test_log_folder_id = get_target_test_folder_id(gdrive, __name__, test_error.__name__)
    logger = GDriveLogger(gdrive, test_log_folder_id)
    logger.initialize()

    # テストしたい処理
    file = logger.error(logged_text)

    # 比較
    yield file, logged_text

    # 後処理
    file.Trash()


def test_error(fixture_error):
    """error() のテスト"""
    file, logged_text = fixture_error

    assert file.GetContentString().split()[-1] == logged_text, "書き込まれたメッセージが一致しません"
