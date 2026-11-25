#!/usr/bin/env python3
"""
parsing.py — Extração de registros de presença de mesário e mensagens de mismatch
dos logs de urna (.jez / .logjez) do TSE.

Uso:
  python parsing.py catalogo --zip /caminho/pacote_UF.zip --saida catalogo.csv
  python parsing.py extrair --zip /caminho/pacote_UF.zip --saida eventos.csv --data 2026-10-25

Saídas sempre mascaram sequências longas de dígitos (títulos) para conformidade LGPD.
O arquivo original dos logs NÃO é alterado.
"""

from __future__ import annotations

import argparse
import csv
import io
import re
import zipfile
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Iterator

# ---------------------------------------------------------------------------
# Vocabulário (Fase 0) — strings a serem refinadas empiricamente em 30 seções
# ---------------------------------------------------------------------------
PADROES_MESARIO = [
    re.compile(r"presen[cç]a.*mes[aá]rio", re.I),
    re.compile(r"mes[aá]rio.*t[ií]tulo", re.I),
    re.compile(r"registro.*mes[aá]rio", re.I),
]
PADROES_MISMATCH = [
    re.compile(r"biometria.*n[aã]o.*coincide.*mes[aá]rio", re.I),
    re.compile(r"biometria.*n[aã]o.*cadastrad", re.I),
    re.compile(r"t[ií]tulo.*n[aã]o.*confere.*mes[aá]rio", re.I),
]
PADROES_TITULO = re.compile(r"\b(\d{12})\b")  # título de eleitor tem 12 dígitos
PADROES_INVALIDO = [
    re.compile(r"t[ií]tulo.*inv[aá]lido", re.I),
    re.compile(r"d[ií]gito.*verificador", re.I),
]

DIGITOS = re.compile(r"\d{4,}")
FORMATO_DATA = "%d/%m/%Y %H:%M:%S"
SECAO_NO_NOME = re.compile(
    r"(?P<mun>\d{5})(?P<zona>\d{4})(?P<secao>\d{4}).*\.(?:logjez|jez)$",
    re.I,
)


@dataclass
class Evento:
    uf: str
    municipio: str
    zona: str
    secao: str
    timestamp: str
    tipo: str          # "presenca_mesario" | "mismatch_bio" | "titulo_invalido" | "outro"
    titulo_mascarado: str
    mensagem_mascarada: str
    arquivo: str


def mascarar(texto: str) -> str:
    """Mascara sequências de 4+ dígitos."""
    return DIGITOS.sub("####", texto)


def identificar_secao(nome: str) -> dict[str, str]:
    m = SECAO_NO_NOME.search(nome)
    if not m:
        return {"municipio": "", "zona": "", "secao": "", "arquivo": nome}
    return {
        "municipio": m.group("mun"),
        "zona": m.group("zona"),
        "secao": m.group("secao"),
        "arquivo": nome,
    }


def ler_jez(conteudo: bytes) -> str:
    """Descompacta .jez (ZIP ou 7z) e devolve o texto concatenado (Latin-1)."""
    if conteudo[:4] == b"PK\x03\x04":
        with zipfile.ZipFile(io.BytesIO(conteudo)) as z:
            partes = []
            for nome in sorted(z.namelist()):
                if not nome.endswith("/"):
                    try:
                        partes.append(z.read(nome).decode("latin-1", errors="replace"))
                    except Exception:
                        partes.append(z.read(nome).decode("utf-8", errors="replace"))
            return "\n".join(partes)
    # fallback 7z — requer py7zr se necessário
    try:
        import py7zr
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            with py7zr.SevenZipFile(io.BytesIO(conteudo), mode="r") as arq:
                arq.extractall(path=tmp)
            textos = []
            for p in Path(tmp).rglob("*"):
                if p.is_file():
                    textos.append(p.read_bytes().decode("latin-1", errors="replace"))
            return "\n".join(textos)
    except ImportError:
        return conteudo.decode("latin-1", errors="replace")


def classificar_linha(linha: str) -> str | None:
    for p in PADROES_MESARIO:
        if p.search(linha):
            return "presenca_mesario"
    for p in PADROES_MISMATCH:
        if p.search(linha):
            return "mismatch_bio"
    for p in PADROES_INVALIDO:
        if p.search(linha):
            return "titulo_invalido"
    return None


def extrair_titulo(linha: str) -> str:
    m = PADROES_TITULO.search(linha)
    return m.group(1) if m else ""


def iterar_eventos(caminho_zip: Path, data_filtro: str | None = None) -> Iterator[Evento]:
    with zipfile.ZipFile(caminho_zip) as pacote:
        for membro in sorted(pacote.namelist()):
            if not re.search(r"\.(logjez|jez)$", membro, re.I):
                continue
            ident = identificar_secao(membro)
            try:
                texto = ler_jez(pacote.read(membro))
            except Exception:
                continue
            for bruta in texto.splitlines():
                if not bruta.strip():
                    continue
                partes = bruta.split("\t")
                ts_str = partes[0].strip() if partes else ""
                try:
                    ts = datetime.strptime(ts_str, FORMATO_DATA)
                except ValueError:
                    continue
                if data_filtro and ts.date().isoformat() != data_filtro:
                    continue
                tipo = classificar_linha(bruta)
                if tipo is None:
                    continue
                titulo = extrair_titulo(bruta)
                yield Evento(
                    uf="",  # preenchido pelo chamador a partir do nome do ZIP
                    municipio=ident["municipio"],
                    zona=ident["zona"],
                    secao=ident["secao"],
                    timestamp=ts.isoformat(),
                    tipo=tipo,
                    titulo_mascarado=mascarar(titulo) if titulo else "",
                    mensagem_mascarada=mascarar(bruta[:200]),
                    arquivo=membro,
                )


def cmd_catalogo(args: argparse.Namespace) -> int:
    """Gera catálogo de mensagens distintas (para refinamento da Fase 0)."""
    from collections import Counter
    cont = Counter()
    n = 0
    for ev in iterar_eventos(args.zip, args.data):
        cont[ev.tipo] += 1
        n += 1
        if args.limite and n >= args.limite:
            break
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    with args.saida.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["tipo", "ocorrencias"])
        for tipo, c in cont.most_common():
            w.writerow([tipo, c])
    print(f"eventos_lidos={n} tipos={len(cont)}")
    return 0


def cmd_extrair(args: argparse.Namespace) -> int:
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with args.saida.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(Evento.__dataclass_fields__.keys()))
        w.writeheader()
        for ev in iterar_eventos(args.zip, args.data):
            ev.uf = args.uf or ""
            w.writerow(asdict(ev))
            n += 1
            if args.limite and n >= args.limite:
                break
    print(f"eventos_escritos={n} -> {args.saida}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p1 = sub.add_parser("catalogo")
    p1.add_argument("--zip", type=Path, required=True)
    p1.add_argument("--saida", type=Path, required=True)
    p1.add_argument("--data", help="AAAA-MM-DD")
    p1.add_argument("--limite", type=int)
    p1.set_defaults(func=cmd_catalogo)

    p2 = sub.add_parser("extrair")
    p2.add_argument("--zip", type=Path, required=True)
    p2.add_argument("--saida", type=Path, required=True)
    p2.add_argument("--uf")
    p2.add_argument("--data", help="AAAA-MM-DD")
    p2.add_argument("--limite", type=int)
    p2.set_defaults(func=cmd_extrair)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
