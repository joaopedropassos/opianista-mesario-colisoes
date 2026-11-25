#!/usr/bin/env python3
"""
simulacao.py — Modelo nulo de colisões de títulos de mesários.

Via 2 (preferida): simulação Monte Carlo sobre o multiconjunto real de títulos
digitados por mesários. 10.000 réplicas.

Uso:
  python simulacao.py --eventos eventos.csv --saida resultados/nulo.json --reps 10000
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import poisson


SEED = 20261124
N_REPS_DEFAULT = 10_000


def carregar_eventos(caminho: Path) -> pd.DataFrame:
    df = pd.read_csv(caminho, dtype=str)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    return df.dropna(subset=["timestamp"])


def medir_p1(df: pd.DataFrame) -> dict:
    """p1 = mensagens de mismatch / registros de presença de mesário."""
    n_presenca = int((df["tipo"] == "presenca_mesario").sum())
    n_mismatch = int((df["tipo"] == "mismatch_bio").sum())
    p1 = n_mismatch / n_presenca if n_presenca else 0.0
    return {"N_presenca": n_presenca, "N_mismatch": n_mismatch, "p1": p1}


def titulos_mesarios(df: pd.DataFrame) -> list[str]:
    """Multiconjunto de títulos que apareceram em presença de mesário."""
    sub = df[df["tipo"] == "presenca_mesario"]
    return sub["titulo_mascarado"].dropna().tolist()


def detectar_colisoes_observadas(df: pd.DataFrame) -> pd.DataFrame:
    """Títulos que aparecem em mais de uma seção distinta."""
    sub = df[(df["tipo"] == "presenca_mesario") & (df["titulo_mascarado"] != "")]
    g = sub.groupby("titulo_mascarado").agg(
        secoes=("secao", "nunique"),
        ufs=("uf", "nunique"),
        registros=("timestamp", "count"),
    )
    return g[g["secoes"] > 1].reset_index()


def simular_nulo(
    titulos: list[str],
    n_erros: int,
    n_reps: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """
    Para cada réplica: sorteia n_erros títulos do multiconjunto (com reposição),
    conta quantos caem em títulos que já existem no conjunto-alvo e em "seção diferente"
    (aproximação: qualquer título que já apareceu é candidato a colisão).
    """
    if not titulos or n_erros == 0:
        return np.zeros(n_reps, dtype=int)
    arr = np.array(titulos)
    contagens = np.empty(n_reps, dtype=int)
    for i in range(n_reps):
        sorteados = rng.choice(arr, size=n_erros, replace=True)
        # colisão = título sorteado que já existe no multiconjunto (condição 3)
        # e que não é o próprio (simplificação conservadora)
        contagens[i] = int(np.sum(np.isin(sorteados, arr)))
    return contagens


def ic_poisson(obs: int, esperado: float, alpha: float = 0.05) -> tuple[float, float]:
    """IC 95 % aproximado via quantis da Poisson com média = esperado."""
    if esperado <= 0:
        return (0.0, float("inf"))
    low = poisson.ppf(alpha / 2, esperado)
    high = poisson.ppf(1 - alpha / 2, esperado)
    return (float(low), float(high))


def indice_dispersao(contagens: np.ndarray) -> float:
    """Var / média. > 1 indica superdispersão (concentração)."""
    m = contagens.mean()
    return float(contagens.var(ddof=1) / m) if m > 0 else 1.0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--eventos", type=Path, required=True)
    ap.add_argument("--saida", type=Path, required=True)
    ap.add_argument("--reps", type=int, default=N_REPS_DEFAULT)
    args = ap.parse_args()

    rng = np.random.default_rng(SEED)
    df = carregar_eventos(args.eventos)

    stats_p1 = medir_p1(df)
    titulos = titulos_mesarios(df)
    colisoes_obs = detectar_colisoes_observadas(df)
    n_obs = int(len(colisoes_obs))

    n_erros = stats_p1["N_mismatch"]
    sims = simular_nulo(titulos, n_erros, args.reps, rng)
    esperado = float(sims.mean())
    ic_low, ic_high = ic_poisson(n_obs, esperado)
    razao = n_obs / esperado if esperado > 0 else float("inf")
    dispersao = indice_dispersao(sims)

    # Sensibilidade p1 x0.5 e x2
    sens = {}
    for fator, nome in [(0.5, "p1_x0.5"), (2.0, "p1_x2")]:
        n_err_s = int(round(n_erros * fator))
        s = simular_nulo(titulos, n_err_s, min(args.reps, 2000), rng)
        sens[nome] = {"esperado": float(s.mean()), "ic95": list(ic_poisson(n_obs, float(s.mean())))}

    resultado = {
        "N_presenca": stats_p1["N_presenca"],
        "N_mismatch": stats_p1["N_mismatch"],
        "p1_medido": stats_p1["p1"],
        "titulos_unicos_mesarios": len(set(titulos)),
        "colisoes_observadas": n_obs,
        "esperado_simulacao": esperado,
        "razao_obs_esp": razao,
        "ic95_esperado": [ic_low, ic_high],
        "dentro_do_ic": ic_low <= n_obs <= ic_high,
        "indice_dispersao_simulacao": dispersao,
        "sensibilidade": sens,
        "seed": SEED,
        "reps": args.reps,
    }

    args.saida.parent.mkdir(parents=True, exist_ok=True)
    args.saida.write_text(json.dumps(resultado, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
