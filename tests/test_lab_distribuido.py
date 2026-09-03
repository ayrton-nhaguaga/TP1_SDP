from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from lab_distribuido import (
    executar_benchmark,
    map_function,
    normalizar_palavra,
    reduce_function,
)


class TestMapReduce(unittest.TestCase):
    def test_normalizacao_remove_pontuacao_e_ignora_maiusculas(self) -> None:
        self.assertEqual(normalizar_palavra("Olá,"), "olá")
        self.assertEqual(normalizar_palavra("MAP-Reduce!"), "mapreduce")
        self.assertEqual(normalizar_palavra("..."), "")

    def test_map_conta_palavras_utf8(self) -> None:
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "entrada.txt"
            caminho.write_text("Olá, mundo! OLÁ. 2026\n", encoding="utf-8")

            self.assertEqual(
                map_function(caminho), {"olá": 2, "mundo": 1, "2026": 1}
            )

    def test_reduce_agrega_resultados(self) -> None:
        resultado = reduce_function([{"map": 2, "reduce": 1}, {"map": 3}])
        self.assertEqual(resultado, {"map": 5, "reduce": 1})

    def test_sequencial_e_distribuido_sao_equivalentes(self) -> None:
        with tempfile.TemporaryDirectory() as diretorio:
            raiz = Path(diretorio)
            ficheiros = []
            for indice, texto in enumerate(("a a b", "b c", "a c c"), start=1):
                caminho = raiz / f"texto{indice}.txt"
                caminho.write_text(texto, encoding="utf-8")
                ficheiros.append(caminho)

            benchmark, contagens = executar_benchmark(
                ficheiros, numero_processos=2, repeticoes=1
            )

            self.assertEqual(contagens, {"a": 3, "b": 2, "c": 3})
            self.assertEqual(benchmark.total_palavras, 8)
            self.assertEqual(benchmark.palavras_distintas, 3)
            self.assertGreater(benchmark.tempo_sequencial_s, 0)
            self.assertGreater(benchmark.tempo_distribuido_s, 0)

    def test_ficheiro_inexistente_produz_erro_claro(self) -> None:
        with self.assertRaises(FileNotFoundError):
            executar_benchmark(["nao_existe.txt"])

    def test_rejeita_numero_de_processos_invalido(self) -> None:
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "entrada.txt"
            caminho.write_text("conteúdo", encoding="utf-8")
            with self.assertRaises(ValueError):
                executar_benchmark([caminho], numero_processos=0)


if __name__ == "__main__":
    unittest.main()
