import re
import os
import base64
import requests
from datetime import datetime

def gerar_imagem_gemini(prompt: str, pasta_saida: str = "materiais_gerados/imagens") -> str | None:
    """
    Gera uma imagem real usando a API do Gemini a partir de um prompt.
    Retorna o caminho da imagem salva ou None em caso de erro.
    """
    from modulos.llm.gemini_config import get_api_key
    import google.generativeai as genai
    
    os.makedirs(pasta_saida, exist_ok=True)
    
    try:
        api_key = get_api_key()
        genai.configure(api_key=api_key)
        
        # Usar modelo com suporte a geração de imagens
        model = genai.GenerativeModel('gemini-2.0-flash-exp-image-generation')
        
        response = model.generate_content(prompt)
        
        # Extrair a imagem gerada
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                for part in candidate.content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        image_data = part.inline_data.data
                        mime_type = part.inline_data.mime_type or 'image/png'
                        
                        # Salvar imagem
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        extensao = mime_type.split('/')[-1] if '/' in mime_type else 'png'
                        nome_arquivo = f"imagem_{timestamp}.{extensao}"
                        caminho_imagem = os.path.join(pasta_saida, nome_arquivo)
                        
                        with open(caminho_imagem, 'wb') as f:
                            f.write(image_data)
                        
                        print(f"Imagem gerada com sucesso: {caminho_imagem}")
                        return caminho_imagem
        
        print(f"Não foi possível extrair a imagem da resposta da API para o prompt: {prompt[:50]}...")
        return None
        
    except Exception as e:
        print(f"Erro ao gerar imagem com Gemini: {str(e)}")
        return None


def processar_imagens(texto_markdown: str, gerar_imagens_reais: bool = True) -> str:
    """
    Varre o texto em busca de tags [SUGESTAO_IMAGEM: descrição].
    Se gerar_imagens_reais for True, gera imagens reais usando a API do Gemini.
    Caso contrário, formata como bloco de texto para geração manual.
    """
    padrao = r'\[SUGESTAO_IMAGEM:\s*(.*?)\]'
    
    if not re.search(padrao, texto_markdown):
        return texto_markdown

    pasta_imagens = "materiais_gerados/imagens"
    
    def formatar_sugestao(match):
        prompt = match.group(1).strip()
        
        if gerar_imagens_reais:
            print(f"\n🎨 Gerando imagem para: {prompt[:60]}...")
            caminho_imagem = gerar_imagem_gemini(prompt, pasta_imagens)
            
            if caminho_imagem and os.path.exists(caminho_imagem):
                # Retornar markdown com referência à imagem local
                # O WeasyPrint consegue carregar imagens locais via path absoluto ou file://
                caminho_absoluto = os.path.abspath(caminho_imagem)
                return f"\n![Imagem Gerada]({caminho_absoluto})\n"
            else:
                return f"\n> ⚠️ **Não foi possível gerar a imagem:** `{prompt}`\n"
        else:
            return f"\n> 🎨 **Sugestão de Imagem (Gere manualmente em outra IA):**\n> `{prompt}`\n"

    texto_processado = re.sub(padrao, formatar_sugestao, texto_markdown)
    return texto_processado

