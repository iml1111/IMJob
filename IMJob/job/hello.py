from job import Job
import time
from loguru import logger
from controller.job.util import convert_param


class HelloWorld(Job):

    async def run(self, name: str = 'IML'):
        logger.info(f"Hello World and {name}!")
        logger.info(f"It's {self.settings.app_name}!")


class SlowWork(Job):

    async def run(self, sec: int = 1):
        sec, ok = convert_param(sec, int)
        if not ok:
            raise ValueError(f"Invalid param: sec={sec}")
        time.sleep(sec)
        logger.info(f"Slow Work {sec}!")


class BadWork(Job):

    async def run(self):
        1 / 0


if __name__ == "__main__":
    pass
