"""Smoke test da Fase 0 — garante que o ambiente e o pythonpath estão configurados
antes de existir qualquer regra de negócio para testar (essa vem na Fase 3)."""

import sys

from core import __version__ as core_version


def test_python_version_e_no_minimo_3_13() -> None:
    assert sys.version_info >= (3, 13), (
        "Documento 4 exige Python 3.13+; ambiente atual: "
        f"{sys.version_info.major}.{sys.version_info.minor}"
    )


def test_pacote_core_e_importavel() -> None:
    assert core_version == "0.1.0"
