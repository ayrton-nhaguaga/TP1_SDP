"""Laboratório 2 — contagem de palavras com MapReduce multiprocesso.

O módulo mantém as funções ``map_function`` e ``reduce_function`` pedidas no
enunciado, mas separa a medição e a interface de linha de comandos para que o
código também possa ser importado e testado.
"""

from __future__ import annotations

import argparse
import json
import multiprocessing
import statistics
import time
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence


FICHEIROS_PADRAO = ("texto1.txt", "texto2.txt", "texto3.txt")


def normalizar_palavra(token: str) -> str:
    """Normaliza um token segundo a regra proposta no código do enunciado."""

    return "".join(caractere for caractere in token.casefold() if caractere.isalnum())


def map_function(file_path: str | Path) -> dict[str, int]:
    """Executa a fase Map para um ficheiro, sem o carregar todo em memória."""

    caminho = Path(file_path)
    contagens: Counter[str] = Counter()

    with caminho.open("r", encoding="utf-8") as ficheiro:
        for linha in ficheiro:
            for token in linha.split():
                palavra = normalizar_palavra(token)
                if palavra:
                    contagens[palavra] += 1

    return dict(contagens)


def reduce_function(mapped_results: Iterable[dict[str, int]]) -> dict[str, int]:
    """Executa a fase Reduce, agregando as contagens produzidas pelo Map."""

    contagem_final: Counter[str] = Counter()
    for resultado in mapped_results:
        contagem_final.update(resultado)
    return dict(contagem_final)


def processar_sequencial(caminhos: Sequence[Path]) -> dict[str, int]:
    """Processa todos os ficheiros no processo atual."""

    return reduce_function(map_function(caminho) for caminho in caminhos)


def processar_distribuido(
    caminhos: Sequence[Path], numero_processos: int
) -> dict[str, int]:
    """Distribui uma tarefa Map por ficheiro e reduz no processo principal."""

    # O context manager garante close/join mesmo quando ocorre uma exceção.
    with multiprocessing.Pool(processes=numero_processos) as pool:
        resultados_mapeados = pool.map(map_function, caminhos)
    return reduce_function(resultados_mapeados)


@dataclass(frozen=True)
class ResultadoBenchmark:
    ficheiros: list[str]
    processos: int
    repeticoes: int
    tempo_sequencial_s: float
    tempo_distribuido_s: float
    speedup: float
    total_palavras: int
    palavras_distintas: int


def _medir(funcao, *argumentos) -> tuple[float, dict[str, int]]:
    inicio = time.perf_counter()
    resultado = funcao(*argumentos)
    return time.perf_counter() - inicio, resultado


def executar_benchmark(
    caminhos: Sequence[str | Path],
    numero_processos: int | None = None,
    repeticoes: int = 1,
) -> tuple[ResultadoBenchmark, dict[str, int]]:
    """Mede as duas estratégias e confirma que produzem o mesmo resultado."""

    if not caminhos:
        raise ValueError("É necessário indicar pelo menos um ficheiro.")
    if repeticoes < 1:
        raise ValueError("O número de repetições tem de ser pelo menos 1.")

    ficheiros = [Path(caminho) for caminho in caminhos]
    inexistentes = [str(caminho) for caminho in ficheiros if not caminho.is_file()]
    if inexistentes:
        raise FileNotFoundError(
            "Ficheiro(s) não encontrado(s): " + ", ".join(inexistentes)
        )

    processos_pedidos = len(ficheiros) if numero_processos is None else numero_processos
    if processos_pedidos < 1:
        raise ValueError("O número de processos tem de ser pelo menos 1.")
    processos = min(processos_pedidos, len(ficheiros))

    tempos_sequenciais: list[float] = []
    tempos_distribuidos: list[float] = []
    resultado_final: dict[str, int] = {}

    for _ in range(repeticoes):
        tempo_seq, resultado_seq = _medir(processar_sequencial, ficheiros)
        tempo_dist, resultado_dist = _medir(
            processar_distribuido, ficheiros, processos
        )

        if resultado_seq != resultado_dist:
            raise RuntimeError(
                "Falha de consistência: os resultados sequencial e distribuído "
                "são diferentes."
            )

        tempos_sequenciais.append(tempo_seq)
        tempos_distribuidos.append(tempo_dist)
        resultado_final = resultado_seq

    tempo_seq_mediano = statistics.median(tempos_sequenciais)
    tempo_dist_mediano = statistics.median(tempos_distribuidos)
    speedup = tempo_seq_mediano / tempo_dist_mediano

    resultado = ResultadoBenchmark(
        ficheiros=[str(caminho) for caminho in ficheiros],
        processos=processos,
        repeticoes=repeticoes,
        tempo_sequencial_s=tempo_seq_mediano,
        tempo_distribuido_s=tempo_dist_mediano,
        speedup=speedup,
        total_palavras=sum(resultado_final.values()),
        palavras_distintas=len(resultado_final),
    )
    return resultado, resultado_final


def _criar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compara a contagem sequencial com MapReduce multiprocesso."
    )
    parser.add_argument(
        "ficheiros",
        nargs="*",
        default=list(FICHEIROS_PADRAO),
        help="ficheiros UTF-8 (padrão: texto1.txt texto2.txt texto3.txt)",
    )
    parser.add_argument(
        "-p",
        "--processos",
        type=int,
        help="número de processos Map (padrão: um por ficheiro)",
    )
    parser.add_argument(
        "-r",
        "--repeticoes",
        type=int,
        default=1,
        help="repetições do benchmark; reporta-se a mediana (padrão: 1)",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=10,
        help="quantidade de palavras mais frequentes a apresentar (padrão: 10)",
    )
    parser.add_argument(
        "--json",
        type=Path,
        metavar="FICHEIRO",
        help="guarda métricas e contagens num ficheiro JSON",
    )
    return parser


def _imprimir_resultado(
    resultado: ResultadoBenchmark, contagens: dict[str, int], top: int
) -> None:
    print("--- RESULTADOS DO LABORATÓRIO 2 ---")
    print(f"Ficheiros processados : {len(resultado.ficheiros)}")
    print(f"Processos Map         : {resultado.processos}")
    print(f"Tempo sequencial      : {resultado.tempo_sequencial_s:.4f} s")
    print(f"Tempo distribuído     : {resultado.tempo_distribuido_s:.4f} s")
    print(f"Speedup (Ts/Td)       : {resultado.speedup:.2f}x")
    print(f"Total de palavras     : {resultado.total_palavras}")
    print(f"Palavras distintas    : {resultado.palavras_distintas}")

    if top > 0:
        print(f"\nTop {top} palavras:")
        for palavra, quantidade in Counter(contagens).most_common(top):
            print(f"  {palavra:<24} {quantidade}")


def main(argv: Sequence[str] | None = None) -> int:
    argumentos = _criar_parser().parse_args(argv)
    try:
        resultado, contagens = executar_benchmark(
            argumentos.ficheiros, argumentos.processos, argumentos.repeticoes
        )
    except (FileNotFoundError, OSError, UnicodeError, ValueError) as erro:
        print(f"Erro: {erro}")
        print("Crie os dados com: python gerar_dados.py")
        return 2

    _imprimir_resultado(resultado, contagens, argumentos.top)

    if argumentos.json:
        payload = asdict(resultado)
        payload["contagens"] = dict(sorted(contagens.items()))
        argumentos.json.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"\nResultado JSON guardado em: {argumentos.json}")

    return 0


if __name__ == "__main__":
    multiprocessing.freeze_support()
    raise SystemExit(main())
