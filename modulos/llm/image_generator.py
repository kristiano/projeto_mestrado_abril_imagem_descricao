import re
import base64
import os
from typing import Optional
from modulos.llm.gemini_config import criar_cliente_genai


def gerar_imagem_com_gemini(prompt: str) -> Optional[bytes]:
    """
    Gera uma imagem usando a API do Gemini (nova SDK google.genai) com base no prompt fornecido.
    Retorna os bytes da imagem em formato PNG ou None se falhar.
    """
    try:
        print(f"  🎨 Gerando imagem com Gemini: {prompt[:80]}...")
        
        # Usar a nova SDK para geração de imagens
        client = criar_cliente_genai()
        
        # Configurar parâmetros para geração de imagem
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp-image-generation",
            contents=prompt,
            config={
                "response_modalities": ["IMAGE"],
            }
        )
        
        # Extrair a imagem da resposta
        # A nova SDK retorna a estrutura de forma diferente
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'inline_data') and part.inline_data:
                return part.inline_data.data
        
        print("  ⚠️ Nenhuma imagem foi retornada pela API.")
        return None
        
    except Exception as e:
        print(f"  ❌ Erro ao gerar imagem: {str(e)}")
        return None


def processar_imagens(texto_markdown: str, dimensoes: dict) -> str:
    """
    Varre o texto em busca de tags [SUGESTAO_IMAGEM: descrição] e:
    - Se o aluno for VISUAL: gera a imagem usando a API do Gemini e insere no texto
    - Se não for visual: mantém como bloco de texto informativo
    
    Parâmetros:
    texto_markdown: conteúdo com as tags de sugestão
    dimensoes: dicionário com o perfil do aluno (para verificar se é Visual)
    
    Retorna:
    texto_processado: markdown com imagens geradas ou prompts formatados
    """
    padrao = r'\[SUGESTAO_IMAGEM:\s*(.*?)\]'
    
    if not re.search(padrao, texto_markdown):
        return texto_markdown
    
    # Verificar se o aluno tem perfil Visual
    eh_visual = dimensoes.get('entrada', '').lower() == 'visual'
    
    if not eh_visual:
        # Aluno não é visual: manter apenas o prompt como texto
        def formatar_sugestao(match):
            prompt = match.group(1).strip()
            return f"\n> 🎨 **Sugestão de Imagem:**\n> `{prompt}`\n"
        
        texto_processado = re.sub(padrao, formatar_sugestao, texto_markdown)
        return texto_processado
    
    # Aluno é VISUAL: tentar gerar as imagens
    print("\n" + "="*60)
    print("   GERANDO IMAGENS COM GEMINI (Perfil Visual Detectado)")
    print("="*60)
    
    imagens_encontradas = re.findall(padrao, texto_markdown)
    print(f"\n📊 {len(imagens_encontradas)} sugestão(ões) de imagem encontrada(s)")
    
    # Criar pasta para salvar imagens temporárias
    pasta_imagens = "imagens_geradas"
    os.makedirs(pasta_imagens, exist_ok=True)
    
    def substituir_com_imagem(match):
        prompt = match.group(1).strip()
        
        # Gerar imagem
        imagem_bytes = gerar_imagem_com_gemini(prompt)
        
        if imagem_bytes:
            # Salvar imagem em arquivo
            timestamp = os.urandom(4).hex()
            nome_arquivo = f"img_{timestamp}.png"
            caminho_completo = os.path.join(pasta_imagens, nome_arquivo)
            
            with open(caminho_completo, "wb") as f:
                f.write(imagem_bytes)
            
            print(f"  ✅ Imagem salva: {nome_arquivo}")
            
            # Retornar referência Markdown para a imagem
            return f"\n![Imagem gerada]({caminho_completo})\n"
        else:
            # Fallback: manter o prompt como texto se falhar
            return f"\n> 🎨 **Sugestão de Imagem (não gerada):**\n> `{prompt}`\n"
    
    texto_processado = re.sub(padrao, substituir_com_imagem, texto_markdown)
    
    print("\n" + "="*60)
    print("   PROCESSO DE GERAÇÃO DE IMAGENS CONCLUÍDO")
    print("="*60 + "\n")
    
    return texto_processado

