import json
import pathlib as pl

def load(batch_file):
    batch_file = pl.Path(batch_file).resolve()

    with open(batch_file, "r") as bfile:
        batch_obj = json.loads(bfile.read())

    batch_obj["base_path"] = batch_file.parent

    return __load_batch_obj(batch_obj)


def __load_batch_obj(batch_obj):
    instances = []

    instance_dir = None

    if "dir" in batch_obj:
        instance_dir = pl.Path(batch_obj["dir"])

        if not instance_dir.is_absolute():
            instance_dir = pl.Path(batch_obj["base_path"], instance_dir)
    else:
        instance_dir = batch_obj["base_path"]

    if "instances" in batch_obj:
        for instance in batch_obj["instances"]:
            file_path = ""
            instance_data = {}
            
            if "file" in instance:
                file_path =  pl.Path(instance_dir, instance["file"]).resolve()
           
            if "data" in instance:
                instance_data = instance["data"]
                
            instances.append({"file": file_path, "data": instance_data})

    if "batches" in batch_obj:
        for batch in batch_obj["batches"]:
            batch["base_path"] = instance_dir

            instances.extend(__load_batch_obj(batch))

    if "include" in batch_obj:
        for batch_file in batch_obj["include"]:
            instances.extend(load(pl.Path(instance_dir, batch_file)))

    return instances

