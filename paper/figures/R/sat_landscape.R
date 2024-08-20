library(ggplot2)
library(tibble)
library(purrr)
library(dplyr)
library(tikzDevice)
library(patchwork)
library(readr)
library(scales)

source("figures/R/util.R")

sat_ldsc <- new.env()

sat_ldsc$plotn <- function(n, df_eds, df_cov, size_T) {
  beta <- seq(-pi / 2, pi / 2, length.out = 100)
  gamma <- seq(0, 2 * pi, length.out = 200)

  df_ef <- calc_EF(beta, gamma, n, df_eds, df_cov, size_T)
  plot_EF(beta, gamma, n, df_eds, df_cov, size_T) +
  theme_light() +
  scale_fill_gradientn(colors = c("#1a1a1a", "#9F9F9F", "#FFFFFF"),
                       values = rescale(c(min(df_ef$val), size_T / 2^n, max(df_ef$val)))) +
  ggtitle(sprintf("$n = %d$", n)) +
  labs(x = "$\\beta$",
       y = "$\\gamma$",
       fill = "$\\tilde{E}(F_1)$")
}

sat_ldsc$plot <- function() {
  df_eds <- read_csv("figures/links/sat/out_Eds")
  df_cov <- read_csv("figures/links/sat/out_Covds")
  size_T <- read_csv("figures/links/sat/outall") |> 
            group_by(n) |>
            summarize(sizeT = mean(sizeT))

  
  #pn07 <- plotn(7, df_eds, df_cov)
  pn08 <- sat_ldsc$plotn(8,
                         df_eds,
                         df_cov,
                         size_T |>
                         filter(n == 8) |>
                         pull(sizeT)) +
          theme(legend.position = "bottom")
  pn09 <- sat_ldsc$plotn(9,
                         df_eds,
                         df_cov,
                         size_T |>
                         filter(n == 9) |>
                         pull(sizeT)) +
          theme(axis.title.y = element_blank(),
                axis.ticks.y = element_blank(),
                axis.text.y = element_blank(),
                legend.position = "bottom")
  pn10 <- sat_ldsc$plotn(10,
                         df_eds,
                         df_cov,
                         size_T |>
                         filter(n == 10) |>
                         pull(sizeT)) +
          theme(axis.title.y = element_blank(),
                axis.ticks.y = element_blank(),
                axis.text.y = element_blank(),
                legend.position = "bottom")
  pn11 <- sat_ldsc$plotn(11,
                         df_eds,
                         df_cov, 
                         size_T |>
                         filter(n == 11) |>
                         pull(sizeT)) +
          theme(axis.title.y = element_blank(),
                axis.ticks.y = element_blank(),
                axis.text.y = element_blank(),
                legend.position = "bottom")

  p <- pn08 | pn09 | pn10 | pn11

  return(p)
}

main <- function() {
  p <- sat_ldsc$plot()

  options(tikzDocumentDeclaration = c(
                                 "\\documentclass[10pt]{standalone}", 
                                 "\\usepackage[T1]{fontenc}",
                                 "\\usepackage[utf8]{inputenc}",
                                 "\\usepackage[tt=false, type1=true]{libertine}",
                                 "\\usepackage[varqu]{zi4}",
                                 "\\usepackage[libertine]{newtxmath}"
                                 ))
  tikz(file = "sat_landscape.tex", width = 5.5, height = 4.7, standAlone = TRUE)
  print(p)

  dev.off()
}

if (!interactive()) {
  main()
}
