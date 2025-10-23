from hamdist_shells import *

def main():
    preamble = """
    \\documentclass[aps,rpx,reprint,amsmath,amssymb,a4paper,noarxiv]{quantumarticle}

    \\usepackage[active,tightpage,psfixbb]{preview}
    \\usepackage{nameref}
    \\renewcommand{\\PreviewBbAdjust}{0pt 0pt 4pt 0pt}
    \\usepackage[T1]{fontenc}
    \\usepackage[utf8]{inputenc}
    \\usepackage{tikz}
    \\definecolor{lfd1}{HTML}{FFFFFF} % For background use, white is colour 1
    \\definecolor{lfd2}{HTML}{E69F00}
    \\definecolor{lfd3}{HTML}{999999}
    \\definecolor{lfd4}{HTML}{009371}
    \\usepackage{makecell}
    """

    ps = plot()

    latex_str = f"""
    {preamble}
    \\begin{{document}}
    \\begin{{preview}}
    {ps[1]}
    \\end{{preview}}
    \\end{{document}}
    """

    with open("hamdist_layers_top.tex", "w") as latex_file:
        latex_file.write(latex_str)


if __name__ == "__main__":
    main()
