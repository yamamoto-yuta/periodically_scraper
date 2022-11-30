from periodically_scraper.shared.gdrive_client import GDriveClient
from periodically_scraper.shared.repository.abstract_storage_repository import AbstractStorageRepository


class GDriveStorageRepository(AbstractStorageRepository):
    def __init__(self, save_folder: str, gdrive: GDriveClient):
        super().__init__(save_folder)
        self.gdrive = gdrive

    def save_article(self, html: str, filename: str) -> None:
        self.gdrive.create_file(html, filename, "text/html", self.save_folder)

    def get_saved_article_urls(self) -> list:
        article_file_list = self.gdrive.list_file(f"'{self.save_folder}' in parents")
        article_path_list = [article_file["title"] for article_file in article_file_list]
        return article_path_list
