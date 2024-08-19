import numpy as np
import os
import scipy as sc
import json
from binhamming import binhamming
from numerical_debugging import count_ds_for_k_in_target, f
from itertools import combinations_with_replacement
from functools import reduce
import operator


def approx(n, target, nclusters, cluster_size, filepath):
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
        of.write(f"{json.dumps({'n': n, 'nclusters': nclusters, 'cluster_size': cluster_size, 'ds': list(ds), 'd1d2': d1d2})}\n")


def ck(theta, phi, k, target, n):
    return sum(map(lambda z: (np.exp(-1j * phi) if z in target else 1) * f(theta, binhamming(z,k), n), range(2**n)))


def calc_exact(n, target, theta, phi, nclusters, cluster_size, filepath):
    vals = sum(map(lambda k: np.abs(ck(theta, phi, k, target, n))**2, target))
    vals /= 2**n

    return vals


def exact(n, target, theta, phi, nclusters, cluster_size, filepath):
    vals = calc_exact(n, target, theta, phi, nclusters, cluster_size, filepath)

    with open(filepath, "a") as of:
        # for t, val in zip(theta, vals):
        #     of.write(f"{nclusters},{cluster_size},{t},{phi},{np.abs(val)}\n")
        for i in range(len(theta)):
            of.write(f"{n},{nclusters},{cluster_size},{theta[i]},{phi},{np.abs(vals[i])}\n")


def generate_target(n, pstep, nseeds, cluster_size):
    seeds = np.unique(np.random.randint(0, 2**n, nseeds))
    while len(seeds) < nseeds:
        seeds = np.unique(np.append(seeds, np.random.randint(0, 2**n, nseeds - len(seeds))))

    target = np.array([], dtype=np.uint)

    while len(target) < cluster_size * nseeds:
        for s in seeds:
            state = s

            while np.random.random() < pstep:
                state = state ^ 2**(np.random.randint(0, n))

            target = np.append(target, state).astype(np.uint)

        target = np.unique(target)

    return target.astype(np.uint)


def run(instance, save, state, **kwargs):
    id = kwargs["worker_id"]
    n = instance["data"]["n"]
    nseeds = instance["data"]["nseeds"]
    cluster_size = instance["data"]["cluster_size"]
    pstep = instance["data"]["pstep"]
    phi = instance["data"]["phi"]

    np.random.seed(instance["seed"] % 2**32)

    target = generate_target(n, pstep, nseeds, cluster_size)

    filepath = f"out/clustered/out{id:03d}"

    if not os.path.isfile(filepath):
        with open(filepath, "a") as of:
            of.write("n,nclusters,clustersize,theta,phi,overlap\n")

    theta = np.linspace(-np.pi / 2, np.pi / 2, 100)

    approx(n, target, nseeds, cluster_size, filepath)
    exact(n, target, theta, phi, nseeds, cluster_size, filepath)


def collect_ds_data(outall_ds: str):
    ds_data = {}
    with open(outall_ds) as of:
        for line in of.readlines():
            line_obj = json.loads(line)
            nclusters = line_obj["nclusters"]
            cluster_size = line_obj["cluster_size"]
            n = line_obj["n"]

            if str(nclusters) not in ds_data:
                ds_data[str(nclusters)] = {}

            if str(cluster_size) not in ds_data[str(nclusters)]:
                ds_data[str(nclusters)][str(cluster_size)] = {} 

            if str(n) not in ds_data[str(nclusters)][str(cluster_size)]:
                ds_data[str(nclusters)][str(cluster_size)][str(n)] = {"Mds": [], "Md1d2s": []}

            print(ds_data[str(nclusters)][str(cluster_size)][str(n)])

            ds_data[str(nclusters)][str(cluster_size)][str(n)]["Mds"].append(line_obj["ds"])
            ds_data[str(nclusters)][str(cluster_size)][str(n)]["Md1d2s"].append(np.array(line_obj["d1d2"]))

    return ds_data


def done():
    os.system("csvstack out/clustered/out??? > out/clustered/outall")
    os.system("for f in out/clustered/out???_ds ; do cat $f >> out/clustered/outall_ds ; done")

    ds_data = collect_ds_data("out/clustered/outall_ds")

    with open("out/clustered/out_Eds", "w") as ofE:
        with open("out/clustered/out_Ed1d2", "w") as ofEd1d2: 
            ofE.write("n,nclusters,clustersize,d,Eds\n")
            ofEd1d2.write("n,nclusters,clustersize,d1,d2,Ed1d2\n")

            for nclusters, ds_data_nclusters in ds_data.items():
                for cluster_size, ds_data_cluster_size in ds_data_nclusters.items():
                    for n_key, ds_data in ds_data_cluster_size.items():
                        Mds = ds_data["Mds"]
                        Md1d2s = ds_data["Md1d2s"]

                        n = int(n_key)
                        EMd = np.array(Mds).mean(axis=0)
                        EMd1d2 = np.array(reduce(operator.add, Md1d2s)) / len(Md1d2s)
                        
                        for d1 in range(n + 1):
                            ofE.write(f"{n},{nclusters},{cluster_size},{d1},{EMd[d1]}\n")

                            for d2 in range(n + 1):
                                ofEd1d2.write(f"{n},{nclusters},{cluster_size},{d1},{d2},{EMd1d2[d1][d2]}\n")
