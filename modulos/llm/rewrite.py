# rewrite.py
# Adaptação do material didático ao perfil de aprendizagem do aluno
# Adaptado de Vaccaro et al. (2025)

import time
from modulos.llm.gemini_config import criar_modelo


def adaptar_material(dimensoes: dict, assunto: str, texto: str) -> str:
    """
    Adapta o material didático ao perfil de aprendizagem do aluno.

    Parâmetros:
    dimensoes: dicionário com as 4 dimensões do Felder-Silverman
    assunto  : nome do capítulo/assunto escolhido pelo aluno
    texto    : conteúdo extraído do PDF

    Retorna:
    material_adaptado: string com o material personalizado
    """

    print("\n***\nInicializando Rewrite:")
    start_time = time.time()

    # System message do Rewrite (Usando a estrutura do Orientador)
    rewrite_sys_msg = (
        "# Role: Especialista em Design Instrucional e Teoria de Felder-Silverman\n\n"
        "## Contexto\n"
        "Sou um professor universitário e preciso adaptar um conteúdo técnico para um "
        "aluno com um perfil de aprendizagem específico, baseado no Index of Learning Styles (ILS).\n\n"
        "## Instruções de Adaptação (Diretrizes Teóricas)\n"
        "Utilize as seguintes restrições baseadas nos polos de Felder e Silverman:\n\n"
        "1. **Eixo de Percepção:**\n"
        "   - Se **Sensorial**: Foque em aplicações práticas, exemplos do mundo real e dados concretos.\n"
        "   - Se **Intuitivo**: Priorize a teoria subjacente, modelos matemáticos e a inovação conceitual.\n"
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
        "   - Se **Global**: Comece apresentando o objetivo macro e a utilidade final do conceito antes de mergulhar nos detalhes.\n\n"
        "## Formato de Saída\n"
        "Gere o conteúdo estruturado em Markdown. Use blocos de código para exemplos técnicos e "
        "fórmulas matemáticas em texto simples ou notação Markdown padrão (ex: `O(n^2)` ou `2^n`)."
    )

    # User message com o perfil do aluno e o conteúdo acoplado as variáveis
    rewrite_user_msg = (
        f"## Dados do Aluno (Perfil FSLM)\n"
        f"- **Processamento:** {dimensoes['processamento']}\n"
        f"- **Percepção:** {dimensoes['percepcao']}\n"
        f"- **Entrada:** {dimensoes['entrada']}\n"
        f"- **Compreensão:** {dimensoes['compreensao']}\n\n"
        f"## Conteúdo a ser Adaptado\n"
        f"TEMA ESCOLHIDO: {assunto}\n\n"
        f"INFORMAÇÃO ORIGINAL RETIRADA DA APOSTILA:\n{texto[:8000]}\n"
    )

    # Cria o modelo com o system message
    model = criar_modelo(system_instruction=rewrite_sys_msg)

    # Gera o material adaptado
    response = model.generate_content(rewrite_user_msg)
    material_adaptado = response.text

    stop_time = time.time()
    print(f"Tempo de execução do Rewrite: {(stop_time - start_time):.2f} s\n***\n")

    return material_adaptado