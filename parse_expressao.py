import sys

TOKEN_NUM       = "NUM"
TOKEN_OP        = "OP"
TOKEN_LPAREN    = "LPAREN"
TOKEN_RPAREN    = "RPAREN"
TOKEN_RES       = "RES"
TOKEN_MEM_STORE = "MEM_STORE"
TOKEN_MEM_LOAD  = "MEM_LOAD"
TOKEN_EOF       = "EOF"


class Token:
    def __init__(self, tipo, valor, linha=0, coluna=0):
        self.tipo   = tipo
        self.valor  = valor
        self.linha  = linha
        self.coluna = coluna

    def __repr__(self):
        return f"Token({self.tipo}, {repr(self.valor)}, L{self.linha}:C{self.coluna})"

    def to_dict(self):
        return {'tipo': self.tipo, 'valor': self.valor,
                'linha': self.linha, 'coluna': self.coluna}


class No:
    def __init__(self, tipo, valor=None, filhos=None):
        self.tipo   = tipo
        self.valor  = valor
        self.filhos = filhos or []

    def __repr__(self, nivel=0):
        indent = "  " * nivel
        s = f"{indent}No({self.tipo}, {repr(self.valor)})\n"
        for f in self.filhos:
            s += f.__repr__(nivel + 1)
        return s

    def to_dict(self):
        return {
            'tipo'  : self.tipo,
            'valor' : self.valor,
            'filhos': [f.to_dict() for f in self.filhos],
        }


class AnalisadorLexico:
    def __init__(self, texto, num_linha=0):
        self._texto   = texto
        self._pos     = 0
        self._linha   = num_linha
        self._tokens  = []
        self._buffer  = ""
        self._col_ini = 0

    def tokenizar(self):
        self._estado_inicio()
        return self._tokens

    def _atual(self):
        return self._texto[self._pos] if self._pos < len(self._texto) else '\0'

    def _avanca(self):
        c = self._atual()
        self._pos += 1
        return c

    def _emite(self, tipo, valor=None):
        val = valor if valor is not None else self._buffer
        self._tokens.append(Token(tipo, val, self._linha, self._col_ini))
        self._buffer = ""

    def _erro(self, msg):
        raise SyntaxError(f"[Lexico] L{self._linha}:C{self._pos} - {msg}")

    def _estado_inicio(self):
        while True:
            self._col_ini = self._pos
            c = self._avanca()
            if c in ('\0', '\n'):
                return
            if c in (' ', '\t', '\r'):
                continue
            if c == '#':
                return
            if c == '(':
                self._emite(TOKEN_LPAREN, '(')
            elif c == ')':
                self._emite(TOKEN_RPAREN, ')')
            elif c == '+':
                self._emite(TOKEN_OP, '+')
            elif c == '%':
                self._emite(TOKEN_OP, '%')
            elif c == '^':
                self._emite(TOKEN_OP, '^')
            elif c == '-':
                self._buffer = c
                self._estado_menos()
            elif c == '*':
                self._buffer = c
                self._estado_op_estrela()
            elif c == '/':
                self._buffer = c
                self._estado_op_barra()
            elif c.isdigit():
                self._buffer = c
                self._estado_num_inteiro()
            elif c.isalpha() or c == '_':
                self._buffer = c
                self._estado_palavra()
            else:
                self._erro(f"Caractere inesperado '{c}'")

    def _estado_menos(self):
        c = self._atual()
        ultimo_tipo = self._tokens[-1].tipo if self._tokens else None
        if c.isdigit() and ultimo_tipo in (TOKEN_LPAREN, None):
            self._buffer += self._avanca()
            self._estado_num_inteiro()
        else:
            self._emite(TOKEN_OP, '-')

    def _estado_op_barra(self):
        if self._atual() == '/':
            self._buffer += self._avanca()
            self._emite(TOKEN_OP, '//')
        else:
            self._emite(TOKEN_OP, '/')

    def _estado_op_estrela(self):
        self._emite(TOKEN_OP, '*')

    def _estado_num_inteiro(self):
        while True:
            c = self._atual()
            if c.isdigit():
                self._buffer += self._avanca()
            elif c == '.':
                self._buffer += self._avanca()
                self._estado_num_ponto()
                return
            elif c in ('e', 'E'):
                self._buffer += self._avanca()
                self._estado_num_exp_e()
                return
            else:
                self._emite(TOKEN_NUM)
                return

    def _estado_num_ponto(self):
        c = self._atual()
        if c.isdigit():
            self._buffer += self._avanca()
            self._estado_num_decimal()
        else:
            self._erro(f"Digito esperado apos '.', encontrou '{c}'")

    def _estado_num_decimal(self):
        while True:
            c = self._atual()
            if c.isdigit():
                self._buffer += self._avanca()
            elif c in ('e', 'E'):
                self._buffer += self._avanca()
                self._estado_num_exp_e()
                return
            else:
                self._emite(TOKEN_NUM)
                return

    def _estado_num_exp_e(self):
        c = self._atual()
        if c in ('+', '-'):
            self._buffer += self._avanca()
            self._estado_num_exp_sinal()
        elif c.isdigit():
            self._estado_num_exp_digito()
        else:
            self._erro(f"Sinal ou digito esperado no expoente, encontrou '{c}'")

    def _estado_num_exp_sinal(self):
        c = self._atual()
        if c.isdigit():
            self._estado_num_exp_digito()
        else:
            self._erro(f"Digito esperado apos sinal do expoente, encontrou '{c}'")

    def _estado_num_exp_digito(self):
        while True:
            c = self._atual()
            if c.isdigit():
                self._buffer += self._avanca()
            else:
                self._emite(TOKEN_NUM)
                return

    def _estado_palavra(self):
        while True:
            c = self._atual()
            if c.isalnum() or c == '_':
                self._buffer += self._avanca()
            else:
                palavra = self._buffer.upper()
                if palavra == "RES":
                    self._emite(TOKEN_RES, "RES")
                elif palavra == "MEM":
                    self._emite(TOKEN_MEM_STORE, "MEM")
                else:
                    self._erro(f"Identificador desconhecido: '{self._buffer}'")
                return


class ParserRPN:
    def __init__(self, tokens):
        self._tokens = tokens
        self._pos    = 0

    def _atual(self):
        if self._pos < len(self._tokens):
            return self._tokens[self._pos]
        return Token(TOKEN_EOF, None)

    def _peek(self, offset=1):
        idx = self._pos + offset
        if idx < len(self._tokens):
            return self._tokens[idx]
        return Token(TOKEN_EOF, None)

    def _consome(self, tipo=None):
        tok = self._atual()
        if tipo and tok.tipo != tipo:
            raise SyntaxError(
                f"[Parser] Esperado '{tipo}', encontrou '{tok.tipo}' "
                f"('{tok.valor}') L{tok.linha}:C{tok.coluna}"
            )
        self._pos += 1
        return tok

    def parse(self):
        no = self._parse_expressao()
        if self._atual().tipo != TOKEN_EOF:
            tok = self._atual()
            raise SyntaxError(f"[Parser] Token inesperado apos expressao: {tok}")
        return no

    def _parse_expressao(self):
        self._consome(TOKEN_LPAREN)
        no = self._parse_conteudo()
        self._consome(TOKEN_RPAREN)
        return no

    def _parse_conteudo(self):
        tok  = self._atual()
        prox = self._peek()

        if tok.tipo == TOKEN_MEM_STORE and prox.tipo == TOKEN_RPAREN:
            self._consome(TOKEN_MEM_STORE)
            return No("MEM_LOAD", "MEM")

        if tok.tipo == TOKEN_NUM and prox.tipo == TOKEN_RES:
            num = self._consome(TOKEN_NUM)
            self._consome(TOKEN_RES)
            return No("RES", int(float(num.valor)))

        if tok.tipo == TOKEN_NUM and prox.tipo == TOKEN_MEM_STORE:
            num = self._consome(TOKEN_NUM)
            self._consome(TOKEN_MEM_STORE)
            return No("MEM_STORE", num.valor)

        esq = self._parse_elemento()
        if self._atual().tipo == TOKEN_RPAREN:
            return esq  # Retorna o elemento diretamente
        
        # Caso normal: elemento, elemento, operador
        dir = self._parse_elemento()
        op  = self._consome(TOKEN_OP)
        return No("OP", op.valor, [esq, dir])

    def _parse_elemento(self):
        tok = self._atual()
        if tok.tipo == TOKEN_NUM:
            self._consome(TOKEN_NUM)
            return No("NUM", tok.valor)
        if tok.tipo == TOKEN_LPAREN:
            return self._parse_expressao()
        raise SyntaxError(
            f"[Parser] Elemento esperado, encontrou '{tok.tipo}' "
            f"L{tok.linha}:C{tok.coluna}"
        )


def parseExpressao(linha, num_linha=0):
    linha = linha.strip()
    if not linha or linha.startswith('#'):
        return [], None
    lexer  = AnalisadorLexico(linha, num_linha)
    tokens = lexer.tokenizar()
    parser = ParserRPN(tokens)
    arvore = parser.parse()
    return tokens, arvore


def processar_arquivo(caminho):
    resultados = []
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            linhas = f.readlines()
    except FileNotFoundError:
        print(f"[ERRO] Arquivo nao encontrado: {caminho}", file=sys.stderr)
        sys.exit(1)

    for i, texto in enumerate(linhas, start=1):
        texto = texto.rstrip('\n')
        if not texto.strip() or texto.strip().startswith('#'):
            continue
        try:
            tokens, arvore = parseExpressao(texto, i)
            resultados.append({
                'linha' : i,
                'texto' : texto,
                'tokens': tokens,
                'arvore': arvore,
            })
        except SyntaxError as e:
            print(f"[ERRO] {e}", file=sys.stderr)
            resultados.append({
                'linha' : i,
                'texto' : texto,
                'tokens': [],
                'arvore': None,
            })
    return resultados


def exportar_tokens_txt(resultados, caminho_saida):
    with open(caminho_saida, 'w', encoding='utf-8') as f:
        f.write("# TIPO\tVALOR\tLINHA\tCOLUNA\n")
        for r in resultados:
            f.write(f"# --- Linha {r['linha']}: {r['texto']}\n")
            for tok in r['tokens']:
                f.write(f"{tok.tipo}\t{tok.valor}\t{tok.linha}\t{tok.coluna}\n")
            f.write("\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python parse_expressao.py <arquivo.txt>")
        sys.exit(1)

    caminho    = sys.argv[1]
    resultados = processar_arquivo(caminho)

    for r in resultados:
        print(f"\nLinha {r['linha']}: {r['texto']}")
        for tok in r['tokens']:
            print(f"  {tok.tipo:<12} | {repr(tok.valor)}")
        if r['arvore']:
            print(r['arvore'])

    saida = caminho.rsplit('.', 1)[0] + "_tokens.txt"
    exportar_tokens_txt(resultados, saida)
    print(f"\n[INFO] Tokens exportados -> {saida}")