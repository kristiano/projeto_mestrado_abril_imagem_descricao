"""
limpar_latex.py
Converte notação LaTeX inline ($...$) em texto Unicode legível para humanos.
Uso: python limpar_latex.py material.md [material_limpo.md]
"""

import re
import sys

# Mapa de símbolos LaTeX → Unicode/texto legível
SIMBOLOS = {
    r'\to': '→',
    r'\rightarrow': '→',
    r'\implies': '→',
    r'\gets': '←',
    r'\leftarrow': '←',
    r'\leftrightarrow': '↔',
    r'\Leftrightarrow': '⇔',
    r'\iff': '↔',
    r'\neg': '¬',
    r'\lnot': '¬',
    r'\land': '∧',
    r'\wedge': '∧',
    r'\lor': '∨',
    r'\vee': '∨',
    r'\oplus': '⊕',
    r'\therefore': '∴',
    r'\forall': '∀',
    r'\exists': '∃',
    r'\nexists': '∄',
    r'\in': '∈',
    r'\notin': '∉',
    r'\subset': '⊂',
    r'\subseteq': '⊆',
    r'\supset': '⊃',
    r'\supseteq': '⊇',
    r'\cup': '∪',
    r'\cap': '∩',
    r'\emptyset': '∅',
    r'\infty': '∞',
    r'\equiv': '≡',
    r'\neq': '≠',
    r'\leq': '≤',
    r'\geq': '≥',
    r'\times': '×',
    r'\cdot': '·',
    r'\cdots': '⋯',
    r'\dots': '…',
    r'\ldots': '…',
    r'\quad': '  ',
    r'\qquad': '    ',
    r'\,': ' ',
    r'\;': ' ',
    r'\!': '',
    r'\ ': ' ',
}


def converter_expressao_latex(expr: str) -> str:
    """Converte uma expressão LaTeX individual em texto Unicode."""
    resultado = expr

    # Substituir símbolos (ordenar por tamanho descendente para evitar conflitos parciais)
    for latex, unicode_char in sorted(SIMBOLOS.items(), key=lambda x: -len(x[0])):
        resultado = resultado.replace(latex, unicode_char)

    # Remover comandos \text{...} mantendo conteúdo
    resultado = re.sub(r'\\text\{([^}]*)\}', r'\1', resultado)
    resultado = re.sub(r'\\textbf\{([^}]*)\}', r'\1', resultado)
    resultado = re.sub(r'\\textit\{([^}]*)\}', r'\1', resultado)
    resultado = re.sub(r'\\mathbf\{([^}]*)\}', r'\1', resultado)

    # Remover \overline{X} → X̅ (com combining overline) ou simplificar para ¬X
    resultado = re.sub(r'\\overline\{([^}]*)\}', r'¬\1', resultado)
    resultado = re.sub(r'\\bar\{([^}]*)\}', r'¬\1', resultado)

    # Limpar espaços duplos residuais
    resultado = re.sub(r'  +', ' ', resultado)

    return resultado.strip()


def processar_markdown(texto: str) -> str:
    """Processa todo o texto Markdown, convertendo expressões LaTeX inline."""

    def substituir_inline(match):
        expr = match.group(1)
        return converter_expressao_latex(expr)

    # Substituir $...$ (inline math) — não-guloso
    resultado = re.sub(r'\$([^$]+?)\$', substituir_inline, texto)

    # Substituir $$...$$ (display math) — caso exista
    def substituir_display(match):
        expr = match.group(1)
        return converter_expressao_latex(expr)

    resultado = re.sub(r'\$\$([^$]+?)\$\$', substituir_display, resultado)

    return resultado


def main():
    if len(sys.argv) < 2:
        print("Uso: python limpar_latex.py <arquivo.md> [saida.md]")
        sys.exit(1)

    entrada = sys.argv[1]
    saida = sys.argv[2] if len(sys.argv) > 2 else entrada.replace('.md', '_limpo.md')

    with open(entrada, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Contar ocorrências antes
    ocorrencias_antes = len(re.findall(r'\$[^$]+?\$', conteudo))

    conteudo_limpo = processar_markdown(conteudo)

    # Contar ocorrências depois
    ocorrencias_depois = len(re.findall(r'\$[^$]+?\$', conteudo_limpo))

    with open(saida, 'w', encoding='utf-8') as f:
        f.write(conteudo_limpo)

    print(f"Expressões LaTeX encontradas: {ocorrencias_antes}")
    print(f"Expressões LaTeX restantes:   {ocorrencias_depois}")
    print(f"Arquivo salvo em: {saida}")


if __name__ == '__main__':
    main()