import os
import asyncio
import pkgutil
from typing import List
from multiprocessing import Process
import subprocess
import typer
from controller.job.typer_callback import job_context_callback
from model.appmodel.job import JobPlan
import job
for _, name, _ in pkgutil.iter_modules([os.path.dirname(job.__file__)]):
    exec(f"from job.{name} import *")


app = typer.Typer()


@app.command()
def run(
    job_context: List[str] = typer.Argument(
        ..., help="Job Context",
        callback=job_context_callback
    ),
    workers: int = typer.Option(3, help="Number of workers")
):
    job_plans: List[JobPlan] = job_context
    # TODO: 존재하지 않는 잡 예외처리
    jobs = [eval(job_plan.name)() for job_plan in job_plans]

    if workers > len(jobs):
        workers = len(jobs)
        typer.secho(
            f"Number of workers is greater than number of jobs. "
            f"Number of workers is set to {workers}.",
            fg=typer.colors.YELLOW
        )

    if workers < 2:
        # Single Process
        for job, job_plan in zip(jobs, job_plans):
            asyncio.run(job.run(*job_plan.args, **job_plan.kwargs))
    else:
        # Multi Process
        processes = []
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
            typer.secho(f"Process {process.pid} started.", fg=typer.colors.GREEN)
            processes.append(process)


@app.command()
def job_info():
    typer.echo("Hello World")


if __name__ == "__main__":
    app()
