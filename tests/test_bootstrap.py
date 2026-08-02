"""Teste de fumaça (smoke test) da Fase 0.

Objetivo único: garantir que o ambiente uv está corretamente configurado
(Python >= 3.13, pacote `core` importável via pythonpath=["src"]) e que o
pipeline de CI tem pelo menos um teste real para executar — evitando que
"pytest" retorne "nenhum teste coletado" (exit code 5) no primeiro PR.

Nenhuma regra de negócio é testada aqui; testes de domínio/aplicação
começam na Fase 3 (módulo Aluno), conforme Documento 5, Seção 12.
"""

import sys

from core import __version__ as core_version


def test_python_version_e_no_minimo_3_13() -> None:
    assert sys.version_info >= (3, 13), (
        "Documento 4 exige Python 3.13+; ambiente atual: "
        f"{sys.version_info.major}.{sys.version_info.minor}"
    )


def test_pacote_core_e_importavel() -> None:
    assert core_version == "0.1.0"
