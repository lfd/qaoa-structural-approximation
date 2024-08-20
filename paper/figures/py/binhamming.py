import scipy as sc

def binhamming(a, b):
    ba = bin(a)[2:]
    bb = bin(b)[2:]

    if len(ba) > len(bb):
        bb = bb.zfill(len(ba))
    elif len(ba) < len(bb):
        ba = ba.zfill(len(bb))

    return(sc.spatial.distance.hamming(list(bb), list(ba)) * len(bb))
