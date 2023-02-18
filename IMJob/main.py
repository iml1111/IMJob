import os
import pkgutil
from typing import List
import typer
from rich.console import Console
from rich.table import Table
from controller.job.typer_callback import job_context_callback
from controller.job.util import Timer
from controller.job.process_executor import single_process, multi_process
from model.appmodel.job_plan import JobPlan
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
    for plan in job_plans:
        try:
            plan.job = eval(plan.name)()
        except NameError as e:
            typer.secho(
                f"Job[{plan.name}] is not found.",
                fg=typer.colors.RED)
            raise typer.Abort()

    if len(job_plans) == 0:
        typer.secho("No job is found.", fg=typer.colors.YELLOW)
        raise typer.Abort()

    if workers > len(job_plans):
        workers = len(job_plans)
        if verbose:
            typer.secho(
                f"Number of workers is greater than number of jobs. "
                f"Number of workers is set to {workers}.",
                fg=typer.colors.YELLOW)

    if workers < 2:
        single_process(job_plans, timer, verbose)
    else:
        multi_process(workers, job_plans, timer)

    if verbose:
        typer.secho(
            "Total elapsed time: "
            f"{timer.elapsed:.3f} seconds.",
            fg=typer.colors.GREEN)


@app.command()
def job_info():
    table = Table("Name", "Path")
    for path, name, _ in pkgutil.iter_modules([os.path.dirname(job.__file__)]):
        table.add_row(f"job.{name}", f"{os.path.dirname(job.__file__)}/{name}")
    console.print(table)


if __name__ == "__main__":
    app()
