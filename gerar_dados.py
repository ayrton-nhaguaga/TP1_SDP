"""Gera os três ficheiros de texto usados no Laboratório 2."""

from __future__ import annotations

import argparse
from pathlib import Path


BLOCOS = (
    "Sistemas distribuídos permitem escalabilidade horizontal. "
    "MapReduce divide o trabalho em map, shuffle e reduce. "
    "Cada processo conta palavras localmente; depois os resultados são agregados.\n",
    "Python oferece multiprocessing para executar tarefas CPU-bound em paralelo. "
    "Processos não partilham memória: comunicam por serialização e mensagens. "
    "Todo paralelismo possui overhead de criação, comunicação e sincronização.\n",
    "O speedup compara o tempo sequencial com o tempo distribuído. "
    "Resultados corretos devem ser iguais em todas as execuções! "
    "Medir, validar e interpretar os dados é essencial num experimento científico.\n",
)


def gerar_ficheiro(caminho: Path, tamanho_bytes: int, bloco: str) -> int:
    """Escreve blocos completos até atingir pelo menos o tamanho pretendido."""

    caminho.parent.mkdir(parents=True, exist_ok=True)
    bloco_bytes = bloco.encode("utf-8")
    escritos = 0
    with caminho.open("wb") as ficheiro:
        while escritos < tamanho_bytes:
            ficheiro.write(bloco_bytes)
            escritos += len(bloco_bytes)
    return escritos


def _criar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Gera texto1.txt, texto2.txt e texto3.txt deterministicamente."
    )
    parser.add_argument(
        "--destino",
        type=Path,
        default=Path.cwd(),
        help="diretório de saída (padrão: diretório atual)",
    )
    parser.add_argument(
        "--tamanho-mb",
        type=float,
        default=8.0,
        help="tamanho mínimo de cada ficheiro em MiB (padrão: 8)",
    )
    return parser


def main() -> int:
    argumentos = _criar_parser().parse_args()
    if argumentos.tamanho_mb <= 0:
        raise SystemExit("Erro: --tamanho-mb tem de ser maior que zero.")

    tamanho_bytes = round(argumentos.tamanho_mb * 1024 * 1024)
    for indice, bloco in enumerate(BLOCOS, start=1):
        caminho = argumentos.destino / f"texto{indice}.txt"
        escritos = gerar_ficheiro(caminho, tamanho_bytes, bloco)
        print(f"Criado {caminho} ({escritos / 1024 / 1024:.2f} MiB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
