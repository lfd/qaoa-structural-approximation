library(readr)
library(patchwork)
library(tikzDevice)
library(patchwork)
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

collect_eds <- function() {
  df_eds <- bind_rows(
    read_csv("figures/links/uniform/out_Eds") |>
    select(n, d, Eds) |>
    mutate(experiment = "uniform"),
    read_csv("figures/links/clustered/out_Eds") |>
    select(n, d, Eds) |>
    mutate(experiment = "clustered"),
    read_csv("figures/links/sat/out_Eds") |>
    select(n, d, Eds) |>
    mutate(experiment = "sat"),
    read_csv("figures/links/qrfactoring_approx/out_Eds") |>
    select(n, d, Eds) |>
    mutate(experiment = "qrf"),
  )

  return(df_eds)
}

collect_cov <- function() {
  df_cov <- bind_rows(
    read_csv("figures/links/uniform/out_Ed1d2") |>
    select(n, d1, d2, Cov) |>
    mutate(experiment = "uniform"),
    read_csv("figures/links/clustered/out_Ed1d2") |>
    select(n, d1, d2, Cov) |>
    mutate(experiment = "clustered"),
    read_csv("figures/links/sat/out_Ed1d2") |>
    select(n, d1, d2, Cov) |>
    mutate(experiment = "sat"),
    read_csv("figures/links/qrfactoring_approx/out_Ed1d2") |>
    select(n, d1, d2, Cov) |>
    mutate(experiment = "qrf"),
  )

  return(df_cov)
}

collect_data <- function() {
  theta <- seq(-pi/2, pi/2, length.out = 100)
  phi <- seq(0, 2*pi, length.out = 200)
 
  size_T_sat <- read_csv("figures/links/sat/outall") |>
                group_by(n) |>
                summarize(sizeT = mean(sizeT))

  df_ef <- bind_rows(
    seq(8,11) |>
    map_dfr(\(n) calc_EF(theta,
                         phi,
                         n,
                         read_csv("figures/links/uniform/out_Eds"),
                         read_csv("figures/links/uniform/out_Ed1d2"),
                         2^(n-1))) |>
    mutate(experiment = "uniform"),
    seq(8,11) |>
    map_dfr(\(n) calc_EF(theta,
                         phi,
                         n,
                         read_csv("figures/links/clustered/out_Eds"),
                         read_csv("figures/links/clustered/out_Ed1d2"),
                         90)) |>
    mutate(experiment = "clustered"),
    seq(8,11) |>
    map_dfr(\(nn) calc_EF(theta,
                         phi,
                         nn,
                         read_csv("figures/links/sat/out_Eds"),
                         read_csv("figures/links/sat/out_Ed1d2"),
                         size_T_sat |> filter(n == nn) |> pull(sizeT))) |>
    mutate(experiment = "sat"),
    c(12, 14, 16, 18) |>
    map_dfr(\(n) calc_EF(theta,
                         phi,
                         n,
                         read_csv("figures/links/qrfactoring_approx/out_Eds"),
                         read_csv("figures/links/qrfactoring_approx/out_Ed1d2"),
                         2)) |>
    mutate(experiment = "qrf"),
  )

  return(df_ef)
}

plot <- function() {
  df <- collect_data()


  problem_labels <- c("uniform" = "Uniform"
                     ,"sat" = "SAT"
                     ,"qrf" = "$qr$-FACTORING"
                     ,"clustered" = "Clustered"
                     ,"8" = "n = 8"
                     ,"9" = "n = 9"
                     ,"10" = "n = 10"
                     ,"11" = "n = 11"
                     ,"12" = "n = 8"
                     ,"14" = "n = 14"
                     ,"16" = "n = 16"
                     ,"18" = "n = 18"
                     )
  
  p1 <- df |>
        filter(experiment == "uniform") |>
        ggplot(aes(x = theta, y = phi)) +
        geom_raster(aes(fill = val)) + 
        geom_contour(aes(z = log10(val)),
                     linewidth = 0.5,
                     color="black") +
        facet_grid(rows = vars(experiment)
                  ,cols = vars(n)
                  ,labeller = as_labeller(problem_labels)
                  ) + 
        scale_fill_gradientn(colors = c("#1a1a1a", "#9F9F9F", "#FFFFFF"),
                             trans="log10") +
        theme_light(base_size = 9) +
        xlab(label = "$\\beta$") +
        ylab(label = "$\\gamma$") +
        labs(fill = "Approximated \n Landscape") +
        theme(strip.text.x = element_text(margin = margin(1,0,1,0, "mm"))
             ,strip.text.y = element_text(margin = margin(0,1,0,1, "mm"))
             ,aspect.ratio = 1
             ,axis.ticks.x = element_blank()
             ,axis.title.x = element_blank()
             ,axis.text.x = element_blank()
             ,legend.title = element_text(hjust = 0.5)
             ) 

  p2 <- df |>
        filter(experiment == "clustered") |>
        ggplot(aes(x = theta, y = phi)) +
        geom_raster(aes(fill = val)) + 
        geom_contour(aes(z = log10(val)),
                     linewidth = 0.5,
                     color="black") +
        facet_grid(rows = vars(experiment)
                  ,cols = vars(n)
                  ,labeller = as_labeller(problem_labels)
                  ) + 
        scale_fill_gradientn(colors = c("#1a1a1a", "#9F9F9F", "#FFFFFF"),
                             trans="log10") +
        theme_light(base_size = 9) +
        xlab(label = "$\\beta$") +
        ylab(label = "$\\gamma$") +
        labs(fill = "") +
        theme(strip.text.x = element_text(margin = margin(1,0,1,0, "mm"))
             ,strip.text.y = element_text(margin = margin(0,1,0,1, "mm"))
             ,aspect.ratio = 1
             ,axis.ticks.x = element_blank()
             ,axis.title.x = element_blank()
             ,axis.text.x = element_blank()
             )

  p3 <- df |>
        filter(experiment == "sat") |>
        ggplot(aes(x = theta, y = phi)) +
        geom_raster(aes(fill = val)) + 
        geom_contour(aes(z = log10(val)),
                     linewidth = 0.5,
                     color="black") +
        facet_grid(rows = vars(experiment)
                  ,cols = vars(n)
                  ,labeller = as_labeller(problem_labels)
                  ) + 
        scale_fill_gradientn(colors = c("#1a1a1a", "#9F9F9F", "#FFFFFF"),
                             trans="log10",
                             labels=label_log()) +
        theme_light(base_size = 9) +
        xlab(label = "$\\beta$") +
        ylab(label = "$\\gamma$") +
        labs(fill = "") +
        theme(strip.text.x = element_text(margin = margin(1,0,1,0, "mm"))
             ,strip.text.y = element_text(margin = margin(0,1,0,1, "mm"))
             ,aspect.ratio = 1
             ,axis.ticks.x = element_blank()
             ,axis.title.x = element_blank()
             ,axis.text.x = element_blank()
             )
        
  p4 <- df |>
        filter(experiment == "qrf") |>
        ggplot(aes(x = theta, y = phi)) +
        geom_raster(aes(fill = val)) + 
        geom_contour(aes(z = log10(val)),
                     linewidth = 0.5,
                     color="black") +
        facet_grid(rows = vars(experiment)
                  ,cols = vars(n)
                  ,labeller = as_labeller(problem_labels)
                  ) + 
        scale_fill_gradientn(colors = c("#1a1a1a", "#9F9F9F", "#FFFFFF"),
                             trans="log10",
                             labels=label_log()) +
        theme_light(base_size = 9) +
        xlab(label = "$\\beta$") +
        ylab(label = "$\\gamma$") +
        labs(fill = "") +
        theme(strip.text.x = element_text(margin = margin(1,0,1,0, "mm"))
             ,strip.text.y = element_text(margin = margin(0,1,0,1, "mm"))
             ,aspect.ratio = 1
             )

  layout <- "
  AAAA
  BBBB
  CCCC
  DDDD
  "
  p1 + p2 + p3 + p4 + plot_layout(design = layout, axes = "collect") &
        guides(fill = guide_colorbar(frame.colour = COLOURS.LIST[3]))
}

main <- function() write_tex_plot(plot(), "landscapes_facets.tex", width = 7, height = 7)

if (!interactive()) {
  main()
}
