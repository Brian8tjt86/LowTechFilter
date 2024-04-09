import signal
from typing import Dict

import httpx
import arrow
from base64 import b64encode
import pathlib
import logging
import asyncio
from zipfile import ZipFile
from io import BytesIO

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Downloader:
    def __init__(self):
        self.base_url = (
            "https://www.whoisds.com//whois-database/newly-registered-domains/{args}/nrd"
        )
        self.base_path = pathlib.Path("nrd")
        self.data: Dict[str, BytesIO] = {}
        if not self.base_path.exists():
            self.base_path.mkdir()

    async def fetch(self, date: arrow.Arrow) -> bool:
        logger.info("Downloading: %s", date.format("YYYY-MM-DD"))
        url = self.base_url.format(
            args=b64encode(date.strftime("%Y-%m-%d.zip").encode()).decode()
        )
        print(url)
        # me https://www.whoisds.com//whois-database/newly-registered-domains/MjAyNC0wNC0wOS56aXA=/nrd
        # th https://www.whoisds.com//whois-database/newly-registered-domains/MjAyNC0wNC0wOC56aXA=/nrd
        # assert url == "https://www.whoisds.com//whois-database/newly-registered-domains/MjAyNC0wNC0wOC56aXA=/nrd"
        async with httpx.AsyncClient() as client:
            r = await client.get(url)
            if r.status_code != 200:
                logger.error("Download failed: %s", url)
                return False
            self.data[date.format("YYYY-MM-DD")] = BytesIO(r.content)
            return True

    async def write(self):
        # todo: extract zip file and write to disk
        pass
        # date = sorted(self.data.keys(), reverse=True)
        # for d in date:
        #     f = self.data[d]
        #     ZipFile(f).extractall(self.base_path / d)

    def run(self):
        loop = asyncio.get_event_loop()
        loop.add_signal_handler(signal.SIGILL, loop.stop)
        loop.add_signal_handler(signal.SIGINT, loop.stop)
        today = arrow.utcnow()
        task = []

        for i in range(1, 8):
            date = today.shift(days=-i)
            task.append(loop.create_task(self.fetch(date)))
        loop.run_until_complete(asyncio.gather(*task))
        asyncio.run(self.write())


if __name__ == "__main__":
    Downloader().run()