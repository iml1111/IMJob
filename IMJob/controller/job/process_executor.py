import os
from multiprocessing import Queue
import typer
from typing import List
from controller.job.async_queue import create_consumers
from model.appmodel.job_plan import JobPlan
from controller.job.util import Timer


def single_process(
    job_plans: List[JobPlan],
    timer: Timer,
    verbose: bool = True,
):
    for plan in job_plans:
        if verbose:
            typer.secho(
                f"[Worker-{os.getpid()}] started Job[{plan.name}].",
                fg=typer.colors.GREEN)
        with timer:
            plan.job.execute(*plan.args, **plan.kwargs)


def multi_process(
    workers: int,
    job_plans: List[JobPlan],
    timer: Timer,
    verbose: bool = True,
):
    q = Queue()
    for plan in job_plans:
        q.put(plan)
    for _ in range(workers):
        q.put(None)
    with timer:
        consumers = create_consumers(q, workers, verbose)
        for consumer in consumers:
            consumer.join()
