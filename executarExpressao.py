import math

# ---------------------------------------------
#  Tipos de token (espelho do Aluno 1)
# ---------------------------------------------
TOKEN_NUM       = "NUM"
TOKEN_OP        = "OP"
TOKEN_LPAREN    = "LPAREN"
TOKEN_RPAREN    = "RPAREN"
TOKEN_RES       = "RES"
TOKEN_MEM_STORE = "MEM_STORE"
TOKEN_MEM_LOAD  = "MEM_LOAD"
TOKEN_EOF       = "EOF"


# ---------------------------------------------
#  Estado global compartilhado
# ---------------------------------------------
memoria   = {"MEM": 0.0}
historico = []


# ---------------------------------------------
#  Operacoes aritmeticas (IEEE 754 / 64 bits)
# ---------------------------------------------
def _aplicar_op(op, esq, dir):
    if op == '+':  return esq + dir
    if op == '-':  return esq - dir
    if op == '*':  return esq * dir
    if op == '/':
        if dir == 0: raise ZeroDivisionError("Divisao por zero")
        return esq / dir
    if op == '//':
        if dir == 0: raise ZeroDivisionError("Divisao inteira por zero")
        return float(int(esq) // int(dir))
    if op == '%':
        if dir == 0: raise ZeroDivisionError("Resto por zero")
        return float(int(esq) % int(dir))
    if op == '^':  return math.pow(esq, dir)
    raise ValueError(f"Operador desconhecido: '{op}'")


# ---------------------------------------------
#  Funcao principal
# ---------------------------------------------
def executarExpressao(tokens, mem=None, hist=None, debug=False):
    if mem  is None: mem  = memoria
    if hist is None: hist = historico

    pilha = []

    def _estado():
        print(f"      pilha   = {pilha}")
        print(f"      mem     = {dict(mem)}")
        print(f"      hist    = {list(hist)}")

    if debug:
        print("  [INICIO]")
        _estado()

    for i, tok in enumerate(tokens):
        if debug:
            print(f"\n  [TOKEN {i}] tipo={tok.tipo:<12} valor={repr(tok.valor)}")

        # -- Ignora parenteses --
        if tok.tipo in (TOKEN_LPAREN, TOKEN_RPAREN):
            if debug: print(f"    -> ignorado")
            continue

        # -- Numero: empilha --
        if tok.tipo == TOKEN_NUM:
            pilha.append(float(tok.valor))
            if debug:
                print(f"    -> empilhou {float(tok.valor)}")
                _estado()

        # -- Operador --
        elif tok.tipo == TOKEN_OP:
            if len(pilha) < 2:
                raise RuntimeError(f"Pilha insuficiente para '{tok.valor}'")
            dir_ = pilha.pop()
            esq  = pilha.pop()
            res  = _aplicar_op(tok.valor, esq, dir_)
            pilha.append(res)
            if debug:
                print(f"    -> {esq} {tok.valor} {dir_} = {res}")
                _estado()

        # -- MEM_STORE pode ser (V MEM) ou (MEM) dependendo da pilha --
        # O Aluno 1 emite MEM_STORE nos dois casos; diferenciamos pelo contexto:
        # se a pilha tem valor  -> (V MEM): salva V em mem e mantem V como resultado
        # se a pilha esta vazia -> (MEM):   carrega mem para a pilha
        elif tok.tipo == TOKEN_MEM_STORE:
            if pilha:
                # (V MEM): salva mas mantem o valor na pilha como resultado
                valor_salvo = pilha[-1]   # peek - nao remove
                mem["MEM"] = valor_salvo
                if debug:
                    print(f"    -> (V MEM): salvou {valor_salvo} em mem['MEM'], pilha mantida")
                    _estado()
            else:
                # (MEM): pilha vazia significa load
                valor_carregado = mem.get("MEM", 0.0)
                pilha.append(valor_carregado)
                if debug:
                    print(f"    -> (MEM): carregou mem['MEM'] = {valor_carregado}")
                    _estado()

        # -- TOKEN_MEM_LOAD caso o Aluno 1 venha a emiti-lo no futuro --
        elif tok.tipo == TOKEN_MEM_LOAD:
            valor_carregado = mem.get("MEM", 0.0)
            pilha.append(valor_carregado)
            if debug:
                print(f"    -> MEM_LOAD: carregou mem['MEM'] = {valor_carregado}")
                _estado()

        # -- (N RES): N ja esta na pilha, busca no historico --
        elif tok.tipo == TOKEN_RES:
            if not pilha:
                raise RuntimeError("Pilha vazia ao ler RES")
            n = int(pilha.pop())
            if debug:
                print(f"    -> N={n}, tamanho do hist={len(hist)}")
                print(f"    -> hist completo: {list(hist)}")
            if n < 1 or n > len(hist):
                raise IndexError(
                    f"RES({n}) invalido: historico tem {len(hist)} entradas"
                )
            valor_res = hist[-n]
            pilha.append(valor_res)
            if debug:
                print(f"    -> hist[-{n}] = {valor_res}")
                _estado()

    if debug:
        print(f"\n  [FIM DO LOOP]")
        _estado()

    if len(pilha) != 1:
        raise RuntimeError(
            f"Expressao malformada: pilha terminou com {len(pilha)} elemento(s)"
        )

    resultado = pilha[0]
    hist.append(resultado)

    if debug:
        print(f"\n  [RESULTADO] {resultado} adicionado ao historico")
        _estado()

    return resultado


# ---------------------------------------------
#  Testes
# ---------------------------------------------
def _fmt(v):
    return str(int(v)) if isinstance(v, float) and v == int(v) else str(v)
