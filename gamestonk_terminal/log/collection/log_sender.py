# IMPORTATION STANDARD
from copy import deepcopy
from threading import Thread
from queue import SimpleQueue
from pathlib import Path

# IMPORTATION THIRDPARTY

# IMPORTATION INTERNAL
from gamestonk_terminal.feature_flags import LOG_COLLECTION
from gamestonk_terminal.log.constants import (
    ARCHIVES_FOLDER_NAME,
    S3_FOLDER_SUFFIX,
    TMP_FOLDER_NAME,
)
from gamestonk_terminal.log.collection.s3_sender import send_to_s3
from gamestonk_terminal.log.generation.settings import Settings

# DO NOT USE THE FILE LOGGER IN THIS MODULE


class QueueItem:
    @property
    def path(self) -> Path:
        return self.__path

    @property
    def last(self) -> bool:
        return self.__last

    def __init__(self, path: Path, last: bool = False):
        self.__path = path
        self.__last = last

    def __str__(self):
        return "{" + f'"last": {self.last}, "path": {self.path}' + "}"


class LogSender(Thread):
    MAX_FAILS = 3

    @staticmethod
    def start_required() -> bool:
        """Check if it makes sense to start a LogsSender instance ."""

        return LOG_COLLECTION

    @property
    def settings(self) -> Settings:
        return deepcopy(self.__settings)

    @property
    def fails(self) -> int:
        return self.__fails

    @property
    def queue(self) -> SimpleQueue:
        return self.__queue

    # OVERRIDE
    def run(self):
        settings = self.__settings
        app_settings = settings.app_settings
        aws_settings = settings.aws_settings
        queue = self.__queue

        app_name = app_settings.name
        identifier = app_settings.identifier

        while True:
            item: QueueItem = queue.get()
            file = item.path
            last = item.last

            if self.check_sending_conditions():
                archives_file = file.parent / ARCHIVES_FOLDER_NAME / f"{file.stem}.log"
                object_key = (
                    f"{app_name}{S3_FOLDER_SUFFIX}/logs/{identifier}/{file.stem}.log"
                )
                tmp_file = file.parent / TMP_FOLDER_NAME / f"{file.stem}.log"

                try:
                    send_to_s3(
                        archives_file=archives_file,
                        aws_settings=aws_settings,
                        file=file,
                        object_key=object_key,
                        tmp_file=tmp_file,
                        copy=last,
                    )
                except Exception:
                    self.fails_increment()
                finally:
                    self.fails_reset()

            if last:
                break

    # OVERRIDE
    def __init__(
        self,
        settings: Settings,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.__settings = settings

        self.__fails: int = 0  # type: ignore
        self.__queue: SimpleQueue = SimpleQueue()

    def check_sending_conditions(self):
        """Check if the condition are met to send data."""

        return self.start_required() and not self.max_fails_reached()

    def fails_increment(self):
        self.__fails += 1

    def fails_reset(self):
        self.__fails = 0

    def max_fails_reached(self) -> bool:
        return self.__fails > self.MAX_FAILS

    def send_path(self, path: Path, last: bool = False):
        """Only closed files should be sent."""

        queue = self.__queue
        queue.put(QueueItem(path=path, last=last))
