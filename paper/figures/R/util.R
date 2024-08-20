
library(ggplot2)
library(tibble)
library(dplyr)
library(purrr)
library(stats)
library(functional)
library(extraDistr)
library(tikzDevice)

write_tex_plot <- function(plot, filename, width, height) {
  options(tikzDocumentDeclaration = c(
                                 "\\documentclass[aps,rpx,reprint]{revtex4-2}", 
                                 "\\usepackage[T1]{fontenc}",
                                 "\\usepackage[utf8]{inputenc}"
                                 ))
  tikz(file = filename, width = width, height = height, standAlone = TRUE)
  print(plot)

  dev.off()
}

f <- function(theta, n, d, conj = FALSE) {
  cos(theta)^(n - d) * (ifelse(conj, 1i, -1i) * sin(theta))^d
}

hamming_dist <- function(a, b) {
  bitwXor(a, b) |>
    intToBits() |>
    map_vec(as.integer) |>
    sum()
}

ck <- function(beta, phi, n, k, target) {
  f <- function(t, n, d) {
    cos(t)^(n - d) * (-1i * sin(t))^d
  }

  cphase <- function(z, target) ifelse(z %in% target, exp(-1i * phi), 1)
  term <- function(z) cphase(z, target) * f(beta, n, hamming_dist(z, k))

  seq(0, 2^n - 1) |> map(term) |> reduce(function(a, b) a + b)
}

surface_df <- function(theta, phi, n, k, T) {
    phi |>
    map_dfr(\(p) tibble(theta = theta,
                        z = abs(ck(theta, p, n, k, T))^2,
                        phi = p))
}

E_abs_ck_sqrd <- function(theta, phi, n, df_eds, df_ed1d2) {
  d1d2s <- seq(0,n) |> map(\(d1) seq(0, n) |> map(\(d2) c(d1, d2))) |>
                      reduce(\(a, b) c(a, b))

  df <- df_ed1d2 |>
        pmap(\(d1, d2, Ed1d2) tibble("d1" = d1,
                                     "d2" = d2,
                                     "Ed1d2" = Ed1d2,
                                     "Ed1" = df_eds |>
                                             filter(d == d1) |>
                                             pull(Eds),
                                     "Ed2" = df_eds |>
                                             filter(d == d2) |>
                                             pull(Eds))) |>
        bind_rows()
  #return(df)

  w <- function(n, d1, d2, Ed1, Ed2, Ed1d2, phi) {
    Ed1d2 * (exp(-1i * phi) - 1) * (exp(1i * phi) - 1) +
    Ed1 * (exp(-1i * phi) - 1) * choose(n, d2) +
    Ed2 * (exp(1i * phi) - 1) * choose(n, d1) +
    choose(n, d1) * choose(n, d2)
  }

  df |> pmap(\(d1, d2, Ed1d2, Ed1, Ed2) w(n, d1, d2, Ed1, Ed2, Ed1d2, phi) * 
                                      f(theta, n, d1) *
                                      Conj(f(theta, n, d2))) |>
        reduce(\(a, b) a + b)
}

Eck <- function(theta, phi, n, Eds) {
  seq(0, n) |>
  map(function(d) (Eds[d + 1] * (exp(-1i * phi) - 1) + choose(n, d)) * f(theta, n, d)) |> # nolint: line_length_linter
  reduce(\(a, b) a + b)
}

Eckabs <- function(theta, phi, n, Eds, df_cov) {
  abs(Eck(theta, phi, n, Eds))^2 +
  2 * (1 - cos(phi)) * 
  (df_cov |>
   pmap(\(d1, d2, Cov) Cov * f(theta, n, d1) * f(theta, n, d2, conj = TRUE)) |>
   reduce(\(a, b) a + b))
}

#calc_EF <- function(theta, phi, n, df_eds, df_cov, size_T) {
#  df_theta_phi <- phi |> map_dfr(\(phi) tibble(phi = phi, theta = theta))
#
#  nn <- n
#  df_theta_phi |> mutate(val = (size_T / 2^nn) * Eckabs(theta, phi, nn,
#                    df_eds |> filter(n == nn) |> pull(Eds),
#                    df_cov |> filter(n == nn) |> select(d1, d2, Cov))) |>
#  mutate(val = abs(val), n = n)
#}
#
#plot_EF <- function(theta, phi, n, df_eds, df_cov, size_T) {
#  df_theta_phi <- phi |> map_dfr(\(phi) tibble(phi = phi, theta = theta))
#
#  nn <- n
#  df_theta_phi |> mutate(val = (size_T / 2^nn) * Eckabs(theta, phi, nn,
#                    df_eds |> filter(n == nn) |> pull(Eds),
#                    df_cov |> filter(n == nn) |> select(d1, d2, Cov))) |>
#  ggplot(aes(x=theta, y=phi)) +
#  geom_raster(aes(fill = abs(val))) +
#  geom_contour(aes(z = abs(val)), linewidth = 0.5, color="black", bins=5)
#}

calc_EF <- function(theta, phi, n, df_eds, df_ed1d2, size_T) {
  df_theta_phi <- phi |> map_dfr(\(phi) tibble(phi = phi, theta = theta))

  nn <- n
  df_theta_phi |> mutate(val = (size_T / 2^nn) * E_abs_ck_sqrd(theta, phi, nn,
                    df_eds |> filter(n == nn) |> select(Eds, d),
                    df_ed1d2 |> filter(n == nn) |> select(d1, d2, Ed1d2))) |>
  mutate(val = abs(val), n = n)
}

plot_EF <- function(theta, phi, n, df_eds, df_cov, size_T) {
  df_theta_phi <- phi |> map_dfr(\(phi) tibble(phi = phi, theta = theta))

  nn <- n
  df_theta_phi |> mutate(val = (size_T / 2^nn) * E_abs_ck_sqrd(theta, phi, nn,
                    df_eds |> filter(n == nn) |> select(Eds, d),
                    df_cov |> filter(n == nn) |> select(d1, d2, Cov))) |>
  ggplot(aes(x=theta, y=phi)) +
  geom_raster(aes(fill = abs(val))) +
  geom_contour(aes(z = abs(val)), linewidth = 0.5, color="black", bins=5)
}


uniform_sampling <- new.env()

uniform_sampling$P_d <- Vectorize(function(size_T, n, d, k) {
  if(d == 0) {
    ifelse(k == 1, 1, 0)
  } else {
    dhyper(k, choose(n, d), 2^n - 1 - choose(n, d), size_T - 1)
  }
})

# d1 == d2 case?
uniform_sampling$P_d1_and_d2 <- Vectorize(function(size_T, n, d1, d2, k1, k2) {
  if(d1 == 0 || d2 == 0) {
    uniform_sampling$P_d(size_T, n, d1, k1) *
    uniform_sampling$P_d(size_T, n, d2, k2)
  } else if (d1 == d2) {
    ifelse(k1 != k2, 0, uniform_sampling$P_d(size_T, n, d1, k1))
  } else {
    dmvhyper(c(k1,
               k2,
               size_T - 1 - k1 - k2),
             c(choose(n, d1),
               choose(n, d2),
               2^n - 1 - choose(n, d1) - choose(n, d2)),
             size_T - 1)
  }
})

uniform_sampling$P_d1d2 <- Vectorize(function(size_T, n, d1, d2, k) {
  seq(0, size_T) |>
  map(function(d1) seq(0, size_T) |> map(function(d2) c(d1, d2))) |>
  flatten() |>
  Curry(Filter, function(ks) ks[1] * ks[2] == k)() |>
  map_vec(function(ks) uniform_sampling$P_d1_and_d2(size_T, n, d1, d2, ks[1], ks[2])) |>
  sum()
})

uniform_sampling$E_d <- Vectorize(function(size_T, n, d) {
  #seq(0, size_T) |>
  #map_vec(\(k) k * uniform_sampling$P_d(size_T, n, d, k)) |>
  #sum()
  ifelse(d == 0, 1, size_T * choose(n, d) / 2^n)
})

uniform_sampling$E_d1d2 <- Vectorize(function(size_T, n, d1, d2) {
    seq(0, size_T^2) |>
    map_vec(function(k) k * uniform_sampling$P_d1d2(size_T, n, d1, d2, k)) |>
    sum()
})

uniform_sampling$cov <- Vectorize(function(size_T, n, d1, d2) {
  if (d1 == 0 || d2 == 0) {
    return(0)
  } else if (d1 == d2) {
    return(uniform_sampling$var(size_T, n, d1))
  } else {
    return(-1 * size_T * ((2^n - size_T) / (2^n - 1)) *
           ((choose(n, d1) * choose(n, d2)) / 2^(2 * n)))
  }
})

uniform_sampling$var <- Vectorize(function(size_T, n, d) {
  size_T * ((2^n - size_T) / (2^n - 1)) *
    (choose(n, d) / 2^n) * (1 - choose(n, d) / 2^n)
})

uniform_sampling$df_cov <- function(size_T, n) {
  #seq(0, n) |>
  #map_dfr(\(d1) tibble(d1 = d1, d2 = seq(0, n))) |>
  #mutate(Cov = uniform_sampling$E_d1d2(size_T, n, d1, d2) -
  #             uniform_sampling$E_d(size_T, n, d1) *
  #             uniform_sampling$E_d(size_T, n, d2),
  #       n = n)
  seq(0, n) |>
  map_dfr(\(d1) tibble(d1 = d1, d2 = seq(0, n))) |>
  mutate(Cov = uniform_sampling$cov(size_T, n, d1, d2),
         n = n)
}

uniform_sampling$df_eds <- function(size_T, n) {
    ds <- seq(0, n)
    tibble(n = n, d = ds, Eds= uniform_sampling$E_d(size_T, n, ds))
}
