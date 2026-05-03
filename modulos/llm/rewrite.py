# rewrite.py
# Adaptação do material didático ao perfil de aprendizagem do aluno
# Adaptado e Refatorado

import time
import re
import textwrap
from modulos.llm.gemini_config import criar_modelo

def adaptar_material(dimensoes: dict, assunto: str, texto: str) -> str:
    """
    Adapta o material didático ao perfil de aprendizagem do aluno.
    Divide o texto em blocos respeitando parágrafos para garantir integridade.

    Parâmetros:
    dimensoes: dicionário com as 4 dimensões do Felder-Silverman
    assunto  : nome do capítulo/assunto escolhido pelo aluno
    texto    : conteúdo extraído do PDF

    Retorna:
    material_adaptado: string com o material personalizado
    """

    print("\n***\nInicializando Rewrite com Chunking Inteligente:")
    start_time = time.time()

    # 1. Extrair sumário para contexto global
    headers = re.findall(r'^#+\s+(.*)', texto, re.MULTILINE)
    sumario = "\n".join([f"- {h}" for h in headers])

    # 2. System Message Dinâmica
    rewrite_sys_msg = (
        f"# Role: Especialista em Design Instrucional e Teoria de Felder-Silverman\n\n"
        "## Contexto\n"
        f"Você deve adaptar um trecho de conteúdo sobre **{assunto}** para um aluno com o perfil "
        "especificado abaixo. Você terá acesso ao Sumário Completo do material para manter o contexto.\n\n"
        "## Perfil do Aluno (ILS)\n"
        f"- **Processamento:** {dimensoes['processamento']}\n"
        f"- **Percepção:** {dimensoes['percepcao']}\n"
        f"- **Entrada:** {dimensoes['entrada']}\n"
        f"- **Compreensão:** {dimensoes['compreensao']}\n\n"
        "## Sumário do Conteúdo Integral (Contexto)\n"
        f"{sumario}\n\n"
        "## Instruções de Adaptação (Diretrizes Teóricas)\n"
        "Utilize as seguintes restrições baseadas nos polos de Felder e Silverman:\n\n"
        "1. **Eixo de Percepção:**\n"
        "   - Se **Sensorial**: Foque em aplicações práticas, exemplos do mundo real e dados concretos.\n"
        "   - Se **Intuitivo**: Priorize a teoria subjacente, modelos e conceitos abstratos.\n"
        "2. **Eixo de Entrada:**\n"
        "   - Se **Visual**: Ao longo do texto, identifique os pontos onde uma representação visual ajudaria e insira blocos de sugestão no formato exato abaixo:\n"
        "     [SUGESTAO_IMAGEM: <prompt em inglês detalhado: inicie citando a área de estudo (ex: Computer Science), depois descreva visualmente o diagrama usando formas simples, vetores e estrutura do conceito. Peça um design sem textos longos (textless)>]\n"
        "     Insira esses blocos em momentos estratégicos: ao introduzir um conceito abstrato, ao representar um fluxo ou processo, ao comparar elementos, ou ao apresentar dados com padrões e tendências.\n"
        "   - Se **Verbal**: Utilize explicações textuais detalhadas, analogias narrativas e discussões teóricas.\n"
        "3. **Eixo de Processamento:**\n"
        "   - Se **Ativo**: Insira uma atividade de \"mão na massa\" ou um desafio imediato para o aluno testar.\n"
        "   - Se **Reflexivo**: Insira perguntas instigantes que exijam reflexão e pausa interpretativa longa antes de prosseguir.\n"
        "4. **Eixo de Compreensão:**\n"
        "   - Se **Sequencial**: Apresente o conteúdo em uma trilha linear, passo a passo, garantindo que cada etapa dependa da anterior.\n"
        "   - Se **Global**: Comece apresentando o objetivo macro e a utilidade final do conceito antes de mergulhar nos detalhes. \n\n"
        "## Requisitos de Conteúdo\n"
        f"Mantenha a profundidade técnica do assunto '{assunto}'. Preserve definições, exemplos e dados técnicos do texto original. "
        "**IMPORTANTE:** Traduza fórmulas lógicas e símbolos para linguagem natural (ex: use 'não p e não q' em vez de apenas símbolos lógicos ou LaTeX complexos). Se desejar manter o rigor, coloque o símbolo entre parênteses após a tradução verbal, mas a leitura deve ser fluida e 'humana'. Se for o último bloco, inclua uma seção de exercícios práticos baseados no conteúdo adaptado.\n\n"
        "## Formato de Saída\n"
        "Markdown estruturado. Evite blocos excessivos de LaTeX; prefira explicações verbais claras para as operações lógicas."
    )

    # 3. Chunking Inteligente (respeita parágrafos)
    # Tenta dividir por parágrafos duplos para não cortar frases ao meio
    tamanho_bloco = 15000
    paragrafos = texto.split('\n\n')
    blocos = []
    bloco_atual = ""

    for p in paragrafos:
        # Se adicionar o parágrafo não estourar o limite, adiciona
        if len(bloco_atual) + len(p) < tamanho_bloco:
            bloco_atual += p + "\n\n"
        else:
            # Se estourar, salva o bloco atual e começa um novo
            if bloco_atual:
                blocos.append(bloco_atual.strip())
            bloco_atual = p + "\n\n"
    
    # Adiciona o último bloco restante
    if bloco_atual:
        blocos.append(bloco_atual.strip())
    
    # Caso o texto não tenha parágrafos (texto corrido), usa o método antigo como fallback
    if not blocos and len(texto) > 0:
        blocos = [texto[i : i + tamanho_bloco] for i in range(0, len(texto), tamanho_bloco)]

    material_total = []
    model = criar_modelo(system_instruction=rewrite_sys_msg)

    print(f"Total de blocos a processar: {len(blocos)}")

    for i, bloco in enumerate(blocos):
        print(f"Processando bloco {i+1}/{len(blocos)}...")
        
        contexto_bloco = (
            f"ESTE É O BLOCO {i+1} DE {len(blocos)}.\n"
            "FOCO: Adapte o texto abaixo mantendo a coesão com o sumário geral.\n"
            f"{'**IMPORTANTE:** Adicione a Visão Panorâmica (Big Picture) inicial aqui.' if i == 0 else ''}\n"
            f"{'**IMPORTANTE:** Adicione a Seção de Exercícios Final aqui.' if i == len(blocos)-1 else ''}\n\n"
            f"TEXTO ORIGINAL PARA ADAPTAR:\n{bloco}"
        )

        try:
            response = model.generate_content(contexto_bloco)
            material_total.append(response.text)
            # Pequena pausa para evitar rate limit em APIs gratuitas
            if len(blocos) > 1:
                time.sleep(2) 
        except Exception as e:
            print(f"Erro ao processar bloco {i+1}: {e}")
            # Adiciona o texto original em caso de erro para não perder conteúdo
            material_total.append(f"\n[ERRO NA ADAPTAÇÃO: {e}]\n\nConteúdo Original:\n{bloco}")

    material_adaptado = "\n\n---\n\n".join(material_total) # Separador visual entre blocos

    stop_time = time.time()
    print(f"Tempo de execução do Rewrite: {(stop_time - start_time):.2f} s\n***\n")

    return material_adaptado