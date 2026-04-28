# questionario.py
# Questionário Reduzido de Felder-Silverman
# Baseado no Artigo 3 - Troussas et al. (Entropy 2020)

def aplicar_questionario():
    print("\n" + "="*60)
    print("   QUESTIONÁRIO DE ESTILO DE APRENDIZAGEM")
    print("   Baseado no Modelo de Felder-Silverman")
    print("="*60)
    print("\nResponda as questões abaixo com (a) ou (b).\n")

    respostas = {}

    questoes = [
        {
            "dimensao": "dimensao_compreensao",
            "numero": 1,
            "enunciado": "Quando estudo um novo assunto, prefiro:",
            "opcao_a": "Aprender o conteúdo em etapas claras e permanecer focado.",
            "opcao_b": "Ter uma visão geral das conexões entre esse assunto e outros relacionados."
        },
        {
            "dimensao": "dimensao_percepcao",
            "numero": 2,
            "enunciado": "Prefiro aulas que enfatizem:",
            "opcao_a": "Material concreto, como dados e fatos.",
            "opcao_b": "Material teórico e conceitual, como teorias e conceitos."
        },
        {
            "dimensao": "dimensao_entrada",
            "numero": 3,
            "enunciado": "Quando recebo dados e informações, prefiro:",
            "opcao_a": "Concentrar-me em figuras, gráficos e tabelas.",
            "opcao_b": "Prestar atenção em explicações orais ou textos escritos que resumam os resultados."
        },
        {
            "dimensao": "dimensao_processamento",
            "numero": 4,
            "enunciado": "Prefiro aprender:",
            "opcao_a": "Em grupo, discutindo o conteúdo com outras pessoas.",
            "opcao_b": "Sozinho, refletindo sobre o conteúdo individualmente."
        }
    ]

    for questao in questoes:
        print(f"Questão {questao['numero']}: {questao['enunciado']}")
        print(f"   (a) {questao['opcao_a']}")
        print(f"   (b) {questao['opcao_b']}")
        
        while True:
            resposta = input("\n   Sua resposta (a/b): ").strip().lower()
            if resposta in ["a", "b"]:
                respostas[questao["dimensao"]] = resposta
                print()
                break
            else:
                print("   ⚠ Resposta inválida! Digite apenas (a) ou (b).")

    return respostas


def mapear_dimensoes(respostas):
    dimensoes = {
        "compreensao": "Sequencial" if respostas["dimensao_compreensao"] == "a" else "Global",
        "percepcao": "Sensorial" if respostas["dimensao_percepcao"] == "a" else "Intuitivo",
        "entrada": "Visual" if respostas["dimensao_entrada"] == "a" else "Verbal",
        "processamento": "Ativo" if respostas["dimensao_processamento"] == "a" else "Reflexivo"
    }
    return dimensoes


def exibir_resultado(dimensoes):
    print("\n" + "="*60)
    print("   RESULTADO DO SEU PERFIL DE APRENDIZAGEM")
    print("="*60)
    print(f"\n  Compreensão  : {dimensoes['compreensao']}")
    print(f"  Percepção    : {dimensoes['percepcao']}")
    print(f"  Entrada      : {dimensoes['entrada']}")
    print(f"  Processamento: {dimensoes['processamento']}")
    print("\n" + "="*60)