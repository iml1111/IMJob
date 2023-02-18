import asyncio
from abc import ABCMeta, abstractmethod
import inspect


class Job(metaclass=ABCMeta):

    def __new__(cls, *arg, **kwargs):
        parent_coros = inspect.getmembers(Job, predicate=inspect.iscoroutinefunction)

        # check if parent's coros are still coros in a child
        for coro in parent_coros:
            child_method = getattr(cls, coro[0])
            if not inspect.iscoroutinefunction(child_method):
                raise RuntimeError('The method %s must be a coroutine' % (child_method,))

        return super(Job, cls).__new__(cls, *arg, **kwargs)

    @abstractmethod
    async def run(self, *args, **kwargs):
        pass

    def execute(self, *args, **kwargs):
        return asyncio.run(self.run(*args, **kwargs))
