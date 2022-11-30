import os
from pathlib import Path

from classopt import classopt, config

from periodically_scraper.shared.const import storage_type
from periodically_scraper.shared.gdrive_client import GDriveClient
from periodically_scraper.shared.gdrive_logger import GDriveLogger
from periodically_scraper.shared.slack_client import slack
from periodically_scraper.shared.repository.gdrive_storage_repository import GDriveStorageRepository
from periodically_scraper.shared.repository.local_storage_repository import LocalStorageRepository
from periodically_scraper.services.news_site_1_scraper import NewsSite1Scraper


if __name__ == "__main__":
    # 引数を設定
    @classopt(default_long=True, default_short=True)
    class Args:
        save_folder: str = config(
            help="Save article folder (default: 'gdrive')",
            default=storage_type.GDRIVE,
        )

    args = Args.from_args()

    try:
        # GDriveClientインスタンスを作成
        gdrive = GDriveClient()

        # ストレージを設定
        if args.save_folder == storage_type.GDRIVE:
            # GDriveLoggerインスタンスを作成
            logger = GDriveLogger(gdrive)
            logger.initialize()

            # StorageRepositoryインスタンスを作成
            save_folder = NewsSite1Scraper.get_gdrive_save_folder_id(os.environ["HTML_FOLDER_ID"], gdrive)
            storage_repository: GDriveStorageRepository = GDriveStorageRepository(save_folder, gdrive)

        else:
            # GDriveLoggerインスタンスを作成
            logger = GDriveLogger(gdrive, use_gdrive=False)

            # StorageRepositoryインスタンスを作成
            save_folder = Path(args.save_folder)
            if save_folder.exists() == False:
                raise Exception(f"Save folder '{save_folder}' does not exist.")
            if save_folder.is_dir() == False:
                raise Exception(f"Save folder '{save_folder}' is not directory.")
            storage_repository = LocalStorageRepository(save_folder=args.save_folder)

        # スクレイピングを実行
        news_site_1_scraper = NewsSite1Scraper(
            logger,
            storage_repository,
        )
        news_site_1_scraper.execute()
    except:
        slack.post_error()
