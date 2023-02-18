# IMJob
Boilerplate for Scalable Python Job Workers

## Feature Summary
- Multiple Job Execution (Iterative / Parallel)
- Asynchronous Support
- Multiprocessing Producer/Consumer Support
- Automatic recommendation of the num of workers
- Timer Support
- Logging support per Worker/Job

# Getting Started
## Installation
```bash
pip install -r requirements.txt
```
## Simple Usage
```bash
$ python main.py --help

Usage: main.py [OPTIONS] COMMAND [ARGS]...

╭─ Options ──────────────────────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.                    │
│ --show-completion             Show completion for the current shell, to copy it or         │
│                               customize the installation.                                  │
│ --help                        Show this message and exit.                                  │
╰────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ─────────────────────────────────────────────────────────────────────────────────╮
│ job-info                                                                                   │
│ run        # Job Context Sample > run Job:HelloWorld arg1 arg2 kwarg1=value1 kwarg2=value2 │
╰────────────────────────────────────────────────────────────────────────────────────────────╯
```

### Run Job
```bash
 Usage: main.py run [OPTIONS] JOB_CONTEXT...

 # Job Context Sample > run Job:HelloWorld arg1 arg2 kwarg1=value1 kwarg2=value2

╭─ Arguments ────────────────────────────────────────────────────────────────────────────────╮
│ *    job_context      JOB_CONTEXT...  Job Context [default: None] [required]               │
╰────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ──────────────────────────────────────────────────────────────────────────────────╮
│ --workers                    INTEGER  Number of workers, (0=auto) [default: 0]             │
│ --verbose    --no-verbose             Verbose mode [default: verbose]                      │
│ --help                                Show this message and exit.                          │
╰────────────────────────────────────────────────────────────────────────────────────────────╯

$ python main.py run Job:HelloWorld
# Job Context Sample 
# run Job:<JobName> arg1 arg2 kwarg1=value1 kwarg2=value2
```
### Job Info
```bash
$ python main.py job-info
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Name      ┃ Path                                                ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ job.hello │ /Users/imiml/Documents/GitHub/IMJob/IMJob/job/hello │
└───────────┴─────────────────────────────────────────────────────┘
```

## Register Job
First of all, you must implement the job you want to register by inheriting the Job Class. Job Class is Abstract Class, so you must implement the run method.

- You must implement the `run` method, and it must be an `async` function.
- You can override the `__init__` method to reuse variables inside the instance, but you cannot receive additional arguments from the `__init__` method. (receive all arguments from the `run` method)
- Jobs must be defined in modules within the `/job` package.
```python
# job/hello.py
from job import Job

class HelloWorld(Job):

    def __init__(self):
        super().__init__()
        self.goodbye = "Goodbye World!"

    async def run(self, name: str = 'IML'):
        print(f"Hello World and {name}!")
        print(self.goodbye)
```

## Job Context
You can use the Job Context to pass arguments to the Job. The Job Context is a string that contains the Job Name and the arguments to be passed to the Job. The Job Context is passed as an argument to the `run` command.

Let's run the Job (HelloWorld) created above through the example below.

```bash
$ python main.py run Job:HelloWorld

workers(10) is greater than number of jobs. Set to 1.
[Worker-41078] started Job[HelloWorld].
Hello World and IML!
Goodbye World!
Total elapsed time: 0.001 seconds.
```
If this sounds noisy to you, there are good options.
```bash
$ python main.py run Job:HelloWorld --no-verbose
Hello World and IML!
Goodbye World!
```
You can give other arguments by modifying the Job Context.
```bash
# The result of both commands is the same.(args, kwargs)
$ python main.py run Job:HelloWorld IronMan --no-verbose
$ python main.py run Job:HelloWorld name=IronMan --no-verbose

Hello World and IronMan!
Goodbye World!
```
### Multiple Job Execution
You can run multiple jobs at once by passing multiple Job Contexts.

such as
`run Job:JobName1 arg1 arg2 kwarg1=value1 kwarg2=value2 Job:JobName2 arg1 arg2 kwarg1=value1 kwarg2=value2 ...`
```bash
$ python main.py run Job:HelloWorld IronMan Job:HelloWorld Tony --workers 1
 
[Worker-43805] started Job[HelloWorld].
Hello World and IronMan!
Goodbye World!
[Worker-43805] started Job[HelloWorld].
Hello World and Tony!
Goodbye World!
Total elapsed time: 0.000 seconds.
```

## Multiple Workers
You can run multiple jobs at once by passing multiple Job Contexts.

First, I created a slow job as a class to feel the performance improvement of parallel execution.

```python
# job/hello.py
class SlowWork(Job):

    async def run(self, sec: int = 1):
        time.sleep(sec)
        print(f"Slow Work {sec}!")
```
And let's run the command like this:
```bash
$ python main.py run Job:SlowWork Job:SlowWork Job:SlowWork Job:SlowWork --workers 1

[Worker-46965] started Job[SlowWork].
Slow Work 1!
[Worker-46965] started Job[SlowWork].
Slow Work 1!
[Worker-46965] started Job[SlowWork].
Slow Work 1!
[Worker-46965] started Job[SlowWork].
Slow Work 1!
Total elapsed time: 4.034 seconds.
```
The above is an example of running sequentially because there is only one worker. Let's increase the worker option this time.
```bash
$ python main.py run Job:SlowWork Job:SlowWork Job:SlowWork Job:SlowWork --workers 4

[Worker-2-47355] started...
[Worker-0-47353] started...
[Worker-2-47355] get Job[SlowWork].
[Worker-0-47353] get Job[SlowWork].
[Worker-1-47354] started...
[Worker-1-47354] get Job[SlowWork].
[Worker-3-47356] started...
[Worker-3-47356] get Job[SlowWork].
Slow Work 1!
Slow Work 1!
Slow Work 1!
Slow Work 1!
[Worker-3-47356] complete Job[SlowWork].
[Worker-3-47356] turn off...
[Worker-1-47354] complete Job[SlowWork].
[Worker-0-47353] complete Job[SlowWork].
[Worker-1-47354] turn off...
[Worker-0-47353] turn off...
[Worker-2-47355] complete Job[SlowWork].
[Worker-2-47355] turn off...
Total elapsed time: 1.168 seconds.
```

# References
- https://hub.docker.com/repository/docker/iml1111/imjob/general
