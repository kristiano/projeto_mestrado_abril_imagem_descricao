"""Ponto único de composição de dependências (Documento 4, Seção 7).

Na inicialização do processo, instancia as implementações concretas de
Infrastructure e as injeta nos casos de uso da Application. Vazio até a
Fase 3, quando existirem os primeiros repositórios e casos de uso para compor.
"""


class Container:
    """Registro central de dependências, resolvidas na inicialização do processo."""
