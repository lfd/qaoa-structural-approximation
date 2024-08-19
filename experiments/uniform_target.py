import numpy as np
import json
from binhamming import binhamming
from numerical_debugging import count_ds_for_k_in_target, f
import os
from functools import reduce
import operator


def approx(n, target, target_size_ratio, filepath):
    ds = np.zeros(n + 1)

    d1d2 = np.zeros((n + 1, n + 1))

    for k in target:
        counts = np.array(count_ds_for_k_in_target(n, k, target))

        ds += counts

        for d1 in range(n+1):
            for d2 in range(n+1):
                d1d2[d1, d2] += counts[d1] * counts[d2] / len(target)
    
    ds /= len(target)
    d1d2 = list(map(list, list(d1d2)))

    with open(f"{filepath}_ds", "a") as of:
        of.write(f"{json.dumps({'n': n, 'target_size_ratio': target_size_ratio, 'ds': list(ds), 'd1d2': d1d2})}\n")


def ck(theta, phi, k, target, n):
    return sum(map(lambda z: (np.exp(-1j * phi) if z in target else 1) * f(theta, binhamming(z,k), n), range(2**n)))


def calc_exact(n, target, theta, phi, filepath):
    vals = sum(map(lambda k: np.abs(ck(theta, phi, k, target, n))**2, target))
    vals /= 2**n

    return vals


def exact(n, target, target_size_ratio, theta, phi, filepath):
    vals = calc_exact(n, target, theta, phi, filepath)

    with open(filepath, "a") as of:
        for i in range(len(theta)):
            of.write(f"{n},{target_size_ratio},{theta[i]},{phi},{np.abs(vals[i])}\n")


def run(instance, save, state, **kwargs):
    id = kwargs["worker_id"]
    n = instance["data"]["n"]
    phi = instance["data"]["phi"]

    target_size_ratio = instance["data"]["target_size_ratio"]
    target_size = int(2**n * target_size_ratio)

    np.random.seed(instance["seed"] % 2**32)
 
    target = np.unique(np.random.random_integers(0,2**n - 1, target_size))
    while len(target) < target_size:
        target = np.unique(np.append(target, [np.unique(np.random.random_integers(0,2**n - 1, target_size - len(target)))]))

    filepath = f"out/uniform/out{id:03d}"

    if not os.path.isfile(filepath):
        with open(filepath, "a") as of:
            of.write("n,targetSizeRatio,theta,phi,overlap\n")

    theta = np.linspace(-np.pi / 2, np.pi / 2, 100)

    approx(n, target, target_size_ratio, filepath)
    exact(n, target, target_size_ratio, theta, phi, filepath)


def collect_ds_data(outall_ds: str):
    ds_data = {}
    with open(outall_ds) as of:
        for line in of.readlines():
            line_obj = json.loads(line)
            n = int(line_obj["n"])
            target_size_ratio = float(line_obj["target_size_ratio"])

            if str(target_size_ratio) not in ds_data:
                ds_data[str(target_size_ratio)] = {}
            
            if str(n) not in ds_data[str(target_size_ratio)]:
                ds_data[str(target_size_ratio)][str(n)] = {"Mds": [], "Md1d2s": []}

            ds_data[str(target_size_ratio)][str(n)]["Mds"].append(line_obj["ds"])
            ds_data[str(target_size_ratio)][str(n)]["Md1d2s"].append(np.array(line_obj["d1d2"]))

    return ds_data


def done():
    os.system("csvstack out/uniform/out??? > out/uniform/outall")
    os.system("for f in out/uniform/out???_ds ; do cat $f >> out/uniform/outall_ds ; done")

    ds_data = collect_ds_data("out/uniform/outall_ds")

    with open("out/uniform/out_Eds", "w") as ofE:
        with open("out/uniform/out_Ed1d2", "w") as ofEd1d2: 
            ofE.write("n,sizeRatio,d,Eds\n")
            ofEd1d2.write("n,sizeRatio,d1,d2,Ed1d2\n")

            for size_ratio_key, ratio_data in ds_data.items():
                for n_key, ds_data in ratio_data.items(): 
                    Mds = ds_data["Mds"]
                    Md1d2s = ds_data["Md1d2s"]
                    target_size_ratio = float(size_ratio_key)

                    n = int(n_key)
                    EMd = np.array(Mds).mean(axis=0)
                    EMd1d2 = np.array(reduce(operator.add, Md1d2s)) / len(Md1d2s)

                    for d1 in range(n + 1):
                        ofE.write(f"{n},{target_size_ratio},{d1},{EMd[d1]}\n")

                        for d2 in range(n + 1):
                            ofEd1d2.write(f"{n},{target_size_ratio},{d1},{d2},{EMd1d2[d1][d2]}\n")
