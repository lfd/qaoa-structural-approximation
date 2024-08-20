library(ggplot2)
library(tibble)
library(purrr)
library(dplyr)
library(tikzDevice)
library(patchwork)
library(readr)
library(scales)

source("figures/R/util.R")

qrf_ldsc <- new.env()

qrf_ldsc$plotn <- function(n, df_eds, df_cov) {
  beta <- seq(-pi / 2, pi / 2, length.out = 100)
  gamma <- seq(0, 2 * pi, length.out = 200)

  df_ef <- calc_EF(beta, gamma, n, df_eds, df_cov, 2)
  plot_EF(beta, gamma, n, df_eds, df_cov, 2) +
  theme_light() +
  scale_fill_gradientn(colors = c("#1a1a1a", "#9F9F9F", "#FFFFFF"),
                       values = rescale(c(min(df_ef$val), 2 / 2^n, max(df_ef$val)))) +
  ggtitle(sprintf("$n = %d$", n)) +
  labs(x = "$\\beta$",
       y = "$\\gamma$",
       fill = "$\\tilde{E}(F_1)$")
}

qrf_ldsc$plot <- function() {
  df_eds <- read_csv("figures/links/qrfactoring_approx/out_Eds")
  df_cov <- read_csv("figures/links/qrfactoring_approx/out_Covds")

  #pn07 <- plotn(7, df_eds, df_cov)
  pn12 <- qrf_ldsc$plotn(12, df_eds, df_cov) +
          theme(legend.position = "bottom")
  pn14 <- qrf_ldsc$plotn(14, df_eds, df_cov) +
          theme(axis.title.y = element_blank(),
                axis.ticks.y = element_blank(),
                axis.text.y = element_blank(),
                legend.position = "bottom")
  pn16 <- qrf_ldsc$plotn(16, df_eds, df_cov) +
          theme(axis.title.y = element_blank(),
                axis.ticks.y = element_blank(),
                axis.text.y = element_blank(),
                legend.position = "bottom")
  pn18 <- qrf_ldsc$plotn(18, df_eds, df_cov) +
          theme(axis.title.y = element_blank(),
                axis.ticks.y = element_blank(),
                axis.text.y = element_blank(),
                legend.position = "bottom")

  p <- pn12 | pn14 | pn16 | pn18

  return(p)
}

main <- function() {
  p <- qrf_ldsc$plot()

  options(tikzDocumentDeclaration = c(
                                 "\\documentclass[10pt]{standalone}", 
                                 "\\usepackage[T1]{fontenc}",
                                 "\\usepackage[utf8]{inputenc}",
                                 "\\usepackage[tt=false, type1=true]{libertine}",
                                 "\\usepackage[varqu]{zi4}",
                                 "\\usepackage[libertine]{newtxmath}"
                                 ))
  tikz(file = "qrf_landscape.tex", width = 5.5, height = 4.7, standAlone = TRUE)
  print(p)

  dev.off()
}

if (!interactive()) {
  main()
}
