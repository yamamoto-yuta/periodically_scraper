import os
from http import HTTPStatus
import time
import random

from bs4 import BeautifulSoup

from periodically_scraper.shared import scraping_tools
from ..shared.repository.abstract_storage_repository import AbstractStorageRepository
from periodically_scraper.shared.slack_client import slack
from periodically_scraper.shared.gdrive_client import GDriveClient
from periodically_scraper.shared.gdrive_logger import GDriveLogger


class NewsSite1Scraper:
    """
    ニュースサイト1をスクレイピングするクラス
    Attributes
    ----------
    BASE_URL : str
        サイトURL
    """

    # ドメイン
    BASE_URL = "https://www.news-site-1.com"
    # 記事一覧ページURLのテンプレート
    def page_url_template(self, page_count: int): return f"{self.BASE_URL}/page/{page_count}"

    @classmethod
    def get_gdrive_save_folder_id(cls, html_folder_id: str, gdrive: GDriveClient) -> str:
        """
        GDriveに保存するフォルダのIDを取得する

        Parameters
        ----------
        html_folder_id : str
            HTMLフォルダのID
        gdrive : GDriveClient
            GDriveクライアント

        Returns
        -------
        str
            GDriveに保存するフォルダのID
        """
        save_folder_id = gdrive.list_file(f"'{html_folder_id}' in parents and title contains '{cls.BASE_URL}'")[0]["id"]
        return save_folder_id

    def __init__(self, logger: GDriveLogger, storage_repository: AbstractStorageRepository) -> None:
        """
        コンストラクタ
        """
        self.logger = logger
        self.storage_repository = storage_repository

    def execute(self) -> None:
        """
        スクレイピングを実行する
        """
        # 開始ログを出力する
        log_msg = f"Start scraping: {self.BASE_URL}"
        self.logger.info(log_msg)
        slack.post_message(log_msg)

        # 記事一覧ページのHTMLを取得する
        url = self.page_url_template(page_count=1)
        self.logger.info(f"Scraping article list page: {url} ")
        html, http_status = scraping_tools.get_html(url)
        if http_status != HTTPStatus.OK:
            log_msg = f"Failed to get HTML: url={url}, http_status={http_status}"
            self.logger.log.error(log_msg)
            slack.post_message(log_msg)
            return

        # 最終ページのページカウントを取得
        last_page_count = self._get_last_page_count(html)
        log_msg = f"Get last page count: {last_page_count}"
        self.logger.info(log_msg)
        slack.post_message(log_msg)

        for page_count in range(1, last_page_count + 1):
            # 現在の記事一覧ページのページ数をログへ出力する
            log_msg = f"Scraping page: {page_count} / {last_page_count}"
            self.logger.info(log_msg)
            slack.post_message(log_msg)

            # 記事一覧ページのHTMLを取得する
            url = self.page_url_template(page_count)
            self.logger.info(f"Scraping article list page: {url} ")
            html, http_status = scraping_tools.get_html(url)
            if http_status != HTTPStatus.OK:
                log_msg = f"Failed to get HTML: url={url}, http_status={http_status}"
                self.logger.log.error(log_msg)
                slack.post_message(log_msg)
                return

            # 記事一覧ページから記事本文ページへのリンクを抽出する
            article_url_list = self._extract_article_page_urls(html)
            self.logger.info(f"Get article page urls: {len(article_url_list)} articles")

            # 保存済みの記事のURLを取得する
            saved_article_url_list = self._get_saved_article_urls()
            self.logger.info(f"Get saved article urls: {len(saved_article_url_list)} articles")

            # 保存済みの記事のURLを除外する
            new_article_url_list = self._drop_saved_articles(article_url_list, saved_article_url_list)
            self.logger.info(f"Drop saved articles: Drop {len(article_url_list) - len(new_article_url_list)} articles")
            slack.post_message(f"Save articles in this page: {len(new_article_url_list)} articles")

            # そのページの全ての記事が既に保存済みだったら、処理終了
            if len(new_article_url_list) == 0:
                self.logger.info("All articles are saved. Break scraping.")
                break

            # 未保存の記事をスクレイピングして保存する
            self.logger.info(f"Start new articles scraping...")
            for article_url in new_article_url_list:
                # 記事本文ページのHTMLを取得する
                self.logger.info(f"Scraping article page: {article_url}")
                html, http_status = scraping_tools.get_html(article_url)
                if http_status != HTTPStatus.OK:
                    log_msg = f"Failed to get HTML: url={article_url}, http_status={http_status}"
                    self.logger.log.error(log_msg)
                    slack.post_message(log_msg)
                    continue

                # 容量削減のため、main要素のみを抽出する
                self.logger.info(f"Extract main element from HTML")
                main_html = self._extract_main_element(html)

                # 記事を保存する
                self._save_article(main_html, article_url)
                self.logger.info(f"Saved article")

        # 終了ログを出力する
        log_msg = "Finish scraping."
        self.logger.info(log_msg)
        slack.post_message(log_msg)

    def _extract_article_page_urls(self, html: str) -> list:
        """
        記事一覧ページから記事本文ページへのリンクを抽出する
        Parameters
        ----------
        html : str
            記事一覧ページのHTML文書

        Returns
        -------
        list
            記事本文ページへのリンクのリスト
        """
        soup = BeautifulSoup(html, "lxml")
        main_html = soup.find("main")
        article_url_list = [f"{self.BASE_URL}{article_html.find('a').get('href')}" for article_html in main_html.find_all("article")]
        return article_url_list

    def _save_article(self, html: str, url: str) -> None:
        """
        記事を保存する

        Parameters
        ----------
        html : str
            記事のHTML文書
        url : str
            記事のURL
        """
        self.storage_repository.save_article(html, url)

    def _get_saved_article_urls(self) -> list:
        """
        保存済み記事のURLを取得する

        Returns
        -------
        list
            保存済み記事のURLのリスト
        """
        saved_article_url_list = sorted(self.storage_repository.get_saved_article_urls())
        return saved_article_url_list

    def _drop_saved_articles(self, current_article_list: list, saved_article_list: list) -> list:
        """
        保存済みの記事を除外する

        Parameters
        ----------
        current_article_list : list
            現在の記事のリスト
        saved_article_list : list
            保存済みの記事のリスト

        Returns
        -------
        list
            除外済みの記事のリスト
        """
        return list(set(current_article_list) - set(saved_article_list))

    def _get_last_page_count(self, html: str) -> int:
        """
        最終ページ番号を取得する
        Parameters
        ----------
        html : str
            記事一覧ページのHTML文書

        Returns
        -------
        int
            最終ページ番号
        """
        PAGE_COUNT_POS = -2  # ページ番号の位置
        soup = BeautifulSoup(html, "lxml")
        last_page_count = int(soup.find("a", class_="pagenavi-item pagenavi-item--last").get("href").split("/")[PAGE_COUNT_POS])
        return last_page_count

    def _extract_main_element(self, html: str) -> str:
        """
        メイン要素を抽出する
        Parameters
        ----------
        html : str
            記事一覧ページのHTML文書

        Returns
        -------
        str
            メイン要素
        """
        soup = BeautifulSoup(html, "lxml")
        main_html = str(soup.find("main"))
        return main_html
