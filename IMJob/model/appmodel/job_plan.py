from typing import List, Any, Dict, Type, Optional
from pydantic import BaseModel, field_validator
from job import Job


class JobPlan(BaseModel):
    name: str
    args: List[Any]
    kwargs: Dict[str, Any] = {}
    job: Optional[Type[Job]] = None

    @field_validator("name")
    @classmethod
    def name_valid(cls, name: str):
        if name.startswith("Job:"):
            name = name[4:]
        return name


if __name__ == "__main__":
    j = JobPlan(name="Job:HelloWorld", args=["IML"], kwargs_str=["name=IML"])
    print(j)
    print(j.name)
    print(j.args)
    print(j.kwargs)