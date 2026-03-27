# Ler arquivos
import sys
import os

def lerArquivo(caminho):
    """
    Le o arquivo de entrada e retorna as linhas validas
    (ignora linhas vazias e comentarios com #).

    Parametros:
        caminho - str : caminho do arquivo .txt

    Retorna:
        list[str] : linhas validas do arquivo
    """
    if not os.path.exists(caminho):
        print(f"[ERRO] Arquivo nao encontrado: {caminho}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            linhas = f.readlines()
    except Exception as e:
        print(f"[ERRO] Falha ao abrir o arquivo: {e}", file=sys.stderr)
        sys.exit(1)

    validas = []
    for linha in linhas:
        linha = linha.rstrip('\n')
        if linha.strip() and not linha.strip().startswith('#'):
            validas.append(linha.strip())

    if not validas:
        print(f"[AVISO] Arquivo '{caminho}' nao contem expressoes validas.")
        sys.exit(0)

    return validas
