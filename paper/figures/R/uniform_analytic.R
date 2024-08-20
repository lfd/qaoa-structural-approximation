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
  nn <- 8 
  df_exact <- read_csv("figures/links/uniform/outall") |>
              filter(n == nn) |>
              select(theta, overlap) 

  df_eds <- read_csv("figures/links/uniform/out_Eds")
  df_ed1d2 <- read_csv("figures/links/uniform/out_Ed1d2")

  size_T <- df_eds |>
            group_by(n) |>
            summarize(size_T = 2^first(n) * first(sizeRatio)) |>
            filter(n == nn) |>
            pull(size_T)

  theta <- seq(-pi / 2, pi / 2, length.out = 100)

  df_approx <- calc_EF(theta, 1.2, nn, df_eds, df_ed1d2, size_T) |>
               mutate(overlap = val) |>
               select(theta, overlap) |>
               mutate(proc="1sample")

  #df_approx <- read_csv("figures/links/uniform/outEF") |>
  #             filter(n == nn) |>
  #             select(theta, overlap) |>
  #             mutate(proc="1sample")

  pull_ed <- function(df_eds, dd) df_eds |> filter(d==dd) |> pull(Eds)

  df_eds <- uniform_sampling$df_eds(2^(nn - 1), nn)
  df_cov <- uniform_sampling$df_cov(2^(nn - 1), nn)
  df_ed1d2 <- df_cov |>
              pmap(\(n, d1, d2, Cov) tibble("n"=n,
                                            "d1"=d1,
                                            "d2"=d2,
                                            "Ed1d2" = pull_ed(df_eds, d1) *
                                                      pull_ed(df_eds, d2) +
                                                      #((n - 1) / n) * Cov)) |>
                                                        Cov)) |>
              bind_rows()

  df_an <- calc_EF(theta,
                   1.2,
                   nn,
                   df_eds,
                   df_ed1d2,
                   2^(nn - 1)) |>
           mutate(overlap = val) |>
           select(theta, overlap) |>
           mutate(proc="2analytic")

  df <- bind_rows(df_exact |>
                    group_by(theta) |>
                    summarize(overlap = mean(overlap)) |>
                    mutate(proc = "0mean"),
                  df_approx,
                  df_an)

  method_labels = c("Expected", "Approximated (Empirical Sampling)", "Approximated  (Analytical Model)")

  plot_hist <- df_exact |>
      ggplot(aes(x = theta, y = overlap)) +
      geom_bin_2d(bins = 100, show.legend = FALSE) +
      scale_fill_continuous(high="#101010", low="#dddddd") + 
      scale_y_continuous(position = "right") +
      theme_light(base_size = 9) +
      labs(x = "$\\beta$",
           y = "Value")

  plot_lines <- df_exact |>
      ggplot(aes(x = theta, y = overlap)) +
      geom_line(data = df, aes(color = proc, linetype = proc), linewidth = 1.5) +
      scale_color_manual(name = "Landscape",
                         labels = method_labels,
                         values = c(COLOURS.LIST[1], COLOURS.LIST[2], COLOURS.LIST[4])) +
      scale_linetype_manual(name = "Landscape",
                            labels = method_labels,
                            values = c("solid","7111","22")) +
      theme_light(base_size = 9) +
      scale_y_continuous(position = "right") +
      labs(x = "$\\beta$",
           y = "Value") +
      theme(legend.position = "top"
           ,legend.title.position = "top"
           )

  df_eds_sampled <- read_csv("figures/links/uniform/out_Eds") |> filter(n == nn)
  df_ed1d2_sampled <- read_csv("figures/links/uniform/out_Ed1d2") |> filter(n == nn) 

  df_lndscp_an <- calc_EF(seq(-pi/2, pi/2, length.out=100),
                          seq(0, 2*pi, length.out = 200),
                          nn,
                          df_eds,
                          df_ed1d2,
                          2^(nn - 1)) |>
                  mutate(landscape = "modeled")

  df_lndscp_sm <- calc_EF(seq(-pi/2, pi/2, length.out=100),
                          seq(0, 2*pi, length.out = 200),
                          nn,
                          df_eds_sampled,
                          df_ed1d2_sampled,
                          2^(nn - 1)) |>
                  mutate(landscape = "sampled")

  df_lndscp_dif <- df_lndscp_sm |>
                   select(phi, theta, val) |>
                   inner_join(df_lndscp_an |>
                              select(phi, theta, val),
                              by = join_by(phi, theta)) |>
                   mutate(val = val.x - val.y, 
                          landscape = "diff",
                          n = 5) |>
                   select(phi, theta, val, n, landscape)
 
  df_landscape = bind_rows(df_lndscp_an, 
                           df_lndscp_sm)

  plot_landscape <- df_landscape |>
                    ggplot(aes(x = theta, y = phi)) +
                    geom_raster(aes(fill = val)) +
                    geom_contour(aes(z = val), color="black", bins=7) + 
                    geom_hline(data = tibble(landscape = c("modeled", "sampled"),
                                             crosssection = c(1.2, 1.2)),
                               aes(yintercept = crosssection, color = landscape, linetype = landscape),
                               linewidth = 1.5) + 
                    facet_wrap(~landscape
                              ,ncol = 1
                              , labeller = as_labeller(c(`modeled` = "Analytical Model", `sampled` = "Empirical Sampling"))
                              ) +
                    theme_light(base_size = 9) +
                    scale_fill_gradientn(colors = c("#1a1a1a", "#9F9F9F", "#FFFFFF")
                                        ,values = rescale(c(min(df_landscape$val), mean(df_landscape$val), max(df_landscape$val)))
                                        ,guide = guide_colorbar(frame.colour = COLOURS.LIST[3])
                                        ) +
                    scale_color_manual(values = c(COLOURS.LIST[4], COLOURS.LIST[2]),
                                       guide = "none") +
                    scale_linetype_manual(values = c("22", "7111"),
                                          guide = "none") +
                    labs(x = "$\\beta$",
                         y = "$\\gamma$",
                         fill = "Approximated Landscape $\\tilde{E}(F_1)$") +
                    theme(legend.position = "top"
                         ,legend.title.position = "top"
                         ,legend.box.just = "center"
                         )

  #plot_diff <- df_lndscp_dif |>
  #             ggplot(aes(x = theta, y = phi)) +
  #             geom_raster(aes(fill = val)) +
  #             geom_contour(aes(z = val), color="black", bins=7) + 
  #             facet_wrap(~landscape) +
  #             theme_light(base_size = 9) +
  #             scale_fill_gradientn(colors = c("#1a1a1a", "#9F9F9F", "#FFFFFF"),
  #                                  values = rescale(c(min(df_landscape$val), mean(df_landscape$val), max(df_landscape$val)))) +
  #             labs(x = "$\\beta$",
  #                  y = "$\\gamma$",
  #                  fill = "") +
  #             theme(legend.position = "bottom",
  #                  ,axis.text.y = element_blank()
  #                  ,axis.ticks.y = element_blank()
  #                  ,axis.title.y = element_blank()
  ##                  )

  layout <- "
  AABBBBB
  AACCCCC
  "
   plot_landscape + plot_hist + plot_lines + plot_layout(guides = "collect", design = layout, axes = "collect") & 
       theme(legend.position = "top"
            )
}

main <- function() write_tex_plot(plot(), "uniform_analytic.tex", width = 7, height = 5)

if (!interactive()) {
  main()
}
