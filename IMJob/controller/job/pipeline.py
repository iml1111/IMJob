from typing import List
from job import Job
from controller.job.exception import IsNotJob
from job.hello import HelloWorld


class JobPipeline:

    def __init__(self, jobs: List[Job]):
        self.jobs = jobs
        for job in self.jobs:
            if job.__class__.__bases__[0] is not Job:
                raise IsNotJob()
        self.iter_index = 0

    def __truediv__(self, other: int):
        if not isinstance(other, int):
            raise TypeError("other must be int")
        if other > len(self.jobs):
            return self
        return [
            JobPipeline(self.jobs[i: i + other])
            for i in range(0, len(self.jobs), other)
        ]

    def __repr__(self):
        return f"JobPipeline({self.jobs})"

    def __next__(self):
        if self.iter_index >= len(self.jobs):
            raise StopIteration
        self.iter_index += 1
        return self.jobs[self.iter_index - 1]

    def __iter__(self):
        self.iter_index = 0
        return self


if __name__ == "__main__":
    p = JobPipeline([HelloWorld(), HelloWorld(), HelloWorld(), HelloWorld()])