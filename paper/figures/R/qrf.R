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
                 , "#1f78b5"
                 , "#009371")

plot <- function() {
  df_exact <- read_csv("figures/links/qrfactoring_approx/outall")


  df_eds <- read_csv("figures/links/qrfactoring_approx/out_Eds")
  df_ed1d2 <- read_csv("figures/links/qrfactoring_approx/out_Ed1d2")

  theta <- seq(-pi / 2, pi / 2, length.out = 100)

  df_approx <- calc_EF(theta, 1.2, 18, df_eds, df_ed1d2, 2) |>
               mutate(overlap = val)
  #df_approx <- read_csv("figures/links/qrfactoring_approx/outEF")

  plot_fit <- df_exact |> 
  filter(n == 18)|>
  ggplot(aes(x=theta, y=overlap)) +
  geom_bin_2d(aes(fill = after_stat(count / 100)), bins = 100) +
  geom_line(data = df_exact |> filter(n == 18) |>
                   group_by(theta) |>
                   summarise(overlap = mean(overlap)),
            mapping = aes(linetype = "0mean")) +
  geom_line(data = df_approx |> filter(n == 18),
            mapping = aes(linetype = "1approx"),
            color=COLOURS.LIST[2]) +
  scale_fill_continuous(high = "#333333", low = "#bbbbbb") +
  scale_y_continuous(label = label_log()) +
  xlab(label = "$\\beta$") +
  ylab(label = "Value") +
  labs(fill = "Value Frequency",
       linetype = "Landscape") + 
  scale_linetype_manual(values = c(1, 2),
                        labels = c("Expected", "Approximated")) +
  theme_light(base_size = 9) +
  theme(legend.position = "top",
        legend.title.position = "top") +
  guides(linetype = guide_legend(direction = "vertical")
        #,linetype = guide_legend(direction = "vertical") 
        ,fill = guide_colorbar(frame.colour = COLOURS.LIST[3])
        )

  plot_err <- df_exact |> filter(n == 18) |> group_by(theta) |>
  summarise(meanoverlap = mean(overlap),
            sdoverlap = sd(overlap)) |>
  inner_join(df_approx |> filter(n == 18), join_by(theta)) |>
  mutate(abserror = abs(overlap - meanoverlap)) |>
  ggplot(aes(x = theta)) +
  geom_line(aes(y=abserror, linetype="0error")) +
  geom_line(aes(y=sdoverlap, linetype="1stddev")) +
  scale_y_log10(label = label_log()) + 
  scale_linetype_manual(labels = c("Absolute Approximation Error", "Standard Deviation of $F_1$"),
                        values = c("solid", "dashed")) +
  xlab(label = "$\\beta$") +
  ylab(label = "Value") +
  labs(linetype = "") +
  theme_light(base_size = 9) +
  theme(legend.position = "bottom",
        legend.direction = "vertical",
        legend.title = element_blank(),
        legend.margin = margin(0, 0, 0, 0),
        legend.spacing.y = unit(0, "mm")) +
  guides(y = "axis_logticks")

  plot_fit / plot_err + plot_layout(axes = "collect")
}

main <- function() write_tex_plot(plot(), "qrf.tex", width = 3.4, height = 4)

if (!interactive()) {
  main()
}
