# gerador_pdf.py
import os
import markdown
from weasyprint import HTML
from datetime import datetime

GITHUB_STYLE_CSS = """
@page {
    size: A4;
    margin: 2cm;
}
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", "Liberation Sans", Helvetica, Arial, sans-serif;
    line-height: 1.6;
    color: #333;
    font-size: 14px;
    font-variant-ligatures: none;
}
.header-box {
    background-color: #f0f4ff;
    border: 1px solid #4a90d9;
    padding: 15px;
    border-radius: 5px;
    margin-bottom: 30px;
    text-align: center;
}
.header-box h1 {
    color: #1a1a2e;
    font-size: 24px;
    margin-bottom: 5px;
    border: none;
}
.header-box h2 {
    color: #4a90d9;
    font-size: 18px;
    margin-bottom: 10px;
    border: none;
}
.header-profile {
    color: #1a1a2e;
    font-weight: bold;
}
.header-profile span {
    color: #4a90d9;
    font-weight: normal;
}
h1, h2, h3 { border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }
table { border-collapse: collapse; width: 100%; margin: 15px 0; }
th, td { border: 1px solid #dfe2e5; padding: 6px 13px; }
th { background-color: #f6f8fa; font-weight: bold; text-align: left; }
pre { background-color: #f6f8fa; padding: 16px; overflow: auto; border-radius: 3px; font-family: monospace; font-size: 13px; page-break-inside: avoid; }
code { background-color: rgba(27,31,35,0.05); padding: 0.2em 0.4em; border-radius: 3px; font-family: monospace; font-size: 13px; }
blockquote { padding: 0 1em; color: #6a737d; border-left: 0.25em solid #dfe2e5; margin: 0; }
img { max-width: 100%; box-sizing: content-box; }
"""

def gerar_pdf(
    material_adaptado: str,
    assunto: str,
    dimensoes: dict,
    pasta_saida: str = "materiais_gerados"
) -> str:
    print("\n***\nGerando PDF do material adaptado com padrão Github (WeasyPrint)...")
    os.makedirs(pasta_saida, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_pdf = os.path.join(pasta_saida, f"material_{timestamp}.pdf")
    
    caminho_md_adaptado = os.path.join(pasta_saida, f"material_{timestamp}.md")
    with open(caminho_md_adaptado, "w", encoding="utf-8") as f:
        f.write(material_adaptado)
    print(f"Versão bruta do conteúdo da IA salva em Markdown: {caminho_md_adaptado}")

    perfil_texto = (
        f"{dimensoes['compreensao']} | "
        f"{dimensoes['percepcao']} | "
        f"{dimensoes['entrada']} | "
        f"{dimensoes['processamento']}"
    )

    titulo_curto = assunto[:60] + "..." if len(assunto) > 60 else assunto
    
    header_html = f"""
    <div class="header-box">
        <h1>Material Did\u00e1tico Personalizado</h1>
        <h2>{titulo_curto}</h2>
        <div class="header-profile">Perfil de Aprendizagem: <br><span>{perfil_texto}</span></div>
        <div style="margin-top:10px; font-size: 11px; color:#999;">Gerado em {datetime.now().strftime('%d/%m/%Y \u00e0s %H:%M')}</div>
    </div>
    """

    try:
        html_body = markdown.markdown(
            material_adaptado, 
            extensions=['tables', 'fenced_code', 'sane_lists', 'nl2br']
        )
    except Exception as e:
        print(f"Erro ao parsear Markdown para HTML: {e}")
        return ""

    styled_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            {GITHUB_STYLE_CSS}
        </style>
    </head>
    <body>
        {header_html}
        {html_body}
    </body>
    </html>
    """

    try:
        import sys
        
        # Redireciona a STDERR (fd=2) do sistema para esconder GLib warnings em C no macOS
        sys.stderr.flush()
        devnull_fd = os.open(os.devnull, os.O_WRONLY)
        old_stderr_fd = os.dup(2)
        os.dup2(devnull_fd, 2)
        
        try:
            HTML(string=styled_html).write_pdf(caminho_pdf)
        finally:
            os.dup2(old_stderr_fd, 2) # Restaura original
            os.close(devnull_fd)
            os.close(old_stderr_fd)
            
    except Exception as e:
        print(f"Erro no WeasyPrint ao gerar o PDF: {str(e)}")
        print("NOTA: O WeasyPrint requer a instalação do Pango no Mac. (Execute: brew install pango cairo pango libffi)")
        raise

    print(f"PDF gerado com sucesso: {caminho_pdf}\n***\n")
    return caminho_pdf
