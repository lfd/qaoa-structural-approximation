library(ggplot2)
library(tibble)
library(purrr)
library(dplyr)
library(tikzDevice)
library(patchwork)
library(readr)
library(scales)

source("figures/R/util.R")

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
  df_uniform_eds <- read_csv("figures/links/uniform/out_Eds") |>
                    mutate(problem = "uniform")
  df_uniform_ed1d2 <- read_csv("figures/links/uniform/out_Ed1d2") |>
                      mutate(problem = "uniform")
  df_uniform_ldsc <- calc_EF(theta = seq(-pi/2, pi/2, length.out=100),
                         phi = seq(0, 2*pi, length.out=200),
                         n = 8,
                         df_eds = df_uniform_eds,
                         df_ed1d2 = df_uniform_ed1d2,
                         size_T = 2**7) |>
                     mutate(problem = "uniform")

  df_cluster <- read_csv("figures/links/clustered_preopt/out") |>
                mutate(problem = "cluster")
  df_cluster_eds <- read_csv("figures/links/clustered/out_Eds") |>
                    mutate(problem = "cluster")
  df_cluster_ed1d2 <- read_csv("figures/links/clustered/out_Ed1d2") |>
                      mutate(problem = "cluster")
  df_cluster_ldsc <- calc_EF(theta = seq(-pi/2, pi/2, length.out=100),
                         phi = seq(0, 2*pi, length.out=200),
                         n = 8,
                         df_eds = df_cluster_eds,
                         df_ed1d2 = df_cluster_ed1d2,
                         size_T = 90) |>
                     mutate(problem = "cluster")

  df_sat <- read_csv("figures/links/sat_preopt/out") |>
            mutate(problem = "sat")
  df_sat_eds <- read_csv("figures/links/sat/out_Eds") |>
                mutate(problem = "sat")
  df_sat_ed1d2 <- read_csv("figures/links/sat/out_Ed1d2") |>
                  mutate(problem = "sat")
  df_sat_ldsc <- calc_EF(theta = seq(-pi/2, pi/2, length.out=100),
                         phi = seq(0, 2*pi, length.out=200),
                         n = 8,
                         df_eds = df_sat_eds,
                         df_ed1d2 = df_sat_ed1d2,
                         size_T = 30) |>
                 mutate(problem = "sat")

  df_qrf <- read_csv("figures/links/qrf_preopt/out") |>
            mutate(problem = "qrf")
  df_qrf_eds <- read_csv("figures/links/qrfactoring_approx/out_Eds") |>
                mutate(problem = "qrf")
  df_qrf_ed1d2 <- read_csv("figures/links/qrfactoring_approx/out_Ed1d2") |>
                  mutate(problem = "qrf")
  df_qrf_ldsc <- calc_EF(theta = seq(-pi/2, pi/2, length.out=100),
                         phi = seq(0, 2*pi, length.out=200),
                         n = 12,
                         df_eds = df_qrf_eds,
                         df_ed1d2 = df_qrf_ed1d2,
                         size_T = 2) |>
                 mutate(problem = "qrf")

  df_ldsc <- list(df_uniform_ldsc, df_cluster_ldsc, df_sat_ldsc, df_qrf_ldsc) |>
             map(\(df) df |> select(theta, phi, val, problem)) |>
             bind_rows()

  df <- list(df_uniform, df_cluster, df_sat, df_qrf) |>
        map(\(df) df |> select(n, mangle, pangle, issolution, seed, opt, problem)) |>
        bind_rows()

  problem_labels <- c("uniform" = "Uniform"
                     ,"sat" = "SAT"
                     ,"qrf" = "$qr$-FACTORING"
                     ,"cluster" = "Clustered"
                     )

  ps <- df_ldsc$problem |>
  unique() |>
  map(\(p) df_ldsc |>
           filter(problem == p) |>
           ggplot(aes(x = theta, y = phi)) +
           geom_raster(aes(fill = val)) +
           geom_contour(aes(z = val),
                        color = "black") +
           geom_point(data = df |> filter(problem == p),
                      aes(x = mangle, y = pangle), shape = 4, color=COLOURS.LIST[6]) + 
           scale_fill_gradientn(colors = c("#1a1a1a", "#9F9F9F", "#FFFFFF")
                               #,trans="log10"
                               ) +
           #theme_light() + 
           #ggtitle(problem_labels[p]) +
           facet_wrap(~problem, labeller = as_labeller(problem_labels)) +
           labs(x = "$\\beta$"
               ,y = "$\\gamma$" 
               ,fill = "Value"
               )
     )

  ps |> reduce(\(a, b) a + b) + plot_layout(ncol = 4, axis = "collect") &
        theme_light(base_size = 9) & 
        theme(strip.text.x = element_text(margin = margin(1,0,1,0, "mm"))
             ,strip.text.y = element_text(margin = margin(0,1,0,1, "mm"))
             ,legend.position = "top"
             ,plot.title.position = "plot"
             ,legend.title.position = "top"
             ) &
        guides(fill = guide_colorbar(frame.colour = COLOURS.LIST[3]))
}

main <- function() write_tex_plot(plot(), "circopt_landscape.tex", width = 7, height = 2.9)

if (!interactive()) {
  main()
}
