import os
import json
from typing import List, Dict, Tuple, Optional
from modulos.llm.gemini_config import criar_modelo

def _extrair_amostras_md(
    caminho_md: str,
    max_chars: int = 15000,
) -> str:
    """
    Extrai uma amostra textual do arquivo markdown para a LLM:
    - remove tags de imagens gigantes em Base64 para não poluir a amostra
    - pega os primeiros caracteres (limitado por max_chars)
    """
    if not os.path.exists(caminho_md):
        return ""
        
    with open(caminho_md, "r", encoding="utf-8") as f:
        texto_completo = f.read()

    return texto_completo[:max_chars]


def _sugerir_assuntos_com_llm(
    texto_amostra: str,
) -> List[Dict]:
    """
    Usa a LLM para sugerir possíveis assuntos/tópicos da disciplina
    com base em uma amostra.
    """
    if not texto_amostra.strip():
        return []

    system_msg = (
        "Você é um especialista em organização de conteúdo de disciplinas "
        "universitárias. Seu trabalho é ler uma amostra de um material em Markdown "
        "e propor possíveis assuntos/tópicos principais dessa disciplina.\n\n"
        "IMPORTANTE: responda ESTRITAMENTE em JSON válido, sem comentários, "
        "sem texto antes ou depois. O formato deve ser:\n"
        "[\n"
        "  {\n"
        '    \"id\": 1,\n'
        '    \"titulo\": \"Título curto do assunto\",\n'
        '    \"descricao\": \"Breve descrição do que é abordado\",\n'
        '    \"palavras_chave\": [\"palavra1\", \"palavra2\"]\n'
        "  },\n"
        "  ...\n"
        "]\n"
    )

    user_msg = (
        "A seguir está uma amostra do conteúdo de uma disciplina.\n"
        "Com base nessa amostra, identifique de 3 a 8 possíveis assuntos/tópicos "
        "principais da disciplina.\n\n"
        "Use palavras-chave que provavelmente aparecem no texto para ajudar a "
        "localizar o assunto depois.\n\n"
        "AMOSTRA DO CONTEÚDO:\n\n"
        f"{texto_amostra}\n"
    )

    model = criar_modelo(system_instruction=system_msg)
    resposta = model.generate_content(user_msg)
    raw = (resposta.text or "").strip()

    # Tratamento para limpar se a LLM botar blocos ```json ... ```
    if raw.startswith("```json"):
        raw = raw[7:]
    if raw.startswith("```"):
        raw = raw[3:]
    if raw.endswith("```"):
        raw = raw[:-3]
    raw = raw.strip()

    try:
        dados = json.loads(raw)
        if isinstance(dados, list):
            topicos = []
            for item in dados:
                if not isinstance(item, dict):
                    continue
                if "titulo" not in item or "id" not in item:
                    continue
                if "palavras_chave" not in item:
                    item["palavras_chave"] = []
                topicos.append(item)
            return topicos
    except Exception:
        print("\nNão foi possível interpretar a resposta da LLM como JSON válido.")

    return []


def _extrair_trecho_por_palavras_chave_md(
    caminho_md: str,
    palavras_chave: List[str],
    contexto_linhas: int = 50,
) -> str:
    """
    Procura blocos de texto no arquivo markdown que contenham pelo menos 
    uma das palavras-chave.
    """
    if not palavras_chave or not os.path.exists(caminho_md):
        return ""

    palavras_norm = [p.lower() for p in palavras_chave if p.strip()]
    if not palavras_norm:
        return ""

    with open(caminho_md, "r", encoding="utf-8") as f:
        linhas = f.readlines()

    trechos_relevantes = []
    
    # Vamos dividir o documento em blocos de parágrafos/seções
    texto_completo = "".join(linhas)
    blocos = texto_completo.split("\n\n")

    for bloco in blocos:
        bloco_lower = bloco.lower()
        if any(p in bloco_lower for p in palavras_norm):
            trechos_relevantes.append(bloco.strip())

    return "\n\n".join(trechos_relevantes).strip()


def localizar_assunto_com_llm(
    caminho_pdf: str,
) -> Optional[Tuple[str, str]]:
    """
    Fallback quando não foi possível identificar capítulos automaticamente.
    Agora lê a partir do 'conteudo.md' que foi gerado previamente.
    """
    print(
        "\nTentando localizar assuntos na disciplina com apoio da LLM "
        "(a partir do Markdown gerado)..."
    )

    base_dir = os.path.dirname(os.path.abspath(caminho_pdf))
    caminho_md = os.path.join(base_dir, "conteudo.md")

    texto_amostra = _extrair_amostras_md(caminho_md)
    if not texto_amostra.strip():
        print("\nNão foi possível ler o arquivo Markdown gerado.")
        return None

    topicos = _sugerir_assuntos_com_llm(texto_amostra)
    if not topicos:
        print(
            "\nA LLM não conseguiu sugerir assuntos de forma confiável. "
            "Operação cancelada."
        )
        return None

    print("\n" + "=" * 60)
    print("   ASSUNTOS SUGERIDOS PELA LLM")
    print("=" * 60)
    for item in topicos:
        tid = item.get("id")
        titulo = item.get("titulo", "").strip()
        desc = item.get("descricao", "").strip()
        print(f"\n  {tid}. {titulo}")
        if desc:
            print(f"     - {desc}")

    print("\nDigite o número do assunto que deseja adaptar.")
    print("Ou digite o TEMA ESPECÍFICO desejado se preferir buscar algo próprio.")
    print("Pressione Enter em branco para cancelar.")

    escolhido = None
    while True:
        resp = input("\n  Sua escolha: ").strip()
        if not resp:
            print("\nOperação cancelada pelo usuário.")
            return None
            
        try:
            num = int(resp)
            for item in topicos:
                if int(item.get("id")) == num:
                    escolhido = item
                    break
            if escolhido is None:
                print("  ⚠ ID não encontrado na lista. Tente novamente.")
            else:
                break
        except ValueError:
            # Trata entrada textual livre como assunto personalizado
            palavras_extras = [p.strip() for p in resp.replace(',', ' ').split() if len(p.strip()) >= 3]
            escolhido = {
                "id": "Personalizado",
                "titulo": resp,
                "descricao": "Tópico inserido manualmente pelo usuário.",
                "palavras_chave": palavras_extras
            }
            break

    titulo = str(escolhido.get("titulo", "")).strip() or f"Assunto {escolhido.get('id')}"
    palavras_chave = escolhido.get("palavras_chave") or []

    texto_assunto = _extrair_trecho_por_palavras_chave_md(
        caminho_md, palavras_chave
    )

    if not texto_assunto.strip():
        extras = [p.strip() for p in titulo.split() if len(p.strip()) > 3]
        texto_assunto = _extrair_trecho_por_palavras_chave_md(
            caminho_md, extras
        )

    if not texto_assunto.strip():
        print(
            "\nNão foi possível localizar no texto um trecho consistente com "
            "o assunto escolhido. Operação cancelada."
        )
        return None

    print(f"\nAssunto selecionado: {titulo}")
    return titulo, texto_assunto
