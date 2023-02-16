from typing import List, Any, Dict
from pydantic import BaseModel, validator


class JobPlan(BaseModel):
    name: str
    args: List[Any]
    kwargs: Dict[str, Any] = {}

    @validator("name")
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