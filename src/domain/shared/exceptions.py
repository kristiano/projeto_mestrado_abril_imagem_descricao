"""Hierarquia de exceções de domínio (Documento 4, Seção 15).

Domain e Application lançam essas exceções quando uma regra de negócio impede a
continuidade de uma operação; a tradução para código HTTP e para o envelope de
erro padrão (Documento 3, §2.4) acontece em core.exceptions, nunca aqui — esta
camada não conhece HTTP.
"""

from typing import Any


class DomainError(Exception):
    """Base da hierarquia. Não é lançada diretamente, apenas suas subclasses."""

    def __init__(self, code: str, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details


class RecursoNaoEncontradoError(DomainError):
    """Recurso referenciado por id não existe. Mapeada para 404 na API."""


class RegraDeNegocioVioladaError(DomainError):
    """Corpo da requisição válido, mas em desacordo com uma regra de negócio. Mapeada para 422."""


class ConflitoDeEstadoError(DomainError):
    """Recurso existe, mas seu estado atual impede a operação solicitada. Mapeada para 409."""
