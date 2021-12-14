import logging
from datetime import datetime
from typing import Optional


class Logger:

    def __init__(self, date: Optional[datetime] = None) -> None:
        self.date = date if date else datetime.now().strftime("%y%m%d")
        self._setup_logging()

    def _setup_logging(self) -> None:
        logging.basicConfig(level=logging.DEBUG,
                            format="%(asctime)s %(levelname)s %(name)s %(message)s",
                            datefmt='%m-%d %H:%M',
                            filename=f"{self.date}.log")

    def __call__(self, msg: str) -> None:
        print(logging.info(msg))
