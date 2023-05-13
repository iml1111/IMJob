from typing import List
from typer import BadParameter
from controller.job.worker_count import get_worker_count
from model.appmodel.job_plan import JobPlan


def job_context_callback(job_context: List[str]) -> List[JobPlan]:
    if not job_context[0].startswith("Job:"):
        raise BadParameter("Job Context must not start with 'Job:'")

    job_name, job_args, job_kwargs = None, [], {}
    job_requests = []

    for ctx in job_context:
        if ctx.startswith("Job:"):
            if job_name is not None:
                job_requests.append(
                    JobPlan(
                        name=job_name,
                        args=job_args,
                        kwargs=job_kwargs))
            job_name = ctx[4:]
            job_args, job_kwargs = [], {}
        elif "=" in ctx:
            values = ctx.split("=")
            if len(values) != 2:
                raise ValueError("kwargs must be in the format of key=value")
            key, value = values
            job_kwargs[key] = value
        else:
            job_args.append(ctx)

    job_requests.append(
        JobPlan(
            name=job_name,
            args=job_args,
            kwargs=job_kwargs))

    return job_requests


def worker_count_callback(workers: int) -> int:
    if workers == 0:
        workers = get_worker_count()
    return workers
