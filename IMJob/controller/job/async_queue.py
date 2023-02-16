import os
import pkgutil
import asyncio
import logging
from traceback import format_exc
from multiprocessing import (
    Queue, Process, current_process
)
from job import Job
import job
for _, name, _ in pkgutil.iter_modules([os.path.dirname(job.__file__)]):
    exec(f"from job.{name} import *")


class SingletonInstance:
    __instance = None

    @classmethod
    def __getInstance(cls, *args, **kwargs):
        # First After
        return cls.__instance

    @classmethod
    def instance(cls, *args, **kwargs):
        # First
        cls.__instance = cls(*args, **kwargs)
        cls.instance = cls.__getInstance
        return cls.__instance


class AsyncQueue(SingletonInstance):

    def __init__(
        self,
        worker_num: int = 3,
        qsize: int = 100
    ):
        self._sem_queue = Queue(maxsize=qsize)
        self._workers = []
        self.set_workers(worker_num=worker_num)

    def add(self, task: Job):
        if not isinstance(task, Job):
            raise RuntimeError(
                f'{task} is not Job Object.')
        self.health_check()
        self._sem_queue.put(task)
        self.health_check()

    @property
    def workers(self):
        return self._workers

    @property
    def q_status(self):
        if self._sem_queue.full():
            return 'full'
        elif self._sem_queue.empty():
            return 'empty'
        else:
            return 'exists'

    def set_workers(self, worker_num: int):
        workers = [
            Process(
                target=self._work,
                args=(self._sem_queue,)
            )
            for _ in range(worker_num)
        ]
        for worker in workers:
            worker.start()
        self._workers = workers

    def health_check(self):
        for idx, worker in enumerate(self._workers):
            if not worker.is_alive():
                logging.warning(
                    f'[WORKER] {worker.name} is Dead, '
                    f'Recovery start...'
                )
                worker.close()
                self._workers[idx] = Process(
                    target=self._work,
                    args=(self._sem_queue,)
                )
                self._workers[idx].start()

    @staticmethod
    def _work(queue: Queue):
        p = current_process()
        worker_prefix = f"[WORKER] ({p.name})"
        logging.info(f"{worker_prefix} Started...")
        while True:
            task = queue.get()
            logging.info(f"{worker_prefix} get task...")
            try:
                asyncio.run(task.run())
            except Exception as e:
                error_msg = format_exc()
                logging.error(f"{worker_prefix} {error_msg}")
                logging.info(f"{worker_prefix} aborted task...")
            else:
                logging.info(f"{worker_prefix} complete task...")


def get_async_queue(*args, **kwargs):
    return AsyncQueue.instance(*args, **kwargs)
