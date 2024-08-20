library(ggplot2)
library(tibble)
library(purrr)
library(dplyr)
library(tikzDevice)
library(patchwork)
library(readr)
library(scales)

source("figures/R/util.R")

hamming_dist <- function(a, b) {
  bitwXor(a, b) |>
    intToBits() |>
    map_vec(as.integer) |>
    sum()
}

ck <- function(theta, phi, n, k, target) {
  cphase <- function(z, target) ifelse(z %in% target, exp(-1i * phi), 1)
  term <- function(z) cphase(z, target) * f(theta, n, hamming_dist(z, k))

  seq(0, 2^n - 1) |> map(term) |> reduce(function(a, b) a + b)
}

COLOURS.LIST <- c( "black" # nolint
                 , "#E69F00" # nolint
                 , "#999999"
                 , "#009371"
                 , "#beaed4"
                 , "#ed665a"
                 , "#1f78b4"
                 , "#009371")

plot <- function() {
  nn <- 9
  df_exact <- read_csv("figures/links/sat/outall") 
  
  df_eds <- read_csv("figures/links/sat/out_Eds")
  df_ed1d2 <- read_csv("figures/links/sat/out_Ed1d2")
 
  #theta <- seq(-pi / 2, pi / 2, length.out = 100)
  #theta <- seq(0, pi, length.out = 100)
  ts <- df_exact |> pull(theta) |> unique()

  df_approx <- calc_EF(ts,
                       1.2,
                       nn,
                       df_eds,
                       df_ed1d2,
                       df_exact |> filter(n == nn) |> pull(sizeT) |> mean()) |>
                mutate(overlap = val) |>
                select(theta, overlap) |>
                mutate(proc="1approx")
  df_mean <- df_exact |>
             filter(n == nn) |>
             group_by(theta) |>
             summarize(overlap = mean(overlap)) |>
             mutate(proc="0mean")

  df <- bind_rows(df_approx, df_mean)

  method_labels = c("Expected", "Approximated")

  plot_hist <- df_exact |>
      filter(n == nn) |>
      ggplot(aes(x = theta, y = overlap)) +
      geom_bin_2d(aes(fill = after_stat(count / 500)), bins = 100) +
      scale_fill_continuous(high="#101010"
                           ,low="#dddddd"
                           ,guide = guide_colorbar(frame.colour = COLOURS.LIST[3])
                           ) + 
      geom_line(data = df, aes(color = proc, linetype = proc), linewidth = 1.5) +
      scale_color_manual(name = "Landscape"
                        ,labels = method_labels
                        ,values = c(COLOURS.LIST[1], COLOURS.LIST[2])
                        ,guide = guide_legend(theme = theme(legend.direction = "vertical"))
                        ) +
      scale_linetype_manual(name = "Landscape"
                           ,labels = method_labels
                           ,values = c(1,2)
                           ,guide = guide_legend(theme = theme(legend.direction = "vertical"))
                           ) +
      labs(fill = "Value Frequency") +
      theme_light(base_size = 9) +
      labs(x = "$\\beta$",
           y = "Value") +
      theme(legend.position = "top"
           ,legend.title.position = "top" 
           )

    
  plot_hist
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
  tikz(file = "sat_cross_section.tex", width = 3.4, height = 3, standAlone = TRUE)
  print(p)

  dev.off()
}

main <- function() write_tex_plot(plot(), "sat_cross_section.tex", width = 3.4, height = 3)

if (!interactive()) {
  main()
}
