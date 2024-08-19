from sim import train_on_QPU
from sim import sim
import os
import numpy as np


def sample_qaoa(target, nsamples, qaoa_state, n):
    is_in_target = []

    for i in range(nsamples):
        bitstring = sim.measure_bitstring(n, qaoa_state)
        state = int("".join(map(str, bitstring)), 2)
        is_in_target.append(1 if state in target else 0)

    return is_in_target


def run(instance, save, state, **kwargs):
    PARAMS={"pangle": 4.714e+00, "mangle": -1.747e-01}
    id = kwargs["worker_id"]
    n = instance["data"]["n"]
    nsamples = instance["data"]["nsamples"]

    target_size_ratio = instance["data"]["target_size_ratio"]
    target_size = int(2**n * target_size_ratio)

    np.random.seed(instance["seed"] % 2**32)

    target = np.unique(np.random.random_integers(0,2**n - 1, target_size))
    while len(target) < target_size:
        target = np.unique(np.append(target, [np.unique(np.random.random_integers(0,2**n - 1, target_size - len(target)))]))

    filepath = f"out/uniform_preopt/out{id:03d}"

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


