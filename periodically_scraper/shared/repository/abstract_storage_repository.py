from abc import ABC, abstractmethod


class AbstractStorageRepository(object):

    def __init__(self, save_folder: str):
        """
        コンストラクタ

        Parameters
        ----------
        save_folder : str
            保存先フォルダ
        """
        self.save_folder = save_folder

    @abstractmethod
    def save_article(self, html: str, filename: str) -> None:
        """
        記事を保存する

        Parameters
        ----------
        html : str
            記事のHTML文書
        filename : str
            保存ファイル名
        """
        pass

    @abstractmethod
    def get_saved_article_urls(self) -> list:
        """保存済み記事のURLを取得する"""
        pass
