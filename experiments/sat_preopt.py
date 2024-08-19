from sim import train_on_QPU
from sim import sim
import os
import numpy as np

from pysat.solvers import Glucose42


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


def random_clause(n):
    c = np.random.choice(range(1, n+1), 3, replace=False) * np.random.choice([-1, 1], 3)
    return list(map(int, list(c)))


def model2state(m):
    k = 0

    for i, v in enumerate(m):
        if v > 0:
            k += 2**i

    return k


def sample_qaoa(target, nsamples, qaoa_state, n):
    is_in_target = []

    for i in range(nsamples):
        bitstring = sim.measure_bitstring(n, qaoa_state)
        state = int("".join(map(str, bitstring)), 2)
        is_in_target.append(1 if state in target else 0)

    return is_in_target


def run(instance, save, state, **kwargs):
    PARAMS={"pangle": 2.496e+00, "mangle": 2.874e-01}

    id = kwargs["worker_id"]
    n = int(instance["data"]["n"])
    num_clauses = int(instance["data"]["num_clauses"])
    nsamples = int(instance["data"]["nsamples"])

    np.random.seed(instance["seed"] % 2**32)
    
    target = []
    
    while len(target) == 0:
        s = Glucose42()
        for i in range(num_clauses):
            s.add_clause(random_clause(n))
             
        for m in s.enum_models():
            target.append(model2state(m))

        s.delete()

    filepath = f"out/sat_preopt/out{id:03d}"

    file_is_new = True if not os.path.isfile(filepath) else False

    C = sim.C_hamiltonian(n, target)
    circ = sim.Uqaoa(n, C, pangle=PARAMS["pangle"], mangle=PARAMS["mangle"])
    qaoa_state = circ * sim.ket_s(n)

    is_in_target = sample_qaoa(target, nsamples, qaoa_state, n)

    with open(filepath, "a") as of:
        if file_is_new: 
            of.write("n,mangle,pangle,issolution,nsamples,seed,opt,sizeT,nclauses\n")

        for intarget in is_in_target:
            of.write(f"{n},{PARAMS['mangle']},{PARAMS['pangle']},{intarget},{nsamples},{instance['seed']},preopt,{len(target)},{num_clauses}\n")

    res = train_on_QPU.train(target, n)
    mangle = res["x"][0]
    pangle = res["x"][1]

    circ = sim.Uqaoa(n, C, pangle=pangle, mangle=mangle)
    qaoa_state = circ * sim.ket_s(n)

    is_in_target = sample_qaoa(target, nsamples, qaoa_state, n)
    with open(filepath, "a") as of:
        for intarget in is_in_target:
            of.write(f"{n},{mangle},{pangle},{intarget},{nsamples},{instance['seed']},circopt,{len(target)},{num_clauses}\n")


