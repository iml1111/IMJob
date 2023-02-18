import os
from traceback import format_exc
import typer
from multiprocessing import (
    Queue, Process, current_process
)
from model.appmodel.job_plan import JobPlan

GR = typer.colors.GREEN
RED = typer.colors.RED


def consumer(q: Queue, verbose: bool = True):
    p = current_process()
    prefix = f"[{p.name}-{os.getpid()}]"
    if verbose:
        typer.secho(f"{prefix} started...", fg=GR)
    while True:
        plan: JobPlan = q.get()
        if plan is None:
            if verbose:
                typer.secho(f"{prefix} turn off...", fg=GR)
            break
        if verbose:
            typer.secho(f"{prefix} get Job[{plan.name}].", fg=GR)
        try:
            plan.job.execute(*plan.args, **plan.kwargs)
        except Exception as e:
            error_msg = format_exc()
            typer.secho(f"{prefix} {error_msg}", fg=RED)
            typer.secho(f"{prefix} aborted Job[{plan.name}].", fg=RED)
        else:
            if verbose:
                typer.secho(f"{prefix} complete Job[{plan.name}].", fg=GR)


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
