import pathlib as pl
import json
import os
import multiprocessing
import threading
import random
import sys

from . import batch


class Plan:
    def __init__(self, experiment=None, lock=None):
        self.experiment = None
        self.file = None
        self.pending_instances = []
        self.assigned_instances = []
        self.instance_states = {}

        self.__instance_id_counter = 0

        self.__lock = threading.Lock() if lock is None else lock

        if experiment:
            self.create(experiment)

    def create(self, experiment):
        self.experiment = pl.Path(experiment).resolve()
        self.__set_file()

        if self.__is_finished():
            self.__create()
        else:
            self.__load()

    def __create(self):
        content = self.__create_content()

        self.pending_instances = content["pending"]
        self.iterations_left = content["iterations_left"]

        with self.__lock:
            self.__update_file()

    def __create_content(self, iterations_left=None):
        content = {}

        with open(self.experiment, "r") as expf:
            exp_obj = json.loads(expf.read())

            instances = batch.load(pl.Path(exp_obj["batch"]))

            if iterations_left is None:

                if "iterations" in exp_obj:
                    iterations_left = exp_obj["iterations"] - 1
                if "seed" in exp_obj:
                    random.seed(exp_obj["seed"])

                else:
                    iterations_left = 0

        content["pending"] = instances
        content["iterations_left"] = iterations_left

        return content

    def __set_file(self):
        if self.experiment is None:
            self.file = None
        else:
            exp_path = pl.Path(self.experiment)
            self.file = exp_path.parent / (exp_path.stem + ".plan")

    def __load(self):
        self.pending_instances = []
        self.assigned_instances = []

        if not self.file.is_file():
            return

        with open(self.file, "r") as pfile:
            content = json.loads(pfile.read())

            if "assigned" in content:
                self.assigned_instances = content["assigned"]

                self.__instance_id_counter = max(map(lambda i: i["id"], self.assigned_instances)) + 1

            if "pending" in content:
                self.pending_instances = content["pending"]

            if "iterations_left" in content:
                self.iterations_left = content["iterations_left"]

            if "instance_states" in content:
                self.instance_states = content["instance_states"]

            if "rand_state" in content:
                random.setstate(self.__arr2tup(content["rand_state"]))

    def __is_finished(self):
        return False if self.file.is_file() else True

    def next(self):

        with self.__lock:
            self.__load()

            if len(self.pending_instances) == 0:
                if self.iterations_left > 0:
                    self.__load_next_iteration()
                else:
                    return None

            next_instance = self.pending_instances.pop()
            next_instance["id"] = self.__instance_id_counter
            next_instance["seed"] = random.randint(0, sys.maxsize)
            self.__instance_id_counter += 1

            self.assigned_instances.append(next_instance)

            self.__update_file()

            return next_instance

    def done_with(self, instance):

        with self.__lock:
            self.__load()

            self.assigned_instances = list(filter(lambda i: i["id"] != instance["id"],
                                                  self.assigned_instances))

            if str(instance["id"]) in self.instance_states:
                self.instance_states.pop(str(instance["id"]))

            self.__update_file()

    def __update_file(self):
        content = {}

        all_done = True

        content["iterations_left"] = self.iterations_left

        content["instance_states"] = self.instance_states

        if len(self.assigned_instances) > 0:
            content["assigned"] = self.assigned_instances
            all_done = False

        if len(self.pending_instances) > 0:
            content["pending"] = self.pending_instances
            all_done = False

        content["rand_state"] = random.getstate()

        if all_done:
            if self.iterations_left > 0:
                self.__load_next_iteration()
            elif self.file.is_file():
                self.file.unlink()
        else:
            self.__write_content(content)

    def __load_next_iteration(self):
        content = self.__create_content(self.iterations_left - 1)

        self.pending_instances = content["pending"]
        self.iterations_left = content["iterations_left"]

        self.__write_content(content)

    def __write_content(self, content):

        with open(self.file, "w") as pfile:
            pfile.write(json.dumps(content))

    def __serialize_rand_state(self):
        return json.dumps(random.getstate())

    def __arr2tup(self, arr):
        for i, e in enumerate(arr):
            if type(e) is list:
                arr[i] = self.__arr2tup(e)

        return tuple(arr)

    def save_instance_state(self, instance, data):

        with self.__lock:
            self.__load()

            self.instance_states[str(instance["id"])] = data

            self.__update_file()

    def load_instance_state(self, instance):

        with self.__lock:
            self.__load()

            if str(instance["id"]) in self.instance_states:
                return self.instance_states[str(instance["id"])]
            else:
                return ""

    def delete(self):
        with self.__lock:
            self.__load()

            self.pending_instances.extend(self.assigned_instances)
            self.assigned_instances = []

            self.__update_file()
