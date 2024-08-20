library(ggplot2)
library(tibble)
library(purrr)
library(dplyr)
library(tikzDevice)
library(patchwork)
library(readr)
library(scales)


COLOURS.LIST <- c( "black" # nolint
                 , "#E69F00" # nolint
                 , "#999999"
                 , "#009371"
                 , "#beaed4"
                 , "#ed665a"
                 , "#1f78b4"
                 , "#009371")

plot <- function() {
  df <- read_csv("figures/links/sat_preopt/out") |>
        mutate(alpha = nclauses / n)

  #df |>
  #group_by(seed, opt, alpha) |>
  #summarize(hitrate = mean(issolution)) |>
  #ggplot(aes(y = opt, x = hitrate)) +
  #geom_boxplot() +
  #facet_grid(row=vars(alpha)) +
  #theme_light()
  #df |>

  df |>
  group_by(seed, opt, alpha) |>
  summarize(solfreq = mean(issolution)) |>
  ggplot(aes(x = solfreq, y = factor(alpha), fill = opt)) +
  geom_boxplot() +
  theme_light(base_size = 9) +
  scale_fill_manual(values = c("circopt" = "white", "preopt" = COLOURS.LIST[2]),
                    labels = c("circopt" = "Standard QAOA", "preopt" = "Non-Iterative QAOA")) + 
  labs(y = "$\\alpha$"
      ,x = "Solution Probability per Sample"
      ,fill = "Algorithm"
      ) +
  theme(legend.position = "top"
       ,legend.title = element_blank() 
       )
}

main <- function() {

  p <- plot()

  options(tikzDocumentDeclaration = c(
                                 "\\documentclass[10pt]{standalone}", 
                                 "\\usepackage[T1]{fontenc}",
                                 "\\usepackage[utf8]{inputenc}",
                                 "\\usepackage[tt=false, type1=true]{libertine}",
                                 "\\usepackage[varqu]{zi4}",
                                 "\\usepackage[libertine]{newtxmath}",
                                 "\\usepackage{physics2}",
                                 "\\usephysicsmodule{ab, ab.braket, diagmat, ab.legacy}"
                                 ))
  tikz(file = "circopt_vs_preopt_sat.tex", width = 3.4, height = 2, standAlone = TRUE)
  print(p)

  dev.off()
}

if (!interactive()) {
  main()
}
