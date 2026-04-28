import os
import pymupdf4llm

def converter_pdf_para_md(caminho_pdf: str) -> str:
    """
    Lê o PDF usando pymupdf4llm, converte para Markdown e salva 
    todo o conteúdo em 'conteudo.md'. 
    Retorna o caminho do arquivo Markdown gerado.
    """
    print(f"\nLendo PDF e convertendo para Markdown com pymupdf4llm: {caminho_pdf}")
    
    # Extrair todo o PDF como Markdown — imagens NÃO são embutidas
    # (embed_images=False evita dados base64 no markdown que poluem o contexto da LLM)
    md_text = pymupdf4llm.to_markdown(caminho_pdf, embed_images=False)
    
    # Definir o caminho para o arquivo conteudo.md
    base_dir = os.path.dirname(os.path.abspath(caminho_pdf))
    caminho_md = os.path.join(base_dir, "conteudo.md")
    
    # Salvar em conteudo.md
    print(f"Salvando o conteúdo completo convertido em: {caminho_md}")
    with open(caminho_md, "w", encoding="utf-8") as f:
        f.write(md_text)
        
    return caminho_md