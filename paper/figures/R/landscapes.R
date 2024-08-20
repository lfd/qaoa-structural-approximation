library(ggplot2)
library(tibble)
library(purrr)
library(dplyr)
library(tikzDevice)
library(patchwork)
library(readr)
library(scales)


source("figures/R/cluster_landscape.R")
source("figures/R/uniform_landscape.R")
source("figures/R/sat_landscape.R")
source("figures/R/qrf_landscape.R")

plot <- function() {
    p_uniform <- unif_ldsc$plot()
    p_cluster <- clst_ldsc$plot()
    p_sat <- sat_ldsc$plot()
    p_qrf <- qrf_ldsc$plot()


    wrap_elements(p_uniform + plot_annotation(title = "Uniform Sampling")) /
    wrap_elements(p_cluster + plot_annotation(title = "Clustered Sampling"))/
    wrap_elements(p_sat + plot_annotation(title = "SAT")) /
    wrap_elements(p_qrf + plot_annotation(title = "$qr-\\text{FACTORING}$"))
}

main <- function() {
  p <- plot()

  options(tikzDocumentDeclaration = c(
                                 "\\documentclass[10pt]{standalone}", 
                                 "\\usepackage[T1]{fontenc}",
                                 "\\usepackage[utf8]{inputenc}",
                                 "\\usepackage[tt=false, type1=true]{libertine}",
                                 "\\usepackage[varqu]{zi4}",
                                 "\\usepackage[libertine]{newtxmath}"
                                 ))
  scale = 2
  tikz(file = "landscapes.tex", width = scale * 4.3, height = scale * 6.5, standAlone = TRUE)
  print(p)

  dev.off()
}

if (!interactive()) {
  main()
}
