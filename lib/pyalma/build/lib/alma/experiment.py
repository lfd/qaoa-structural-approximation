import pathlib as pl
import json
import importlib.machinery as impmach
import multiprocessing
import threading 
import concurrent.futures as concfut
import os
import time
import random
import sys

from . import batch
from . import plan


def execute(exp_file):
    dispatcher = load(exp_file)
    dispatcher.start()
    dispatcher.join()


def load(exp_file):
    exp_plan = plan.Plan(exp_file, multiprocessing.Lock())

    with open(exp_file) as efile:
        exp_obj = json.loads(efile.read())
        exp_obj["load"] = pl.Path(exp_obj["load"])

        exp_mod = impmach.SourceFileLoader(exp_obj["load"].stem,
                                           str(exp_obj["load"])).load_module()

    num_workers = 1

    if "workers" in exp_obj:
        if exp_obj["workers"] == "all":
            num_workers = os.cpu_count()
        else:
            num_workers = int(exp_obj["workers"])

    return Dispatcher(exp_mod, exp_plan, num_workers)


class Dispatcher (threading.Thread):
    def __init__(self, exp_mod, exp_plan, num_workers):
        threading.Thread.__init__(self)

        self.__num_workers = num_workers
        self.__workers = []
        self.__stop_called = threading.Event()

        self.__exp_mod = exp_mod

        for i in range(self.__num_workers):
            self.__workers.append(Worker(exp_mod,
                                         exp_plan,
                                         i))

    def run(self):
        for worker in self.__workers:
            worker.start()

        def wait_to_continue(workers, stop_called):
            def any_worker_alive(): any(map(lambda w: w.is_alive(), workers))

            while any_worker_alive() and not stop_called.is_set():
                time.sleep(0)

        waiter = threading.Thread(target=wait_to_continue,
                                  args=(self.__workers,
                                        self.__stop_called))

        waiter.start()
        waiter.join()

        if self.__stop_called.is_set():
            for worker in self.__workers:
                worker.terminate()

        for worker in self.__workers:
            worker.join()

        self.__done()

    def stop(self):
        self.__stop_called.set()

    def num_active_workers(self):
        count = 0
        for worker in self.__workers:
            count += 1 if worker.is_alive() else 0

        return count

    def __done(self):
        if hasattr(self.__exp_mod, "done"):
            self.__exp_mod.done()


class Worker (multiprocessing.Process):
    def __init__(self, exp_mod, exp_plan, id):
        multiprocessing.Process.__init__(self)

        self.__exp_mod = exp_mod
        self.__exp_plan = exp_plan
        self.__id = id

    def run(self):
        instance = self.__exp_plan.next()

        while instance is not None:
            instance_state = self.__exp_plan.load_instance_state(instance)

            self.__exp_mod.run(instance,
                               lambda data: self.__exp_plan.save_instance_state(
                                   instance,
                                   data
                                ),
                               instance_state,
                               worker_id=self.__id)

            self.__exp_plan.done_with(instance)

            instance = self.__exp_plan.next()

    def terminate(self):
        self.__exp_plan.delete()
        multiprocessing.Process.terminate(self)
