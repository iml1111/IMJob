import os
from traceback import format_exc
from loguru import logger
from multiprocessing import (
    Queue, Process, current_process
)
from model.appmodel.job_plan import JobPlan


def consumer(q: Queue, verbose: bool = True):
    p = current_process()
    prefix = f"[{p.name}-{os.getpid()}]"
    if verbose:
        logger.opt(colors=True).info(
            f"<green>{prefix} started...</green>")
    while True:
        plan: JobPlan = q.get()
        if plan is None:
            if verbose:
                logger.opt(colors=True).info(
                    f"<green>{prefix} turn off...</green>")
            break
        if verbose:
            logger.opt(colors=True).info(
                f"<green>{prefix} start Job[{plan.name}]</green>")
        try:
            plan.job.execute(*plan.args, **plan.kwargs)
        except Exception as e:
            error_msg = format_exc()
            logger.error(f"{prefix} {error_msg}")
            logger.error(f"{prefix} aborted Job[{plan.name}].")
        else:
            if verbose:
                logger.opt(colors=True).info(
                    f"<green>{prefix} complete Job[{plan.name}].</green>")


def create_consumers(q: Queue, num_workers: int, verbose: bool = True):
    workers = []
    for i in range(num_workers):
        worker = Process(
            target=consumer,
            args=(q, verbose),
            name=f"Worker-{i}"
        )
        worker.start()
        workers.append(worker)
    return workers
