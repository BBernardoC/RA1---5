import os

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


# ---------------------------------------------
#  Cabecalho ARMv7 + habilitacao VFP
# ---------------------------------------------
def _cabecalho(instrucoes):
    instrucoes += [
        ".syntax unified",
        ".arch armv7-a",
        ".fpu vfp",
        ".text",
        ".global main",
        "main:",
        "",
        "    @ Habilitar VFP",
        "    MRC p15, 0, r0, c1, c0, 2",
        "    ORR r0, r0, #0xF00000",
        "    MCR p15, 0, r0, c1, c0, 2",
        "    ISB",
        "    MOV r0, #0x40000000",
        "    VMSR FPEXC, r0",
        "",
    ]


def _mostrar_resultado(instrucoes, sreg):
    instrucoes += [
        f"",
        f"    @ Exibe resultado de s{sreg} nos LEDs",
        f"    PUSH {{r4, r5}}         @ salva r4/r5 (callee-saved AAPCS)",
        f"    VCVT.F64.F32 d0, s{sreg}",
        f"    VMOV r4, r5, d0",
        f"    LDR r1, =0xFF200000",
        f"    STR r5, [r1]          @ MSB (parte alta)",
        f"    MOV r0, #0",
        f"    STR r0, [r1]          @ apaga",
        f"    STR r4, [r1]          @ LSB (parte baixa)",
        f"    MOV r0, #0",
        f"    STR r0, [r1]          @ apaga",
        f"    POP {{r4, r5}}          @ restaura r4/r5",
    ]


# ---------------------------------------------
#  Gera instrucoes para (N RES)
# ---------------------------------------------
def _gerar_res(instrucoes, creg, linha_idx, literais):
    reg_n   = creg - 1          # registrador que contem N
    lbl_ok  = f"res_ok_{linha_idx}_{creg}"
    lbl_end = f"res_end_{linha_idx}_{creg}"
    lbl_zero = f"num_{len(literais)}"
    literais.append((lbl_zero, "0.0"))

    instrucoes += [
        f"",
        f"    @ (N RES) - busca resultado N posicoes atras",
        f"    VCVT.S32.F32 s{reg_n}, s{reg_n}",   
        f"    VMOV r1, s{reg_n}",                   # r1 = N
        f"    LDR r2, ={linha_idx}",                # r2 = indice linha atual
        f"    SUB r1, r2, r1",                      # r1 = linha_atual - N
        f"    CMP r1, #0",
        f"    BGE {lbl_ok}",
        f"    @ indice invalido -> empilha 0.0",
        f"    LDR r2, ={lbl_zero}",
        f"    VLDR s{reg_n}, [r2]",
        f"    B {lbl_end}",
        f"{lbl_ok}:",
        f"    LDR r2, =res_array",
        f"    ADD r2, r2, r1, LSL #2",              
        f"    VLDR s{reg_n}, [r2]",                 
        f"{lbl_end}:",
    ]
    # N e substituido pelo valor buscado, contador nao muda


# ---------------------------------------------
#  Funcao principal
# ---------------------------------------------
def gerarAssembly(lista_tokens_por_linha, caminho_saida="assembly.s"):
    """
    Recebe uma lista onde cada elemento eh a lista de tokens de uma linha.
    Gera Assembly ARMv7 e salva em caminho_saida.

    Parametros:
        lista_tokens_por_linha  - list[list[Token]]
        caminho_saida           - str, caminho do arquivo .s gerado

    Retorna:
        caminho_saida
    """
    instrucoes = []
    literais   = []   # (label, valor_float) para secao .data
    memorias   = []   # labels de variaveis MEM criadas

    _cabecalho(instrucoes)

    for linha_idx, tokens in enumerate(lista_tokens_por_linha):
        creg               = 0      # contador de registrador (topo da pilha virtual)
        ultimo_foi_numero  = False  # flag para distinguir (V MEM) de (MEM)

        instrucoes.append(f"    @ ---- linha {linha_idx} ----")

        for tok in tokens:

            # -- Ignora parenteses --
            if tok.tipo in (TOKEN_LPAREN, TOKEN_RPAREN):
                continue

            # -- Numero: carrega literal em sreg e empilha --
            elif tok.tipo == TOKEN_NUM:
                label = f"num_{len(literais)}"
                literais.append((label, tok.valor))
                instrucoes += [
                    f"",
                    f"    @ Carrega {tok.valor} -> s{creg}",
                    f"    LDR r0, ={label}",
                    f"    VLDR s{creg}, [r0]",
                ]
                creg += 1
                ultimo_foi_numero = True

            # -- Operador --
            elif tok.tipo == TOKEN_OP:
                ultimo_foi_numero = False
                rdir = creg - 1
                resq = creg - 2
                op   = tok.valor

                instrucoes.append(f"")
                instrucoes.append(f"    @ Operacao {op}: s{resq} {op} s{rdir} -> s{resq}")

                if op == '+':
                    instrucoes.append(f"    VADD.F32 s{resq}, s{resq}, s{rdir}")

                elif op == '-':
                    instrucoes.append(f"    VSUB.F32 s{resq}, s{resq}, s{rdir}")

                elif op == '*':
                    instrucoes.append(f"    VMUL.F32 s{resq}, s{resq}, s{rdir}")

                elif op == '/':
                    instrucoes.append(f"    VDIV.F32 s{resq}, s{resq}, s{rdir}")

                elif op == '//':
                    instrucoes += [
                        f"    VDIV.F32 s{resq}, s{resq}, s{rdir}",
                        f"    VCVT.S32.F32 s{resq}, s{resq}",   # trunca para int
                        f"    VCVT.F32.S32 s{resq}, s{resq}",   # volta para float
                    ]

                elif op == '%':
                    stmp = creg   # registrador temporario
                    instrucoes += [
                        f"    VDIV.F32 s{stmp}, s{resq}, s{rdir}",
                        f"    VCVT.S32.F32 s{stmp}, s{stmp}",
                        f"    VCVT.F32.S32 s{stmp}, s{stmp}",
                        f"    VMUL.F32 s{stmp}, s{stmp}, s{rdir}",
                        f"    VSUB.F32 s{resq}, s{resq}, s{stmp}",
                    ]

                elif op == '^':
                    stmp  = creg
                    lbl   = f"pow_{len(literais)}"
                    lbl1  = f"num_{len(literais)}"
                    literais.append((lbl1, "1.0"))
                    instrucoes += [
                        f"    VCVT.S32.F32 s{stmp}, s{rdir}",   # expoente int
                        f"    VMOV r1, s{stmp}",                  # r1 = contador loop
                        f"    LDR r2, ={lbl1}",
                        f"    VLDR s{stmp}, [r2]",                # acumulador = 1.0
                        f"{lbl}_loop:",
                        f"    CMP r1, #0",
                        f"    BLE {lbl}_end",
                        f"    VMUL.F32 s{stmp}, s{stmp}, s{resq}",
                        f"    SUB r1, r1, #1",
                        f"    B {lbl}_loop",
                        f"{lbl}_end:",
                        f"    VMOV.F32 s{resq}, s{stmp}",
                    ]

                creg -= 1   # resultado fica em resq, rdir liberado

            # -- MEM_STORE: (V MEM) se pilha tem valor, (MEM) se vazia --
            elif tok.tipo == TOKEN_MEM_STORE:
                var_label = "MEM_var"
                if var_label not in memorias:
                    memorias.append(var_label)

                if ultimo_foi_numero and creg >= 1:
                    # (V MEM): salva s(creg-1) em MEM, mantem na pilha
                    rtop = creg - 1
                    instrucoes += [
                        f"",
                        f"    @ (V MEM): salva s{rtop} em MEM_var",
                        f"    LDR r1, ={var_label}",
                        f"    VSTR s{rtop}, [r1]",
                    ]
                    # valor permanece na pilha como resultado da expressao
                else:
                    # (MEM): carrega MEM para o topo da pilha
                    instrucoes += [
                        f"",
                        f"    @ (MEM): carrega MEM_var -> s{creg}",
                        f"    LDR r1, ={var_label}",
                        f"    VLDR s{creg}, [r1]",
                    ]
                    creg += 1

                ultimo_foi_numero = False

            # -- MEM_LOAD: sempre carrega --
            elif tok.tipo == TOKEN_MEM_LOAD:
                var_label = "MEM_var"
                if var_label not in memorias:
                    memorias.append(var_label)
                instrucoes += [
                    f"",
                    f"    @ MEM_LOAD -> s{creg}",
                    f"    LDR r1, ={var_label}",
                    f"    VLDR s{creg}, [r1]",
                ]
                creg += 1
                ultimo_foi_numero = False

            # -- RES --
            elif tok.tipo == TOKEN_RES:
                _gerar_res(instrucoes, creg, linha_idx, literais)
                ultimo_foi_numero = False
                # creg nao muda: N foi substituido pelo valor buscado

        # -- Fim da linha: salva resultado em res_array e exibe nos LEDs --
        if creg > 0:
            instrucoes += [
                f"",
                f"    @ Salva resultado da linha {linha_idx} em res_array",
                f"    LDR r1, =res_array",
                f"    LDR r2, ={linha_idx}",
                f"    ADD r1, r1, r2, LSL #2",
                f"    VSTR s0, [r1]",
            ]
            _mostrar_resultado(instrucoes, 0)

        instrucoes.append("")

    # -- Epilogo --
    instrucoes += [
        "    @ Fim da execucao",
        "    BX LR",
        "",
    ]

    # -- Secao .data --
    instrucoes.append(".data")
    instrucoes.append("")

    for mem_lbl in memorias:
        instrucoes += [f"{mem_lbl}:", "    .float 0.0", ""]

    total_linhas = len(lista_tokens_por_linha)
    instrucoes += [
        "res_array:",
        f"    .space {total_linhas * 4}   @ {total_linhas} floats de 4 bytes",
        "",
    ]

    for label, val in literais:
        instrucoes += [f"{label}:", f"    .float {val}", ""]

    # -- Grava arquivo --
    os.makedirs(os.path.dirname(caminho_saida) if os.path.dirname(caminho_saida) else ".", exist_ok=True)
    with open(caminho_saida, "w", encoding="utf-8") as f:
        f.write("\n".join(instrucoes) + "\n")

    return caminho_saida

