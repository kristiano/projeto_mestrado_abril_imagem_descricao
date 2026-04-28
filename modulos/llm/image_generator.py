import re

def processar_imagens(texto_markdown: str) -> str:
    """
    Varre o texto em busca de tags [SUGESTAO_IMAGEM: descrição] e as formata 
    apenas como um bloco de texto para que o usuário possa gerar manualmente em outra IA.
    """
    padrao = r'\[SUGESTAO_IMAGEM:\s*(.*?)\]'
    
    if not re.search(padrao, texto_markdown):
        return texto_markdown

    def formatar_sugestao(match):
        prompt = match.group(1).strip()
        return f"\n> 🎨 **Sugestão de Imagem (Gere manualmente em outra IA):**\n> `{prompt}`\n"

    texto_processado = re.sub(padrao, formatar_sugestao, texto_markdown)
    return texto_processado

