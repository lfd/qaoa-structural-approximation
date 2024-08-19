from sim import train_on_QPU
from sim import sim
import os
import numpy as np



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


def sample_qaoa(target, nsamples, qaoa_state, n):
    is_in_target = []

    for i in range(nsamples):
        bitstring = sim.measure_bitstring(n, qaoa_state)
        state = int("".join(map(str, bitstring)), 2)
        is_in_target.append(1 if state in target else 0)

    return is_in_target


def run(instance, save, state, **kwargs):
    PARAMS={"pangle": 2.735e+00, "mangle": 2.018e-01}
    id = kwargs["worker_id"]
    primes = instance["data"]["primes"]
    nsamples = int(instance["data"]["nsamples"])

    np.random.seed(instance["seed"] % 2**32)

    n = 2 * int(max(map(np.ceil, map(np.log2, primes))))

    q, r = np.sort(np.random.choice(primes, 2, replace=False))

    target = [int(f"{bin(q)[2:].zfill(n//2)}{bin(r)[2:].zfill(n//2)}", 2),
              int(f"{bin(r)[2:].zfill(n//2)}{bin(q)[2:].zfill(n//2)}", 2)]

    filepath = f"out/qrf_preopt/out{id:03d}"

    file_is_new = True if not os.path.isfile(filepath) else False

    C = sim.C_hamiltonian(n, target)
    circ = sim.Uqaoa(n, C, pangle=PARAMS["pangle"], mangle=PARAMS["mangle"])
    qaoa_state = circ * sim.ket_s(n)

    is_in_target = sample_qaoa(target, nsamples, qaoa_state, n)

    with open(filepath, "a") as of:
        if file_is_new: 
            of.write("n,mangle,pangle,issolution,nsamples,seed,opt\n")

        for intarget in is_in_target:
            of.write(f"{n},{PARAMS['mangle']},{PARAMS['pangle']},{intarget},{nsamples},{instance['seed']},preopt\n")

    res = train_on_QPU.train(target, n)
    mangle = res["x"][0]
    pangle = res["x"][1]

    circ = sim.Uqaoa(n, C, pangle=pangle, mangle=mangle)
    qaoa_state = circ * sim.ket_s(n)

    is_in_target = sample_qaoa(target, nsamples, qaoa_state, n)
    with open(filepath, "a") as of:
        for intarget in is_in_target:
            of.write(f"{n},{mangle},{pangle},{intarget},{nsamples},{instance['seed']},circopt\n")

