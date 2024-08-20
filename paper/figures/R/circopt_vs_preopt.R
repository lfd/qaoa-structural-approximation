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
  df_uniform <- read_csv("figures/links/uniform_preopt/out") |>
                mutate(problem = "uniform")
  df_cluster <- read_csv("figures/links/clustered_preopt/out") |>
                mutate(problem = "cluster")
  df_sat <- read_csv("figures/links/sat_preopt/out") |>
            mutate(problem = "sat")
  df_qrf <- read_csv("figures/links/qrf_preopt/out") |>
            mutate(problem = "qrf")

  df <- list(df_uniform, df_cluster, df_sat, df_qrf) |>
        map(\(df) df |> select(n, mangle, pangle, issolution, seed, opt, problem)) |>
        bind_rows()

  problem_labels <- c("uniform" = "Uniform"
                     ,"sat" = "SAT"
                     ,"qrf" = "$qr$-FACTORING"
                     ,"cluster" = "Clustered"
                     )

  algorithm_labels <- c("circopt" = "Standard QAOA"
                       ,"preopt" = "Non-Iterative QAOA" 
                       )
  p_all <- df |>
  group_by(seed, opt, problem) |>
  summarize(solfreq = mean(issolution)) |>
  ggplot(aes(y = problem, x = solfreq, fill = opt)) +
  geom_boxplot() +
  theme_light(base_size = 9) +
  scale_fill_manual(values = c("circopt" = "white", "preopt" = COLOURS.LIST[2]),
                    labels = algorithm_labels) + 
  scale_y_discrete(labels = problem_labels) +
  labs(x = "Solution Probability per Sample"
      ,y = "Problem"
      ,fill = "Algorithm"
      ) +
  theme(legend.position = "top"
       ,axis.title.y = element_blank() 
       ,legend.title = element_blank()
       ,legend.title.position = "top" 
       )

  p_qrf <- df |>
           filter(problem == "qrf") |>
           group_by(seed, opt, problem) |>
           summarize(solfreq = mean(issolution)) |>
           ggplot(aes(y = problem, x = solfreq, fill = opt)) +
           geom_boxplot() +
           theme_light(base_size = 9) + 
           scale_fill_manual(values = c("circopt" = "white", "preopt" = COLOURS.LIST[2]),
                             labels = algorithm_labels) + 
           scale_y_discrete(labels = problem_labels) +
           labs(x = "Solution Probability per Sample"
               ) +
           theme(legend.position = "none"
                ,axis.title.y = element_blank() 
                ,plot.title = element_text(size = 11)
                )           

  layout <- "
  AA
  AA
  AA
  AA
  BB
  "
  p_all + p_qrf + plot_layout(design = layout, axes = "collect")
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
  tikz(file = "circopt_vs_preopt.tex", width = 3.4, height = 3, standAlone = TRUE)
  print(p)

  dev.off()
}

if (!interactive()) {
  main()
}
