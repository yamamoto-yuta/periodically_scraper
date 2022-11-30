import os

from periodically_scraper.shared.gdrive_client import GDriveClient


def get_target_test_folder_id(gdrive: GDriveClient, module_name: str, method_name: str) -> str:
    """テスト用フォルダのIDを取得する

    Parameters
    ----------
    gdrive : GDriveClient
        GDriveClientのインスタンス
    module_name : str
        テスト対象のモジュール名
    method_name : str
        テスト対象のメソッド名

    Returns
    -------
    str
        テスト用フォルダのID
    """
    test_root_folder_id = os.environ["TEST_FOLDER_ID"]
    test_module_folder_id = gdrive.list_file(f"'{test_root_folder_id}' in parents and title contains '{module_name}'")[0]["id"]
    target_test_folder_id = gdrive.list_file(f"'{test_module_folder_id}' in parents and title contains '{method_name}'")[0]["id"]
    return target_test_folder_id
