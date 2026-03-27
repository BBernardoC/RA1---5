"""
Bernardo Czizyk - BBernardo C
Nestor Gazarra Sondhal - RSG616
"""


import sys
import os
from lerArquivo        import lerArquivo
from parse_expressao    import parseExpressao, exportar_tokens_txt
from executarExpressao import executarExpressao
from gerarAssembly     import gerarAssembly
from exibirResultados  import exibirResultados




# Main
def main():
    # -- argumento de linha de comando --
    if len(sys.argv) < 2:
        print("Uso: python main.py <arquivo_de_teste.txt>")
        sys.exit(1)

    caminho = sys.argv[1]

    print(f"\n[INFO] Lendo arquivo: {caminho}")

    #aluno 3 le o arquivo
    linhas = lerArquivo(caminho)
    print(f"[INFO] {len(linhas)} expressao(oes) encontrada(s)\n")

    #stado compartilhado entre expressoes
    mem  = {"MEM": 0.0}
    hist = []

    expressoes      = []   # textos originais
    resultados      = []   # floats calculados
    lista_tokens    = []   # tokens por linha (para Assembly)

    #alunos 1 e 2 pars + exec 
    for i, linha in enumerate(linhas):
        try:
            tokens, _ = parseExpressao(linha, num_linha=i + 1)
            resultado = executarExpressao(tokens, mem, hist)

            expressoes.append(linha)
            resultados.append(resultado)
            lista_tokens.append(tokens)

        except SyntaxError as e:
            print(f"[ERRO LEXICO/SINTATICO] Linha {i+1}: {e}", file=sys.stderr)
            expressoes.append(linha)
            resultados.append(None)
            lista_tokens.append([])

        except Exception as e:
            print(f"[ERRO EXECUCAO] Linha {i+1}: {e}", file=sys.stderr)
            expressoes.append(linha)
            resultados.append(None)
            lista_tokens.append([])

    # aluno 4exibe resultado
    exibirResultados(expressoes, resultados)

    #luno 3 gera Assembl
    nome_base  = os.path.splitext(os.path.basename(caminho))[0]
    saida_asm  = f"{nome_base}.s"
    gerarAssembly(lista_tokens, caminho_saida=saida_asm)
    print(f"[INFO] Assembly gerado -> {saida_asm}\n")

    #Aluno 1: exporta tok
    saida_tokens = f"{nome_base}_tokens.txt"
    resultados_export = []
    for i, (expr, tokens) in enumerate(zip(expressoes, lista_tokens)):
        resultados_export.append({
            'linha' : i + 1,
            'texto' : expr,
            'tokens': tokens,
            'arvore': None,
        })
    exportar_tokens_txt(resultados_export, saida_tokens)
    print(f"[INFO] Tokens exportados -> {saida_tokens}")


if __name__ == "__main__":
    main()
