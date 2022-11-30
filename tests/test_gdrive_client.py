import os
from pathlib import PurePath

import pytest

from periodically_scraper.shared.gdrive_client import GDriveClient
from periodically_scraper.shared.utils_for_test import get_target_test_folder_id


def test_list_file():
    """list_file() のテスト"""
    # テストしたい処理を実行
    gdrive = GDriveClient()
    test_list_file_folder_id = get_target_test_folder_id(gdrive, __name__, test_list_file.__name__)
    file_list = gdrive.list_file(f"'{test_list_file_folder_id}' in parents")
    result = [file["title"] for file in file_list]

    # 比較
    with open(f"{os.environ['WORKING_DIR']}/tests/cases/gdrive_client/list_file/output.txt", "r") as f:
        output = f.read().splitlines()
    assert result == output, "処理結果が一致しません"


def test_download_file():
    """download_file() のテスト"""
    # テストしたい処理を実行
    gdrive = GDriveClient()
    test_download_file_folder_id = get_target_test_folder_id(gdrive, __name__, test_download_file.__name__)
    target_file_id = gdrive.list_file(f"'{test_download_file_folder_id}' in parents and title contains 'output.txt'")[0]["id"]
    file = gdrive.download_file(target_file_id)

    # 比較
    assert file["title"] == "output.txt", "ファイル名が一致しません"
    with open(f"{os.environ['WORKING_DIR']}/tests/cases/gdrive_client/download_file/output.txt", "r") as f:
        output = f.read()
    assert file.GetContentString() == output, "ファイル内容が一致しません"


@pytest.fixture
def fixture_create_file():
    """create_file() のfixture"""
    # テスト用入力
    output = {
        "content": "test",
        "title": "output.txt",
        "mimeType": "text/plain",
    }

    # テストしたい処理を実行
    gdrive = GDriveClient()
    test_create_file_folder_id = get_target_test_folder_id(gdrive, __name__, test_create_file.__name__)
    file = gdrive.create_file(
        output["content"],
        output["title"],
        output["mimeType"],
        test_create_file_folder_id
    )

    # 処理結果を取得
    result = {
        "content": file.GetContentString(),
        "title": file["title"],
        "mimeType": file["mimeType"],
    }

    # テストを実行
    yield result, output

    # 後処理
    file.Trash()


def test_create_file(fixture_create_file):
    """create_file() のテスト"""
    # 比較
    result, output = fixture_create_file
    assert result == output, "処理結果が一致しません"


@pytest.fixture
def fixture_rename_file():
    """rename_file() のテスト"""
    # テスト用入力
    output_title = "output.txt"
    output_renamed_title = "renamed_output.txt"

    # テスト用ファイルを作成
    gdrive = GDriveClient()
    test_rename_file_folder_id = get_target_test_folder_id(gdrive, __name__, test_rename_file.__name__)
    file = gdrive.create_file(
        "test content",
        output_title,
        "text/plain",
        test_rename_file_folder_id
    )

    # テストしたい処理を実行
    file = gdrive.rename_file(file["id"], output_renamed_title)

    # 比較
    yield file["title"], output_renamed_title

    # 後処理
    file.Trash()


def test_rename_file(fixture_rename_file):
    """rename_file() のテスト"""
    # 比較
    result, output = fixture_rename_file
    assert result == output, "処理結果が一致しません"


@pytest.fixture
def fixture_test_upload_file():
    """test_upload_file() のfixture"""
    # テスト入力
    output_path = PurePath(os.environ["WORKING_DIR"]) / "tests/cases/gdrive_client/upload_file/output.txt"

    # テストしたい処理を実行
    gdrive = GDriveClient()
    test_upload_file_folder_id = get_target_test_folder_id(gdrive, __name__, test_upload_file.__name__)
    file = gdrive.upload_file(
        str(output_path),
        test_upload_file_folder_id
    )

    # テストを実行
    yield file, output_path

    # 後処理
    file.Trash()


def test_upload_file(fixture_test_upload_file):
    """upload_file() のテスト"""
    file, output_path = fixture_test_upload_file
    assert file["title"] == output_path.name, "ファイル名が一致しません"
    with open(str(output_path), "r") as f:
        output_content = f.read()
    assert file.GetContentString() == output_content, "ファイル内容が一致しません"


@pytest.fixture
def fixture_test_update_file():
    """test_update_file() のfixture"""
    # テスト入力
    output_path = PurePath(os.environ["WORKING_DIR"]) / "tests/cases/gdrive_client/update_file/output.txt"
    update_text = "updated"

    # テスト用ファイルを用意
    gdrive = GDriveClient()
    test_update_file_folder_id = get_target_test_folder_id(gdrive, __name__, test_update_file.__name__)
    file = gdrive.upload_file(
        str(output_path),
        test_update_file_folder_id
    )

    # テストしたい処理を実行
    file = gdrive.update_file(file["id"], update_text)

    # テストを実行
    yield file, output_path, update_text

    # 後処理
    file.Trash()


def test_update_file(fixture_test_update_file):
    """update_file() のテスト"""
    file, output_path, update_text = fixture_test_update_file
    with open(str(output_path), "r") as f:
        output_content = f.read()
    assert file.GetContentString() == update_text, "ファイル内容が一致しません"
