#!/usr/bin/env python
import os
import sys
import pkgutil
from typing import List
import typer
from loguru import logger
from rich.console import Console
from rich.table import Table
from controller.job.typer_callback import job_context_callback, worker_count_callback
from controller.job.util import Timer
from controller.job.process_executor import single_process, multi_process
from model.appmodel.job_plan import JobPlan
from settings import Settings
import job
for _, name, _ in pkgutil.iter_modules([os.path.dirname(job.__file__)]):
    exec(f"from job.{name} import *")


app = typer.Typer(
    pretty_exceptions_short=False,
    # Check before release
    pretty_exceptions_enable=os.getenv(
        "TYPER_PRETTY_EXCEPTIONS", "True"
    ) == "True",
)
console = Console()
job_timer = Timer()

logger_format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>|"
    "<level>{level: <8}</level>|"
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan>|"
    " <level>{message}</level>"
)
logger.remove()
logger.add(
    sys.stdout, 
    format=logger_format, 
    filter= lambda x: x["level"].name != "ERROR"
)
logger.add(sys.stderr, format=logger_format, level="ERROR")


@app.command()
def run(
    job_context: List[str] = typer.Argument(
        ..., help="Job Context",
        callback=job_context_callback
    ),
    workers: int = typer.Option(
        0, help="Number of workers, (0=auto)",
        callback=worker_count_callback
    ),
    verbose: bool = typer.Option(True, help="Verbose mode"),
    timer: bool = typer.Option(True, help="Timer mode"),
):
    """
    # Job Context Sample
    > run Job:HelloWorld arg1 arg2 kwarg1=value1 kwarg2=value2
    """
    job_plans: List[JobPlan] = job_context
    settings = Settings()
    for plan in job_plans:
        try:
            plan.job = eval(plan.name)(settings)
        except NameError as e:
            logger.error(f"Job[{plan.name}] is not found.")
            raise typer.Abort()

    if len(job_plans) == 0:
        logger.error("No job is found.")
        raise typer.Abort()

    if workers > len(job_plans):
        if verbose:
            logger.opt(colors=True).info(
                f"<yellow>workers({workers})</yellow> is greater than number of jobs. "
                f"<yellow>Set to {len(job_plans)}</yellow>."
            )
        workers = len(job_plans)

    job_timer.enabled = timer
    if workers < 2:
        single_process(job_plans, job_timer, verbose)
    else:
        multi_process(workers, job_plans, job_timer, verbose)

    if verbose and timer:
        logger.opt(colors=True).info(
            "Total elapsed time: "
            f"<blue>{job_timer.elapsed:.3f} seconds</blue>.",
        )


@app.command()
def job_info():
    table = Table("Name", "Path")
    for path, name, _ in pkgutil.iter_modules([os.path.dirname(job.__file__)]):
        table.add_row(f"job.{name}", f"{os.path.dirname(job.__file__)}/{name}")
    console.print(table)


if __name__ == "__main__":
    app()
