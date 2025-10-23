import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from binhamming import binhamming
from pysat.solvers import Glucose42

def t_Graph(ts):
    G = nx.Graph()
    for i in range(len(ts)):
        t1 = ts[i]
        for j in range(i + 1, len(ts)):
            t2 = ts[j]
            G.add_edge(t1, t2, weight = -1 * binhamming(t1, t2))

    return G


def t_centered_layer_layout(ts):
    layouts = {}
    for t1 in ts:
        layout = {t1: [0, 0]}
        for t2 in ts:
            d = binhamming(t1, t2)
            angle = np.random.rand() * 2 * np.pi
            layout[t2] = [d * np.sin(angle), d * np.cos(angle)]

        layouts[t1] = layout

    return layouts

def t_centered_layer_layout_even(ts):
    layouts = {}


    for t1 in ts:
        layout = {t1: [0, 0]} 
        ds = {}
        for t2 in ts:
            d = binhamming(t1, t2)
            if d not in ds:
                ds[d] = [t2]
            else:
                ds[d].append(t2)


        for d, t2s in ds.items():
            angle_step = 2 * np.pi / len(t2s)
            angle = 0
            angle_offset = np.random.rand() * 2 * np.pi

            for t2 in t2s:
                angle += angle_step
                layout[t2] = [d * np.sin(angle + angle_offset), d * np.cos(angle + angle_offset)]

        layouts[t1] = layout

    return layouts

def hamdist_plot(ax, G, sls, t, highlight_level: None):
    max_dist = int(max([-w for _,_,w in G.edges.data('weight')]))
    highlight_nodes = [v for v in G.nodes() if v != t and -1 * int(G[t][v]['weight']) == highlight_level]
    nx.draw_networkx_nodes(
        G,
        sls[t], 
        nodelist=[v for v in G.nodes() if v not in highlight_nodes],
        ax=ax,
        node_color='black',
        node_size=15
    )

    nx.draw_networkx_nodes(
        G,
        sls[t],
        nodelist=highlight_nodes,
        ax=ax,
        node_color='#E69F00',
        node_size=15
    )
    nx.draw_networkx_edges(G, sls[t], ax=ax, edge_color='gray', width=0.25)

    for d in range(1, max_dist + 1):
        active = False
        for t2 in G.neighbors(t):
            if int(G[t][t2]['weight']) == -d:
                active = True
                break

        ax.add_patch(
            plt.Circle(
                (0, 0),
                d,
                fill=False,
                lw = 1.5 if active else 0.5,
                ec = '#E69F00' if highlight_level != None and d == highlight_level else 'black'
            )
        )

    return ax

def hamdist_tikz_node(G, sls, t, highlight_level= None, draw_edges=True, max_d=None, draw_bounding_box=True, clip=True):
    circle_size = 0.3
    shell_radius_scale = 0.825

    max_dist = int(max([-w for _,_,w in G.edges.data('weight')]))

    nodes = G.nodes()
    if max_d != None:
        nodes = [t] + [v for v in G.neighbors(t) if -1 * G[t][v]['weight'] <= max_d]

    highlight_nodes = [v for v in nodes if v != t  and -1 * int(G[t][v]['weight']) == highlight_level]
    non_highlight_nodes = [v for v in nodes if v not in highlight_nodes]
     
    ls = sls[t]

    top = shell_radius_scale * max(map(lambda c: ls[c][1], nodes)) 
    bot = shell_radius_scale * min(map(lambda c: ls[c][1], nodes)) 

    lef = shell_radius_scale * min(map(lambda c: ls[c][0], nodes)) 
    rig = shell_radius_scale * max(map(lambda c: ls[c][0], nodes)) 

    active_ds = list(set(map(lambda n: -1 * G[n][t]['weight'], G.neighbors(t))))

    tikz_vertex_coord_definition = "\n".join(map(
        lambda v: f"\coordinate (t{v}) at ({shell_radius_scale * ls[v][0]},{shell_radius_scale * ls[v][1]});", 
        nodes
    ))

    tikz_vertex_dots = "\n".join(map(
        lambda v: f"\draw[fill=lfd2,color=lfd2] (t{v}) circle ({circle_size});", 
        highlight_nodes
    ))

    tikz_vertex_dots_highlighted = "\n".join(map(
        lambda v: f"\draw[fill=black,color=black] (t{v}) circle ({circle_size});", 
        non_highlight_nodes
    ))

    tikz_d_circles = "\n".join(map(
        lambda d: f"\draw[line width={1.25 if d in active_ds else 0.5},color={'lfd2' if d == highlight_level else 'black'}] (0,0) circle ({shell_radius_scale * d});", 
        range(1, (max_dist if max_d == None else min(max_dist, max_d)) + 1)
    ))

    tikz_edges = ""
    if draw_edges:
        tikz_edges = "\n".join(map(
            lambda e: f"\draw[color=gray,line width=0.5] (t{e[0]}) -- (t{e[1]});",
            [e for e in G.edges() if e[0] in nodes and e[1] in nodes and G[e[0]][e[1]]['weight'] == -1]
        ))

    tikz_bounding_box = ""
    if draw_bounding_box:
        tikz_bounding_box = f"\\draw[line width=1] ({lef - 1},{top + 1}) rectangle ({rig + 1},{bot - 1});"

    tikz_clip = ""
    if clip:
        tikz_clip = f"\\clip ({lef - 1},{top + 1}) rectangle ({rig + 1},{bot - 1});"

    tikz_body = '\n'.join(filter(lambda s: len(s) > 0, [tikz_vertex_coord_definition,
      tikz_bounding_box,
      tikz_clip,
      tikz_edges,
      tikz_d_circles,
      tikz_vertex_dots,
      tikz_vertex_dots_highlighted]))

    tikz_str = f"""
    \\tikz[x=0.75em,y=0.75em,baseline=(current bounding box.center)]{{
      {tikz_body}
    }}
    """

    return tikz_str.strip()

def hamdist_tikz(n, G, sls, ts, nrows, ncols, highlight_level= None):

    def pp_t_as_assignment(t):
        #return "$" + ','.join(map(lambda kv: f"x_{{{kv[0]}}}" if kv[1] == '1' else f'\\overline{{x_{{{kv[0]}}}}}', enumerate(bin(t)[2:]))) + "$"
        return "$k = " + bin(t)[2:].zfill(n) + "$"

    matrix_elements = "\\\\".join(map(
        lambda r: "&\n".join(map(
            lambda c: f"""
                \\makecell{{
                    {hamdist_tikz_node(G, sls, ts[r*ncols + c], highlight_level=highlight_level)} \\\\
                    {pp_t_as_assignment(ts[r*ncols + c])}
                }}
            """,
            range(ncols)
        )),
        range(nrows)
    ))

    tikz_formula_inner = "\\begin{aligned}" + "\\\\".join(map(
        lambda r: "&\n".join(map(
            lambda c: "\\ab(\\mbox{" + hamdist_tikz_node(
                G, 
                sls,
                ts[r*ncols + c], 
                highlight_level=highlight_level,
                max_d=highlight_level,
                draw_bounding_box=False,
                draw_edges = False,
                clip=False
            ) + "})",
            range(ncols)
        )),
        range(nrows)
    )) + "\\end{aligned}"

    tikz_num_orange_dots = f"\\#_{{\\mbox{{\\tikz[x=0.75em,y=0.75em]{{\\draw[color=lfd2,fill=lfd2] (0,0) circle (0.4);}}}}}}"

    def tikz_num_d(G, sls, t, highlight_level):
        return f"""
        {tikz_num_orange_dots}\\ab(\\mbox{{
                {
            hamdist_tikz_node(
                G, 
                sls,
                t, 
                highlight_level=highlight_level,
                max_d=highlight_level,
                draw_bounding_box=False,
                draw_edges = False,
                clip=False
            )}
            }})
        """

    tikz_formula_inner = ",\\\\".join(map(
        lambda r: "&" + ",".join(map(
            lambda c: tikz_num_d(G, sls, ts[r*ncols + c], highlight_level),
            range(ncols)
            )),
        range(nrows))) + "\\\\"

    tikz_set_graphics = f"""
    \\ab\\{{
      \\begin{{aligned}}
        {tikz_formula_inner}
      \\end{{aligned}}
    \\}}
    """

    def tikz_num_d_formal(t):
        return f"\\#_{{{highlight_level}}}\\ab({bin(t)[2:].zfill(n)})"

    def num_d(d, t):
        return len([e for e in G.edges(data='weight') if t in e[:2] and e[2] == -d])

    tikz_num_d_formal_set_inner = ",\\\\".join(map(
        lambda r: "&" + ",".join(map(
            lambda c: tikz_num_d_formal(ts[r*ncols + c]),
            range(ncols)
            )),
        range(nrows))) + "\\\\"

    tikz_num_d_formal_set = f"""
    \\overline{{
      \\ab\\{{
        \\begin{{aligned}}
            {tikz_num_d_formal_set_inner}
        \\end{{aligned}}
      \\}}
    }}
    """

    tikz_graphs = f"""
    \\begin{{tabular}}{{{'c' * ncols}}}
        {matrix_elements} \\\\
    \\end{{tabular}}
    """.strip()

    tikz_mean_num_d = f"""
    \\overline{{
      \\ab\\{{
          {','.join([str(num_d(highlight_level, t)) for t in ts[:nrows*ncols]])}
      \\}}
    }}
    """.strip()

    tikz_formula = f"""
    \\begin{{align*}}
    \\overline{{\\#_{{d=2}}}} &= {tikz_num_d_formal_set} \\\\[1em]
    &= \\overline{{
      {tikz_set_graphics.strip()}
    }} \\\\[1em]
    &= {tikz_mean_num_d} = {np.mean([num_d(highlight_level, t) for t in ts[:nrows*ncols]])}
    \\end{{align*}}
    """.strip()

    tikz_str_top = f"""
    \\colorbox{{lfd3}}{{\\parbox{{\\textwidth}}{{\\textcolor{{white}}{{Hamming Distance Structure}}}}}}

    \\vspace*{{1em}}
    {tikz_graphs}
    """

    tikz_str_bottom = f"""
    \\colorbox{{lfd3}}{{\\parbox{{\\textwidth}}{{\\textcolor{{white}}{{Derivation of $\\#_d(k)$}}}}}}
    {tikz_formula}
    """
    
    tikz_str = f"""
    {tikz_str_top}
    {tikz_str_bottom}
    """

    return tikz_str, tikz_str_top, tikz_str_bottom


def random_clause(n):
    c = np.random.choice(range(1, n+1), 3, replace=False) * np.random.choice([-1, 1], 3)
    return list(map(int, list(c)))


def model2state(m):
    k = 0

    for i, v in enumerate(m):
        if v > 0:
            k += 2**i

    return k

def gen_target(n, num_clauses):
    target = []
    
    while len(target) == 0:
        s = Glucose42()
        for i in range(num_clauses):
            s.add_clause(random_clause(n))
             
        for m in s.enum_models():
            target.append(model2state(m))

        s.delete()

    return target

def plot(preset = 0):
    presets = [
        {"nv": 12, "nc": 36, "seed": 42},
        {"nv": 10, "nc": 36, "seed": 2},
        {"nv": 10, "nc": 40, "seed": 1},
        {"nv": 10, "nc": 40, "seed": 9},
        {"nv": 12, "nc": 44, "seed": 4},
        {"nv": 10, "nc": 40, "seed": 86},
        {"nv": 10, "nc": 40, "seed": 92},
    ]
    nv = presets[preset]["nv"]
    nc = presets[preset]["nc"]
    np.random.seed(presets[preset]["seed"])
    ts = gen_target(nv, nc)
    G = t_Graph(ts)
    sls = t_centered_layer_layout_even(ts)

    return hamdist_tikz(nv, G, sls, ts, nrows=2, ncols=4, highlight_level=2)
