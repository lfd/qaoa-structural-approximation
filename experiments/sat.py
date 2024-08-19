import numpy as np
import os
import json
from binhamming import binhamming
from numerical_debugging import count_ds_for_k_in_target, f
from functools import reduce
import operator

from pysat.solvers import Glucose42


def approx(n, num_clauses, target, theta, phi, filepath):
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
        of.write(f"{json.dumps({'n': n, 'num_clauses': num_clauses, 'ds': list(ds), 'd1d2': d1d2})}\n")


def ck(theta, phi, k, target, n):
    return sum(map(lambda z: (np.exp(-1j * phi) if z in target else 1) * f(theta, binhamming(z,k), n), range(2**n)))


def exact(n, num_clauses, target, theta, phi, filepath):
    vals = sum(map(lambda k: np.abs(ck(theta, phi, k, target, n))**2, target))
    vals /= 2**n

    with open(filepath, "a") as of:
        for t, val in zip(theta, vals):
            of.write(f"{n},{num_clauses},{len(target)},{t},{phi},{np.abs(val)}\n")


def random_clause(n):
    c = np.random.choice(range(1, n+1), 3, replace=False) * np.random.choice([-1, 1], 3)
    return list(map(int, list(c)))


def model2state(m):
    k = 0

    for i, v in enumerate(m):
        if v > 0:
            k += 2**i

    return k


def run(instance, save, state, **kwargs):
    id = kwargs["worker_id"]
    n = int(instance["data"]["n"])
    num_clauses = int(instance["data"]["num_clauses"])
    phi = instance["data"]["phi"]

    np.random.seed(instance["seed"] % 2**32)
    
    target = []
    
    while len(target) == 0:
        s = Glucose42()
        for i in range(num_clauses):
            s.add_clause(random_clause(n))
             
        for m in s.enum_models():
            print(m)
            print(model2state(m))
            target.append(model2state(m))

        s.delete()

    filepath = f"out/sat/out{id:03d}"

    if not os.path.isfile(filepath):
        with open(filepath, "a") as of:
            of.write("n,numClauses,sizeT,theta,phi,overlap\n")

    with open(f"{filepath}_sizeT", "a") as of:
        of.write(f"{len(target)}\n")

    theta = np.linspace(-np.pi / 2, np.pi / 2, 100)

    approx(n, num_clauses, target, theta, phi, filepath)
    exact(n, num_clauses, target, theta, phi, filepath)


def collect_ds_data(outall_ds: str):
    ds_data = {}
    with open("out/sat/outall_ds") as of:
        for line in of.readlines():
            line_obj = json.loads(line)
            n = line_obj["n"]
            num_clauses = line_obj["num_clauses"]

            if str(n) not in ds_data:
                ds_data[str(n)] = {}

            if str(num_clauses) not in ds_data[str(n)]:
                ds_data[str(n)][str(num_clauses)] = {"Mds": [], "Md1d2s": []}

            ds_data[str(n)][str(num_clauses)]["Mds"].append(line_obj["ds"])
            ds_data[str(n)][str(num_clauses)]["Md1d2s"].append(np.array(line_obj["d1d2"]))

    return ds_data


def done():
    os.system("csvstack out/sat/out??? > out/sat/outall")
    os.system("for f in out/sat/out???_ds ; do cat $f >> out/sat/outall_ds ; done")
    os.system("for f in out/sat/out???_sizeT; do cat $f >> out/sat/outall_sizeT; done")

    ds_data = collect_ds_data("out/sat/outall_ds")

    with open("out/sat/out_Eds", "w") as ofE:
        with open("out/sat/out_Ed1d2", "w") as ofEd1d2: 
            ofE.write("n,numClauses,d,Eds\n")
            ofEd1d2.write("n,numClauses,d1,d2,Ed1d2\n")

            for n_key, n_data in ds_data.items():

                n = int(n_key)
                for nc_key, ds_data in n_data.items(): 
                    num_clauses = int(nc_key)
                    Mds = ds_data["Mds"]
                    Md1d2s = ds_data["Md1d2s"]
                    EMd = np.array(Mds).mean(axis=0)
                    EMd1d2 = np.array(reduce(operator.add, Md1d2s)) / len(Md1d2s)

                    for d1 in range(n + 1):
                        ofE.write(f"{n},{num_clauses},{d1},{EMd[d1]}\n")

                        for d2 in range(n + 1):
                            ofEd1d2.write(f"{n},{num_clauses},{d1},{d2},{EMd1d2[d1][d2]}\n")
