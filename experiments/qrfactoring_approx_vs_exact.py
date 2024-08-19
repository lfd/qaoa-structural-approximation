import numpy as np
import os
import json
from binhamming import binhamming
from numerical_debugging import count_ds_for_k_in_target, f
from functools import reduce
import operator


def approx(n, target, theta, phi, qr, filepath):
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
        of.write(f"{json.dumps({'n': n, 'ds': list(ds), 'd1d2': d1d2})}\n")


def ck(theta, phi, k, target, n):
    return sum(map(lambda z: (np.exp(-1j * phi) if z in target else 1) * f(theta, binhamming(z,k), n), range(2**n)))


def exact(n, target, theta, phi, qr, filepath):
    vals = sum(map(lambda k: np.abs(ck(theta, phi, k, target, n))**2, target))
    vals /= 2**n

    with open(filepath, "a") as of:
        for t, val in zip(theta, vals):
            of.write(f"{n},{t},{phi},{np.abs(val)},{qr[0]},{qr[1]}\n")


def run(instance, save, state, **kwargs):
    id = kwargs["worker_id"]
    primes = instance["data"]["primes"]
    phi = instance["data"]["phi"]

    np.random.seed(instance["seed"] % 2**32)

    n = 2 * int(max(map(np.ceil, map(np.log2, primes))))

    q, r = np.sort(np.random.choice(primes, 2, replace=False))

    target = [int(f"{bin(q)[2:].zfill(n//2)}{bin(r)[2:].zfill(n//2)}", 2),
              int(f"{bin(r)[2:].zfill(n//2)}{bin(q)[2:].zfill(n//2)}", 2)]

    filepath = f"out/qrfactoring_approx/out{id:03d}"

    if not os.path.isfile(filepath):
        with open(filepath, "a") as of:
            of.write("n,theta,phi,overlap,q,r\n")

    theta = np.linspace(-np.pi / 2, np.pi / 2, 100)

    approx(n, target, theta, phi, [q, r], filepath)
    exact(n, target, theta, phi, [q, r], filepath)


def collect_ds_data(outall_ds: str):
    ds_data = {}

    with open(outall_ds) as of:
        for line in of.readlines():
            line_obj = json.loads(line)
            n = line_obj["n"]

            if str(n) not in ds_data:
                ds_data[str(n)] = {"Mds": [], "Md1d2s": []}

            ds_data[str(n)]["Mds"].append(line_obj["ds"])
            ds_data[str(n)]["Md1d2s"].append(np.array(line_obj["d1d2"]))

    return ds_data


def done():
    os.system("csvstack out/qrfactoring_approx/out??? > out/qrfactoring_approx/outall")
    os.system("for f in out/qrfactoring_approx/out???_ds ; do cat $f >> out/qrfactoring_approx/outall_ds ; done")

    ds_data = collect_ds_data("out/qrfactoring_approx/outall_ds")

    with open("out/qrfactoring_approx/out_Eds", "w") as ofE:
        with open("out/qrfactoring_approx/out_Ed1d2", "w") as ofEd1d2: 
            ofE.write("n,d,Eds\n")
            ofEd1d2.write("n,d1,d2,Ed1d2\n")

            for n_key, ds_data in ds_data.items():
                Mds = ds_data["Mds"]
                Md1d2s = ds_data["Md1d2s"]

                n = int(n_key)
                EMd = np.array(Mds).mean(axis=0)
                EMd1d2 = np.array(reduce(operator.add, Md1d2s)) / len(Md1d2s)

                for d1 in range(n + 1):
                    ofE.write(f"{n},{d1},{EMd[d1]}\n")

                    for d2 in range(n + 1):
                        ofEd1d2.write(f"{n},{d1},{d2},{EMd1d2[d1][d2]}\n")
