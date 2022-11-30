import os
import json
import logging
from logging import config
import datetime
from typing import Optional
from pathlib import Path

import pytz
from pydrive2.files import GoogleDriveFile

from periodically_scraper.shared.gdrive_client import GDriveClient


class GDriveLogger(object):
    """
    ロガークラス

    Attributes
    ----------
    log_config: dict
        ロギングの環境設定
    log : logging.Logger
        ロガー
    gdrive : GDriveClient
        GDriveClientインスタンス
    log_folder_id : str
        Googleドライブでログファイルを格納するフォルダのID
    log_file_id : str
        GoogleドライブのログファイルのID
    """

    def __init__(self, gdrive: GDriveClient, log_folder_id: Optional[str] = None, use_gdrive: bool = True) -> None:
        """
        コンストラクタ

        Parameters
        ----------
        gdrive : GDriveClient
            GDriveClientインスタンス
        log_folder_id : Optional[str], optional
            ログファイルを格納するGoogleドライブのフォルダID, by default None
        use_gdrive : bool, optional
            Googleドライブにログファイルを保存するかどうか, by default True
        """

        # 設定ファイルを読み込み
        with open(f'{os.environ["WORKING_DIR"]}/log_config.json', "r") as f:
            self.log_config = json.load(f)

        # 既存のローカルログファイルが存在する場合は削除
        local_log_filepath = os.environ["WORKING_DIR"] + "/" + self.log_config["handlers"]["fileHandler"]["filename"]
        if Path(local_log_filepath).exists():
            os.remove(local_log_filepath)

        # 設定を適用
        config.dictConfig(self.log_config)

        self.log = logging.getLogger("file_logger")
        self.gdrive = gdrive
        self.log_folder_id = log_folder_id if log_folder_id is not None else os.environ["LOG_FOLDER_ID"]
        self.log_file_id = None
        self.use_gdrive = use_gdrive

    def initialize(self, log_filename: Optional[str] = None) -> Optional[GoogleDriveFile]:
        """
        初期化

        Parameters
        ----------
        log_filename : Optional[str], optional
            ログファイル名, by default None

        Returns
        -------
        GoogleDriveFile
            Googleドライブで作成したログファイルのGoogleDriveFileインスタンス
        """
        # Googleドライブを使わない場合、何もしない
        if self.use_gdrive == False:
            return None

        # Googleドライブに新しくログファイルを作成
        if log_filename is None:
            dt_now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
            log_filename = dt_now.strftime("%Y-%m-%d-%H-%M-%S-%f") + ".log"
        file = self.gdrive.create_file(
            "",
            log_filename,
            "text/plane",
            self.log_folder_id
        )
        self.log_file_id = file["id"]
        return file

    def info(self, msg: str) -> GoogleDriveFile:
        """
        infoログを出力する

        Parameters
        ----------
        msg : str
            ログメッセージ

        Returns
        -------
        GoogleDriveFile
            GoogleドライブのログファイルのGoogleDriveFileインスタンス
        """
        self.log.info(msg)
        return self.__update_gdrive_log_file()

    def error(self, msg: str) -> GoogleDriveFile:
        """
        errorログを出力する

        Parameters
        ----------
        msg : str
            ログメッセージ

        Returns
        -------
        GoogleDriveFile
            GoogleドライブのログファイルのGoogleDriveFileインスタンス
        """
        self.log.error(msg)
        return self.__update_gdrive_log_file()

    def __update_gdrive_log_file(self) -> Optional[GoogleDriveFile]:
        """
        Googleドライブのログファイルを更新する

        Returns
        -------
        GoogleDriveFile
            GoogleドライブのログファイルのGoogleDriveFileインスタンス
        """
        # Googleドライブを使わない場合、何もしない
        if self.use_gdrive == False:
            return None

        # ログファイルを更新
        with open(os.environ["WORKING_DIR"] + "/" + self.log_config["handlers"]["fileHandler"]["filename"], "r") as f:
            log_content = f.read()
        return self.gdrive.update_file(self.log_file_id, log_content)
