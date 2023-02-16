import os
import asyncio
import pkgutil
from typing import List
from multiprocessing import Process
import typer
from rich.console import Console
from rich.table import Table
from controller.job.typer_callback import job_context_callback
from controller.job.util import Timer
from model.appmodel.job import JobPlan
import job
for _, name, _ in pkgutil.iter_modules([os.path.dirname(job.__file__)]):
    exec(f"from job.{name} import *")

app = typer.Typer()
console = Console()
timer = Timer()


@app.command()
def run(
    job_context: List[str] = typer.Argument(
        ..., help="Job Context",
        callback=job_context_callback
    ),
    workers: int = typer.Option(3, help="Number of workers"),
    verbose: bool = typer.Option(True, help="Verbose mode"),
):
    """
    # Job Context Sample
    > run Job:HelloWorld arg1 arg2 kwarg1=value1 kwarg2=value2
    """
    job_plans: List[JobPlan] = job_context
    jobs = []
    for job_plan in job_plans:
        try:
            jobs.append(eval(job_plan.name)())
        except NameError as e:
            typer.secho(
                f"Job[{job_plan.name}] is not found.",
                fg=typer.colors.RED
            )
            raise typer.Abort()

    if len(jobs) == 0:
        typer.secho("No job is found.", fg=typer.colors.YELLOW)
        raise typer.Abort()

    if workers > len(jobs):
        workers = len(jobs)
        if verbose:
            typer.secho(
                f"Number of workers is greater than number of jobs. "
                f"Number of workers is set to {workers}.",
                fg=typer.colors.YELLOW)

    if workers < 2:
        # Single Process
        for job, job_plan in zip(jobs, job_plans):
            if verbose:
                typer.secho(
                    f"Job[{os.getpid()}-{job.__class__.__name__}] started.",
                    fg=typer.colors.GREEN)
            with timer:
                asyncio.run(job.run(*job_plan.args, **job_plan.kwargs))
    else:
        # Multi Process
        processes = []
        with timer:
            for job, job_plan in zip(jobs, job_plans):
                if len(processes) == workers:
                    for process in processes:
                        process.join()
                    processes = []

                process = Process(
                    target=job.execute,
                    args=job_plan.args,
                    kwargs=job_plan.kwargs,
                )
                process.start()
                processes.append(process)
                if verbose:
                    typer.secho(
                        f"Job[{process.pid}-{job.__class__.__name__}] started.",
                        fg=typer.colors.GREEN)

    if verbose:
        typer.secho(
            f"Total elapsed time: {timer.elapsed:.2f} seconds.",
            fg=typer.colors.GREEN)


@app.command()
def job_info():
    table = Table("Name", "Path")
    for path, name, _ in pkgutil.iter_modules([os.path.dirname(job.__file__)]):
        table.add_row(f"job.{name}", f"{os.path.dirname(job.__file__)}/{name}")
    console.print(table)


if __name__ == "__main__":
    app()
