# Python Algorithm Alchemists Machinery (pyalma)

**Disclaimer:** This project is in a very early stage of development and should therefor be considered as experimental.

The pyalma package provides a framework to plan, run, pause and continue file based experiments (or workloads in general). The framework provided is especially helpful if you have to perform multiple tasks on big batches of files in numerous iterations. It strength comes from the ability to lengthy experiments (tasks) in advance. This allows track progress and pause/continue long tasks.

## Example

Everything starts with grouping the files of interests to (a) [batch(es)](./docs/batch.md). Lets say we have a batch file `example.batch`. This could look as follows. 

###### `example.batch`
 
```json
{
    "instances":
    [
        "file1",
        "file2",
        .
        .
        .
        "file100"
    ]
}
```

Then we need to specify our [experiment / task](./docs/experiment.md). Like the batch descriptions this is also completely file based.

###### `example.experiment`

```json
{
    "load": "example.py",
    
    "workers": 3,

    "iterations": 100,

    "batch": "example.batch"
}
```

The experiment description in `example.experiment` roughly translates to: Perform the algorithm loaded from `example.py` 100 times on all files in `example.batch` and use 3 worker threads to do so. Let's have a look at `example.py` (look at [Run Module](./docs/run_module.md) for more information).

###### `example.py`

```python
def run(instance, save_callback, state):
    # do some stuff on "instance"
```

The `run` function is where the magic happens. For every file in our batch the  ***pyalma*** framework will call `run(...)` exactly "iterations" times. The `instance` parameter is a path to one file of our `example.batch`. 

Now that we have specified everything, we can start executing our experiment.

```python
>>> import alma.experiment

>>> dispatcher = alma.experiment.load("example.experiment")
>>> dispatcher.start()
```

The line `dispatcher.start()` starts the concurrent non blocking execution of our experiment. This means the dispatcher stays responsive and we can pause/stop the execution at any given time.

```python
>>> dispatcher.stop()
```

During the execution the `dispatcher` continuously keeps track of which files he still needs to call `run(...)` on and how many iterations he has left. He does so by saving the current state of the execution in a file. Loading an experiment (`alma.experiment.load(...)`) the framework first looks for such a save file and if one exists, the execution will pick up at the point we've called `dispatcher.stop()`. To pick up the experiment we can perform:

```python
>>> dispatcher = alma.experiment.load("example.experiment")
>>> dispatcher.start()
```
**Note:** The Granularity of  the save file is at the file level, meaning that every active `run(...)` call will be aborted  when `dispatcher.stop(...)` gets called. If we continue the execution at a later time, these `run(...)` calls will be reinitiated.

## Install

Fist clone the repository and then switch into it's root directory and call

```bash
$ pip install -e .
```
This will locally install the **pyalma** framework on your system.
