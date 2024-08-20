library(ggplot2)
library(tibble)
library(purrr)
library(dplyr)
library(tikzDevice)
library(patchwork)
library(readr)
library(scales)

source("figures/R/util.R")

unif_ldsc <- new.env()

unif_ldsc$plotn <- function(n, df_eds, df_cov) {
  beta <- seq(-pi / 2, pi / 2, length.out = 100)
  gamma <- seq(0, 2 * pi, length.out = 200)

  df_ef <- calc_EF(beta, gamma, n, df_eds, df_cov, 2^(n-1))
  plot_EF(beta, gamma, n, df_eds, df_cov, 2^(n-1)) +
  theme_light() +
  scale_fill_gradientn(colors = c("#1a1a1a", "#9F9F9F", "#FFFFFF"),
                       values = rescale(c(min(df_ef$val), 1/2, max(df_ef$val)))) +
  ggtitle(sprintf("$n = %d$", n)) +
  labs(x = "$\\beta$",
       y = "$\\gamma$",
       fill = "$\\tilde{E}(F_1)$")
}

unif_ldsc$plot <- function() {
  df_eds <- read_csv("figures/links/uniform/out_Eds")
  df_cov <- read_csv("figures/links/uniform/out_Covds")

  #pn07 <- plotn(7, df_eds, df_cov)
  pn08 <- unif_ldsc$plotn(8, df_eds, df_cov) +
          theme(legend.position = "bottom")
  pn09 <- unif_ldsc$plotn(9, df_eds, df_cov) +
          theme(axis.title.y = element_blank(),
                axis.ticks.y = element_blank(),
                axis.text.y = element_blank(),
                legend.position = "bottom")
  pn10 <- unif_ldsc$plotn(10, df_eds, df_cov) +
          theme(axis.title.y = element_blank(),
                axis.ticks.y = element_blank(),
                axis.text.y = element_blank(),
                legend.position = "bottom")
  pn11 <- unif_ldsc$plotn(11, df_eds, df_cov) +
          theme(axis.title.y = element_blank(),
                axis.ticks.y = element_blank(),
                axis.text.y = element_blank(),
                legend.position = "bottom")

  p <- pn08 | pn09 | pn10 | pn11

  return(p)
}

main <- function() {
  p <- unif_ldsc$plot()

  options(tikzDocumentDeclaration = c(
                                 "\\documentclass[10pt]{standalone}", 
                                 "\\usepackage[T1]{fontenc}",
                                 "\\usepackage[utf8]{inputenc}",
                                 "\\usepackage[tt=false, type1=true]{libertine}",
                                 "\\usepackage[varqu]{zi4}",
                                 "\\usepackage[libertine]{newtxmath}"
                                 ))
  tikz(file = "uniform_landscape.tex", width = 5.5, height = 4.7, standAlone = TRUE)
  print(p)

  dev.off()
}

if (!interactive()) {
  main()
}
