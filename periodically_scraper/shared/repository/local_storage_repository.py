from glob import glob
from pathlib import PurePath

from periodically_scraper.shared.repository.abstract_storage_repository import AbstractStorageRepository


class LocalStorageRepository(AbstractStorageRepository):

    # エスケープする文字の対応辞書
    ORIGIN = 0
    ESCAPED = 1
    ESCAPE_STR_DICT = {
        "/": ("/", "[SLASH]"),
        ":": (":", "[COLON]"),
    }

    def __init_(self, save_folder: str):
        super().__init__(save_folder)

    @classmethod
    def escape_save_path(cls, save_path: str) -> str:
        return save_path \
            .replace(cls.ESCAPE_STR_DICT["/"][cls.ORIGIN], cls.ESCAPE_STR_DICT["/"][cls.ESCAPED]) \
            .replace(cls.ESCAPE_STR_DICT[":"][cls.ORIGIN], cls.ESCAPE_STR_DICT[":"][cls.ESCAPED]) \


    @classmethod
    def restore_save_path(cls, save_path: str) -> str:
        return save_path \
            .replace(cls.ESCAPE_STR_DICT["/"][cls.ESCAPED], cls.ESCAPE_STR_DICT["/"][cls.ORIGIN]) \
            .replace(cls.ESCAPE_STR_DICT[":"][cls.ESCAPED], cls.ESCAPE_STR_DICT[":"][cls.ORIGIN]) \


    def save_article(self, html: str, filename: str) -> None:
        save_path = f"{self.save_folder}/{self.escape_save_path(filename)}"
        with open(save_path, "w") as f:
            f.write(html)

    def get_saved_article_urls(self) -> list:
        article_path_list = sorted(glob(f"{self.save_folder}/*"))
        article_url_list = [self.restore_save_path(PurePath(article_path).name) for article_path in article_path_list]
        return article_url_list
