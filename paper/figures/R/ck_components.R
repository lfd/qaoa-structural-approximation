library(ggplot2)
library(tibble)
library(purrr)
library(dplyr)
library(tikzDevice)
library(patchwork)

source("figures/R/util.R")

f <- function(t, n, d) {
  cos(t)^(n - d) * (-1i * sin(t))^d
}

hamming_dist <- function(a, b) {
  bitwXor(a, b) |>
    intToBits() |>
    map_vec(as.integer) |>
    sum()
}

ck <- function(beta, phi, n, k, target) {
  cphase <- function(z, target) ifelse(z %in% target, exp(-1i * phi), 1)
  term <- function(z) cphase(z, target) * f(beta, n, hamming_dist(z, k))

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
  ts <- seq(-pi / 2, pi / 2, length.out = 100)
  phi <- 1.2
  target <- c(14, 10, 13)
  n <- 5

  df <- target |>
        map(function(k) tibble(ts=ts, ck=abs(ck(ts, phi, n, k, target))^2, k=k)) |> # nolint
        bind_rows()

  plot_1 <- df |>
    ggplot(aes(x = ts, y = ck)) +
    geom_line(aes(color=factor(k),
                  linetype = "$|c_k|^2$")) +
    geom_line(aes(linetype = "$\\overline{\\left|c_k\\right|^2}$"),
              data = df |> group_by(ts) |> summarise(ck = mean(ck)),
              size=1.2) + 
    #geom_line(data = df |> group_by(ts) |> summarise(ck = sum(ck) / 2^5),
    #          linetype = 3) +
    scale_linetype_manual(values = c(2,1)) +
    theme_light(base_size = 9) +
    xlab(label = "$\\beta$") +
    #ylab(label = "$|c_k|^2$") +
    ylab(label = "Value") +
    labs(linetype = "") +
    scale_color_manual(values = c(COLOURS.LIST[2], COLOURS.LIST[4], COLOURS.LIST[5])
                      #,guide = guide_legend(theme = theme(legend.direction = "vertical"))
                      ) +
    labs(color = "$k$-component") + 
    theme(legend.spacing.y = unit(0, "cm")
         ,legend.position = "top"
         #,legend.direction = "vertical"
         ,legend.box = "vertical"
         )

  plot_2 <- df |> group_by(ts) |>
            summarise(ckmean = (length(target) / 2^n) * mean(ck),
                      cksum = sum(ck) / 2^n) |>
            ggplot(aes(x = ts)) +
            geom_line(aes(y = cksum, linetype = "$\\frac{1}{2^n} \\sum_{k \\in T} |c_k|^2$"),
                      color = COLOURS.LIST[3],
                      size = 0.8) +
            geom_line(aes(y = ckmean, linetype = "$\\frac{|T|}{2^n} \\overline{|c_k|^2}$"),
                      size = 1.5) +
            #scale_linetype_manual(c(, )) +
            scale_linetype_manual(values = c("dashed", "solid")) +
            xlab(label = "$\\beta$") +
            ylab(label = "") +
            theme_light() +
            theme(legend.position = "top")

  plot <- plot_1 #| plot_2

  return(plot)
}

main <- function() write_tex_plot(plot(), "ck_components.tex", width = 3.4, height = 2.5)

if (!interactive()) {
  main()
}
