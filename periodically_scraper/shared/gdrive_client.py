import os
from pathlib import PurePath

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from pydrive2.files import GoogleDriveFile
from oauth2client.service_account import ServiceAccountCredentials


class GDriveClient:
    """Googleドライブを操作するクライアント
    """

    def __init__(self) -> None:
        """コンストラクタ"""
        gauth = GoogleAuth()
        scope = ["https://www.googleapis.com/auth/drive"]
        gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(os.environ["SA_KEY_FILE"], scope)
        self.drive = GoogleDrive(gauth)

    def list_file(self, q: str, trashed: bool = False) -> list:
        """
        ファイルリストを取得するメソッド

        Parameters
        ----------
        q : str
            クエリ
            クエリに使用できる条件、命令は次を参照：
            - https://developers.google.com/drive/api/guides/ref-search-terms
        trashed : bool, default False
            ゴミ箱に入っているファイルを含めるかどうか


        Returns
        -------
        list
            ファイルリスト
        """
        return self.drive.ListFile({'q': f"{q} and trashed = {trashed}"}).GetList()

    def create_file(self, contents: str, file_name: str, mimeType: str, folder_id: str) -> GoogleDriveFile:
        """
        指定したフォルダにファイルを作成するメソッド

        Parameters
        ----------
        contents : str
            作成するファイルのコンテンツ
        file_name : str
            作成するファイルの名前
        mimeType : str
            作成するファイルのMIMEタイプ
        folder_id : str
            作成先のフォルダのID

        Returns
        -------
        GoogleDriveFile
            ファイル
        """
        file = self.drive.CreateFile({
            "title": file_name,
            "mimeType": mimeType,
            "parents": [{"id": folder_id}]
        })
        file.SetContentString(contents)
        file.Upload()
        return file

    def upload_file(self, file_path: str, folder_id: str) -> GoogleDriveFile:
        """
        指定したフォルダにファイルをアップロードするメソッド

        Parameters
        ----------
        file_path : str
            アップロードするファイルのパス
        folder_id : str
            アップロード先のフォルダのID

        Returns
        -------
        GoogleDriveFile
            ファイル
        """
        # アップロード
        file = self.drive.CreateFile({"parents": [{"id": folder_id}]})
        file.SetContentFile(file_path)
        file.Upload()
        # そのままだとファイルパスがファイル名になっているので、ローカルのファイル名へ変更する
        file = self.rename_file(file["id"], PurePath(file_path).name)
        return file

    def download_file(self, file_id: str) -> GoogleDriveFile:
        """
        指定したファイルをダウンロードするメソッド

        Parameters
        ----------
        file_id : str
            ダウンロードするファイルのID

        Returns
        -------
        GoogleDriveFile
            ファイル
        """
        return self.drive.CreateFile({"id": file_id})

    def rename_file(self, file_id: str, new_name: str) -> GoogleDriveFile:
        """
        指定したファイルの名前を変更するメソッド

        Parameters
        ----------
        file_id : str
            変更するファイルのID
        new_name : str
            変更後の名前

        Returns
        -------
        GoogleDriveFile
            ファイル
        """
        # ファイル名を変更してアップロード
        file = self.download_file(file_id)
        file.FetchMetadata()  # メタデータを最新の状態へ更新
        file["title"] = new_name
        file.Upload()
        return file

    def update_file(self, file_id: str, contents: str) -> GoogleDriveFile:
        """
        指定したファイルを更新するメソッド
        Parameters
        ----------
        file_id : str
            更新するファイルのID
        contents : str
            更新後のコンテンツ

        Returns
        -------
        GoogleDriveFile
            ファイル
        """
        file = self.drive.CreateFile({"id": file_id})
        file.SetContentString(contents)
        file.Upload()
        return file
