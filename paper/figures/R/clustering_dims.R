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

calc_approx <- function(df_eds, df_cov, df_size_T) {
  theta <- seq(-pi / 2, pi / 2, length.out = 100)

  df_approx <- bind_rows(calc_EF(theta, 1.2, 8, df_eds, df_cov,
                                 df_size_T |> filter(n == 8) |>
                                 pull(size_T) |> first()) |>
                         mutate(n = 8, overlap = val),
                         calc_EF(theta, 1.2, 9, df_eds, df_cov,
                                 df_size_T |> filter(n == 9) |>
                                 pull(size_T) |> first()) |>
                         mutate(n = 9, overlap = val),
                         calc_EF(theta, 1.2, 10, df_eds, df_cov,
                                 df_size_T |> filter(n == 10) |>
                                 pull(size_T) |> first()) |>
                         mutate(n = 10, overlap = val),
                         calc_EF(theta, 1.2, 11, df_eds, df_cov,
                                 df_size_T |> filter(n == 11) |>
                                 pull(size_T) |> first()) |>
                         mutate(n = 11, overlap = val))
  df_approx
}

plot <- function() {
  df_exact <- read_csv("figures/links/clustered/outall") |>
              filter(n >= 8) 

  df_eds <- read_csv("figures/links/clustered/out_Eds")
  df_ed1d1 <- read_csv("figures/links/clustered/out_Ed1d2")

  df_size_T <- df_eds |>
               group_by(n) |>
               summarize(size_T = mean(nclusters) * mean(clustersize))

  df_approx <- calc_approx(df_eds, df_ed1d1, df_size_T) |>
               mutate(proc="1approx")
  
  df_mean <- df_exact |>
             group_by(n, theta) |>
             summarise(overlap = mean(overlap)) |>
             mutate(proc="0mean")

  df_lines <- bind_rows(df_approx, df_mean)

  dim_labeller <- function(string) paste0("n = ", string)

  method_labels = c("Expected", "Approximated")

  plot_fit <- df_exact |>
  ggplot(aes(x=theta, y=overlap)) +
  geom_bin_2d(bins=100)+
  facet_wrap(vars(n), scales = "fixed", ncol = 5, labeller = as_labeller(dim_labeller)) +
  #geom_line(data = df_exact |>
  #                 group_by(theta, n) |>
  #                 summarise(overlap = mean(overlap))) +
  geom_line(data = df_lines, mapping = aes(color = proc, linetype = proc)) +
  #scale_fill_continuous(high = "#333333",
  #                      low = "#bbbbbb") +
  scale_fill_continuous(high="#333333"
                       ,low="#bbbbbb"
                       ,guide = guide_colorbar(frame.colour = COLOURS.LIST[3])
                       ) + 
  scale_linetype_manual(name = "Landscape"
                       ,labels = method_labels
                       ,values = c(1,2)
                       ,guide = guide_legend(theme = theme(legend.direction = "horizontal"))
                       ) +
  scale_color_manual(name = "Landscape"
                       ,labels = method_labels
                       ,values = c(COLOURS.LIST[1], COLOURS.LIST[2])
                       ,guide = guide_legend(theme = theme(legend.direction = "horizontal"))
                       ) +
  labs(fill = "Value Frequency") +
  xlab(label = "$\\beta$") +
  ylab(label = "Value") +
  theme_light(base_size = 9) +
  theme(legend.position = "top"
       #,legend.title.position = "top" 
       )

  plot_err <- df_exact |> group_by(n, theta) |>
  summarise(meanoverlap = mean(overlap),
            sdoverlap = sd(overlap)) |>
  inner_join(df_approx, join_by(n, theta)) |> mutate(abserror = abs(overlap - meanoverlap)) |>
  ggplot(aes(x = theta)) +
  geom_line(aes(y=abserror, linetype="0abserror")) +
  geom_line(aes(y=sdoverlap, linetype="1sdF")) +
  facet_wrap(~n, ncol = 5, labeller = as_labeller(dim_labeller)) +
  xlab(label = "$\\beta$") +
  ylab(label = "Value") + 
  labs(linetype = "") +
  scale_y_log10(label = label_log()) + 
  guides(y = "axis_logticks") +
  theme_light(base_size = 9) +
  scale_linetype_manual(values = c(1,2 ),
                        labels = c("Absolute Approximation Error",
                                   "Standard Deviation of $F_1$")) +
  theme(legend.position = "bottom"
       ,legend.title.position = "top"
       ,legend.title = element_blank()
       )


  plot <- plot_fit / plot_err + plot_layout(axes = "collect")

  return(plot)
}

main <- function() write_tex_plot(plot(), "clustering_dims.tex", width = 7, height = 4)

if (!interactive()) {
  main()
}
