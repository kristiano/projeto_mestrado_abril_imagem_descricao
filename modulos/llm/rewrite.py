# rewrite.py
# Adaptação do material didático ao perfil de aprendizagem do aluno
# Adaptado de Vaccaro et al. (2025)

import time
import re
from modulos.llm.gemini_config import criar_modelo


def adaptar_material(dimensoes: dict, assunto: str, texto: str) -> str:
    """
    Adapta o material didático ao perfil de aprendizagem do aluno.
    Divide o texto em blocos para garantir cobertura total e profundidade.

    Parâmetros:
    dimensoes: dicionário com as 4 dimensões do Felder-Silverman
    assunto  : nome do capítulo/assunto escolhido pelo aluno
    texto    : conteúdo extraído do PDF

    Retorna:
    material_adaptado: string com o material personalizado
    """

    print("\n***\nInicializando Rewrite com Chunking:")
    start_time = time.time()

    # Extrair sumário de tópicos para dar contexto global a todos os blocos
    headers = re.findall(r'^#+\s+(.*)', texto, re.MULTILINE)
    sumario = "\n".join([f"- {h}" for h in headers])

    # System message do Rewrite
    rewrite_sys_msg = (
        "# Role: Especialista em Design Instrucional e Teoria de Felder-Silverman\n\n"
        "## Missão\n"
        "Você deve adaptar um trecho de conteúdo técnico para um aluno com o perfil "
        "especificado abaixo. Você terá acesso ao Sumário Completo do material para manter o contexto.\n\n"
        "## Perfil do Aluno (ILS)\n"
        f"- **Processamento:** {dimensoes['processamento']}\n"
        f"- **Percepção:** {dimensoes['percepcao']}\n"
        f"- **Entrada:** {dimensoes['entrada']}\n"
        f"- **Compreensão:** {dimensoes['compreensao']}\n\n"
        "## Sumário do Conteúdo Integral (Contexto)\n"
        f"{sumario}\n\n"
        "## Instruções de Adaptação (Diretrizes Teóricas)\n"
        "1. **Eixo de Percepção:**\n"
        "   - Se **Sensorial**: Foque em aplicações práticas, exemplos do mundo real e dados concretos. Evite abstrações sem contexto.\n"
        "   - Se **Intuitivo**: Priorize a teoria subjacente, modelos matemáticos e a inovação conceitual.\n"
        "2. **Eixo de Entrada:**\n"
        "   - Se **Visual**: Identifique pontos onde diagramas (Venn, Circuitos, Tabelas-Verdade) ajudariam. Insira blocos de sugestão:\n"
        "     [SUGESTAO_IMAGEM: <prompt em inglês detalhado: área de estudo, descrição visual, formas, vetores, sem textos longos>]\n"
        "   - Se **Verbal**: Use explicações textuais ricas, analogias narrativas e discussões teóricas.\n"
        "3. **Eixo de Processamento:**\n"
        "   - Se **Ativo**: Insira desafios rápidos e exercícios práticos ao longo do texto.\n"
        "   - Se **Reflexivo**: Insira perguntas instigantes (caixas de reflexão) que exijam pausa para pensar.\n"
        "4. **Eixo de Compreensão:**\n"
        "   - Se **Sequencial**: Trilha linear, passo a passo, progresso lógico.\n"
        "   - Se **Global**: Comece com a 'Visão Panorâmica' (Big Picture) APENAS no primeiro bloco. Mostre como o conceito se conecta ao todo.\n\n"
        "## Regras de Rigor e Humanização (OBRIGATÓRIO)\n"
        "1. **PROIBIÇÃO DE SÍMBOLOS ISOLADOS:** Nunca apresente uma fórmula ou premissa (ex: $P \\to Q$) sem antes explicá-la em português claro. "
        "O aluno deve ser capaz de ler o material como se fosse um livro de narrativa, ignorando os símbolos se desejar.\n"
        "2. **TRADUÇÃO DE PREMISSAS:** Se o original tiver uma lista de premissas, você deve adaptá-la para frases fluidas. "
        "Exemplo: em vez de '1. $P \\to Q$', use '1. Primeiro, temos a premissa de que se P ocorrer, então Q também ocorre (representado por $P \\to Q$).'\n"
        "3. **VOCABULÁRIO DIDÁTICO:** Use termos como 'Portanto', 'Concluímos que', 'Se... então', 'Ou', 'Não'. "
        "Nunca deixe o símbolo '$\\therefore$' ou '$\\neg$' sem a tradução verbal ao lado.\n\n"
        "## Requisitos de Conteúdo e Profundidade\n"
        "O material adaptado deve ser profundo e cobrir:\n"
        "- Definição e Tabelas-Verdade completas.\n"
        "- Negação de proposições compostas (Leis de De Morgan).\n"
        "- Tautologia, Contradição e Contingência.\n"
        "- Leis de Equivalência e Simplificação de Expressões.\n"
        "- Regras de Inferência.\n"
        "- Lógica de Predicados (Quantificadores).\n"
        "- **SEÇÃO DE EXERCÍCIOS:** Se for o último bloco, inclua uma lista de exercícios variados.\n\n"
        "## Formato de Saída\n"
        "Markdown estruturado.\n\n"
        "### REGRA DE OURO — PROIBIÇÃO TOTAL DE LaTeX\n"
        "- **NUNCA** use a sintaxe `$...$` ou `$$...$$` (delimitadores LaTeX). O material será renderizado em PDF simples que NÃO interpreta LaTeX.\n"
        "- Use EXCLUSIVAMENTE caracteres Unicode para símbolos lógicos/matemáticos:\n"
        "  ¬ (negação), ∧ (conjunção/e), ∨ (disjunção/ou), ⊕ (ou-exclusivo), → (implicação), ↔ (bicondicional), "
        "∴ (portanto), ∀ (para todo), ∃ (existe), ≡ (equivalente), ≠ (diferente), ≤, ≥, × , ∈, ∉, ⊂, ⊆, ∪, ∩, ∅\n"
        "- Escreva variáveis como texto simples: P, Q, R, P₁, P₂ (use subscrito Unicode ₁₂₃ quando possível, ou _1 _2 como fallback).\n"
        "- O texto deve ser totalmente compreensível para humanos que não conhecem códigos lógicos. "
        "Símbolos Unicode devem servir apenas como apoio visual secundário entre parênteses ou em blocos explicados."
    )

    # Reduzimos o tamanho do bloco para garantir maior estabilidade e evitar respostas vazias
    tamanho_bloco = 8000
    blocos = [texto[i : i + tamanho_bloco] for i in range(0, len(texto), tamanho_bloco)]
    
    material_total = []
    model = criar_modelo(system_instruction=rewrite_sys_msg)

    for i, bloco in enumerate(blocos):
        print(f"Processando bloco {i+1}/{len(blocos)}...")
        
        contexto_bloco = (
            f"ESTE É O BLOCO {i+1} DE {len(blocos)}.\n"
            "FOCO: Adapte o texto abaixo com profundidade, ignorando o que não estiver nele, mas mantendo a coesão com o sumário.\n"
            f"{'ADICIONE A VISÃO PANORÂMICA GLOBAL AQUI.' if i == 0 else ''}\n"
            f"{'ADICIONE A SEÇÃO DE EXERCÍCIOS AO FINAL.' if i == len(blocos)-1 else ''}\n\n"
            f"TEXTO ORIGINAL PARA ADAPTAR:\n{bloco}"
        )

        try:
            response = model.generate_content(contexto_bloco)
            # Verificação de segurança: se a resposta não tem texto, tenta capturar o motivo
            if not response.candidates or not response.candidates[0].content.parts:
                 print(f"Aviso: Bloco {i+1} retornou resposta vazia. Finish Reason: {response.candidates[0].finish_reason}")
                 material_total.append(f"\n[AVISO: O conteúdo deste bloco não pôde ser adaptado pela IA (Bloqueio ou Resposta Vazia)]\n\n{bloco}")
            else:
                material_total.append(response.text)
            
            if len(blocos) > 1:
                time.sleep(2) # Aumentado para 2s para evitar exaustão de cota
        except Exception as e:
            print(f"Erro ao processar bloco {i+1}: {e}")
            material_total.append(f"\n[ERRO NA ADAPTAÇÃO: {e}]\n")

    material_adaptado = "\n\n".join(material_total)

    stop_time = time.time()
    print(f"Tempo de execução do Rewrite: {(stop_time - start_time):.2f} s\n***\n")

    return material_adaptado