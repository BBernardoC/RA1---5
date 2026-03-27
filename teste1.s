.syntax unified
.arch armv7-a
.fpu vfp
.text
.global main
main:

    @ Habilitar VFP
    MRC p15, 0, r0, c1, c0, 2
    ORR r0, r0, #0xF00000
    MCR p15, 0, r0, c1, c0, 2
    ISB
    MOV r0, #0x40000000
    VMSR FPEXC, r0

    @ ---- linha 0 ----

    @ Carrega 3.0 -> s0
    LDR r0, =num_0
    VLDR s0, [r0]

    @ Carrega 2.0 -> s1
    LDR r0, =num_1
    VLDR s1, [r0]

    @ Operacao +: s0 + s1 -> s0
    VADD.F32 s0, s0, s1

    @ Carrega 4.0 -> s1
    LDR r0, =num_2
    VLDR s1, [r0]

    @ Operacao *: s0 * s1 -> s0
    VMUL.F32 s0, s0, s1

    @ Salva resultado da linha 0 em res_array
    LDR r1, =res_array
    LDR r2, =0
    ADD r1, r1, r2, LSL #2
    VSTR s0, [r1]

    @ Exibe resultado de s0 nos LEDs
    PUSH {r4, r5}         @ salva r4/r5 (callee-saved AAPCS)
    VCVT.F64.F32 d0, s0
    VMOV r4, r5, d0
    LDR r1, =0xFF200000
    STR r5, [r1]          @ MSB (parte alta)
    MOV r0, #0
    STR r0, [r1]          @ apaga
    STR r4, [r1]          @ LSB (parte baixa)
    MOV r0, #0
    STR r0, [r1]          @ apaga
    POP {r4, r5}          @ restaura r4/r5

    @ ---- linha 1 ----

    @ Carrega 10.0 -> s0
    LDR r0, =num_3
    VLDR s0, [r0]

    @ Carrega 2.0 -> s1
    LDR r0, =num_4
    VLDR s1, [r0]

    @ Operacao /: s0 / s1 -> s0
    VDIV.F32 s0, s0, s1

    @ Carrega 3.0 -> s1
    LDR r0, =num_5
    VLDR s1, [r0]

    @ Operacao -: s0 - s1 -> s0
    VSUB.F32 s0, s0, s1

    @ Salva resultado da linha 1 em res_array
    LDR r1, =res_array
    LDR r2, =1
    ADD r1, r1, r2, LSL #2
    VSTR s0, [r1]

    @ Exibe resultado de s0 nos LEDs
    PUSH {r4, r5}         @ salva r4/r5 (callee-saved AAPCS)
    VCVT.F64.F32 d0, s0
    VMOV r4, r5, d0
    LDR r1, =0xFF200000
    STR r5, [r1]          @ MSB (parte alta)
    MOV r0, #0
    STR r0, [r1]          @ apaga
    STR r4, [r1]          @ LSB (parte baixa)
    MOV r0, #0
    STR r0, [r1]          @ apaga
    POP {r4, r5}          @ restaura r4/r5

    @ ---- linha 2 ----

    @ Carrega 2.0 -> s0
    LDR r0, =num_6
    VLDR s0, [r0]

    @ Carrega 3.0 -> s1
    LDR r0, =num_7
    VLDR s1, [r0]

    @ Operacao ^: s0 ^ s1 -> s0
    VCVT.S32.F32 s2, s1
    VMOV r1, s2
    LDR r2, =num_8
    VLDR s2, [r2]
pow_8_loop:
    CMP r1, #0
    BLE pow_8_end
    VMUL.F32 s2, s2, s0
    SUB r1, r1, #1
    B pow_8_loop
pow_8_end:
    VMOV.F32 s0, s2

    @ Carrega 5.0 -> s1
    LDR r0, =num_9
    VLDR s1, [r0]

    @ Operacao +: s0 + s1 -> s0
    VADD.F32 s0, s0, s1

    @ Salva resultado da linha 2 em res_array
    LDR r1, =res_array
    LDR r2, =2
    ADD r1, r1, r2, LSL #2
    VSTR s0, [r1]

    @ Exibe resultado de s0 nos LEDs
    PUSH {r4, r5}         @ salva r4/r5 (callee-saved AAPCS)
    VCVT.F64.F32 d0, s0
    VMOV r4, r5, d0
    LDR r1, =0xFF200000
    STR r5, [r1]          @ MSB (parte alta)
    MOV r0, #0
    STR r0, [r1]          @ apaga
    STR r4, [r1]          @ LSB (parte baixa)
    MOV r0, #0
    STR r0, [r1]          @ apaga
    POP {r4, r5}          @ restaura r4/r5

    @ ---- linha 3 ----

    @ Carrega 9.0 -> s0
    LDR r0, =num_10
    VLDR s0, [r0]

    @ Carrega 4.0 -> s1
    LDR r0, =num_11
    VLDR s1, [r0]

    @ Operacao -: s0 - s1 -> s0
    VSUB.F32 s0, s0, s1

    @ Carrega 3.0 -> s1
    LDR r0, =num_12
    VLDR s1, [r0]

    @ Operacao %: s0 % s1 -> s0
    VDIV.F32 s2, s0, s1
    VCVT.S32.F32 s2, s2
    VCVT.F32.S32 s2, s2
    VMUL.F32 s2, s2, s1
    VSUB.F32 s0, s0, s2

    @ Salva resultado da linha 3 em res_array
    LDR r1, =res_array
    LDR r2, =3
    ADD r1, r1, r2, LSL #2
    VSTR s0, [r1]

    @ Exibe resultado de s0 nos LEDs
    PUSH {r4, r5}         @ salva r4/r5 (callee-saved AAPCS)
    VCVT.F64.F32 d0, s0
    VMOV r4, r5, d0
    LDR r1, =0xFF200000
    STR r5, [r1]          @ MSB (parte alta)
    MOV r0, #0
    STR r0, [r1]          @ apaga
    STR r4, [r1]          @ LSB (parte baixa)
    MOV r0, #0
    STR r0, [r1]          @ apaga
    POP {r4, r5}          @ restaura r4/r5

    @ ---- linha 4 ----

    @ Carrega 4.0 -> s0
    LDR r0, =num_13
    VLDR s0, [r0]

    @ Carrega 5.0 -> s1
    LDR r0, =num_14
    VLDR s1, [r0]

    @ Operacao *: s0 * s1 -> s0
    VMUL.F32 s0, s0, s1

    @ Carrega 2.0 -> s1
    LDR r0, =num_15
    VLDR s1, [r0]

    @ Carrega 3.0 -> s2
    LDR r0, =num_16
    VLDR s2, [r0]

    @ Operacao +: s1 + s2 -> s1
    VADD.F32 s1, s1, s2

    @ Operacao /: s0 / s1 -> s0
    VDIV.F32 s0, s0, s1

    @ Salva resultado da linha 4 em res_array
    LDR r1, =res_array
    LDR r2, =4
    ADD r1, r1, r2, LSL #2
    VSTR s0, [r1]

    @ Exibe resultado de s0 nos LEDs
    PUSH {r4, r5}         @ salva r4/r5 (callee-saved AAPCS)
    VCVT.F64.F32 d0, s0
    VMOV r4, r5, d0
    LDR r1, =0xFF200000
    STR r5, [r1]          @ MSB (parte alta)
    MOV r0, #0
    STR r0, [r1]          @ apaga
    STR r4, [r1]          @ LSB (parte baixa)
    MOV r0, #0
    STR r0, [r1]          @ apaga
    POP {r4, r5}          @ restaura r4/r5

    @ ---- linha 5 ----

    @ Carrega 3.0 -> s0
    LDR r0, =num_17
    VLDR s0, [r0]

    @ Carrega 4.0 -> s1
    LDR r0, =num_18
    VLDR s1, [r0]

    @ Operacao +: s0 + s1 -> s0
    VADD.F32 s0, s0, s1

    @ Carrega 2.0 -> s1
    LDR r0, =num_19
    VLDR s1, [r0]

    @ Carrega 1.0 -> s2
    LDR r0, =num_20
    VLDR s2, [r0]

    @ Operacao -: s1 - s2 -> s1
    VSUB.F32 s1, s1, s2

    @ Operacao ^: s0 ^ s1 -> s0
    VCVT.S32.F32 s2, s1
    VMOV r1, s2
    LDR r2, =num_21
    VLDR s2, [r2]
pow_21_loop:
    CMP r1, #0
    BLE pow_21_end
    VMUL.F32 s2, s2, s0
    SUB r1, r1, #1
    B pow_21_loop
pow_21_end:
    VMOV.F32 s0, s2

    @ Salva resultado da linha 5 em res_array
    LDR r1, =res_array
    LDR r2, =5
    ADD r1, r1, r2, LSL #2
    VSTR s0, [r1]

    @ Exibe resultado de s0 nos LEDs
    PUSH {r4, r5}         @ salva r4/r5 (callee-saved AAPCS)
    VCVT.F64.F32 d0, s0
    VMOV r4, r5, d0
    LDR r1, =0xFF200000
    STR r5, [r1]          @ MSB (parte alta)
    MOV r0, #0
    STR r0, [r1]          @ apaga
    STR r4, [r1]          @ LSB (parte baixa)
    MOV r0, #0
    STR r0, [r1]          @ apaga
    POP {r4, r5}          @ restaura r4/r5

    @ ---- linha 6 ----

    @ Carrega 50.0 -> s0
    LDR r0, =num_22
    VLDR s0, [r0]

    @ (V MEM): salva s0 em MEM_var
    LDR r1, =MEM_var
    VSTR s0, [r1]

    @ Salva resultado da linha 6 em res_array
    LDR r1, =res_array
    LDR r2, =6
    ADD r1, r1, r2, LSL #2
    VSTR s0, [r1]

    @ Exibe resultado de s0 nos LEDs
    PUSH {r4, r5}         @ salva r4/r5 (callee-saved AAPCS)
    VCVT.F64.F32 d0, s0
    VMOV r4, r5, d0
    LDR r1, =0xFF200000
    STR r5, [r1]          @ MSB (parte alta)
    MOV r0, #0
    STR r0, [r1]          @ apaga
    STR r4, [r1]          @ LSB (parte baixa)
    MOV r0, #0
    STR r0, [r1]          @ apaga
    POP {r4, r5}          @ restaura r4/r5

    @ ---- linha 7 ----

    @ (MEM): carrega MEM_var -> s0
    LDR r1, =MEM_var
    VLDR s0, [r1]

    @ Carrega 1 -> s1
    LDR r0, =num_23
    VLDR s1, [r0]

    @ (N RES) - busca resultado N posicoes atras
    VCVT.S32.F32 s1, s1
    VMOV r1, s1
    LDR r2, =7
    SUB r1, r2, r1
    CMP r1, #0
    BGE res_ok_7_2
    @ indice invalido -> empilha 0.0
    LDR r2, =num_24
    VLDR s1, [r2]
    B res_end_7_2
res_ok_7_2:
    LDR r2, =res_array
    ADD r2, r2, r1, LSL #2
    VLDR s1, [r2]
res_end_7_2:

    @ Operacao +: s0 + s1 -> s0
    VADD.F32 s0, s0, s1

    @ Salva resultado da linha 7 em res_array
    LDR r1, =res_array
    LDR r2, =7
    ADD r1, r1, r2, LSL #2
    VSTR s0, [r1]

    @ Exibe resultado de s0 nos LEDs
    PUSH {r4, r5}         @ salva r4/r5 (callee-saved AAPCS)
    VCVT.F64.F32 d0, s0
    VMOV r4, r5, d0
    LDR r1, =0xFF200000
    STR r5, [r1]          @ MSB (parte alta)
    MOV r0, #0
    STR r0, [r1]          @ apaga
    STR r4, [r1]          @ LSB (parte baixa)
    MOV r0, #0
    STR r0, [r1]          @ apaga
    POP {r4, r5}          @ restaura r4/r5

    @ ---- linha 8 ----

    @ Carrega 3.0 -> s0
    LDR r0, =num_25
    VLDR s0, [r0]

    @ Carrega 2.0 -> s1
    LDR r0, =num_26
    VLDR s1, [r0]

    @ Operacao +: s0 + s1 -> s0
    VADD.F32 s0, s0, s1

    @ Carrega 1 -> s1
    LDR r0, =num_27
    VLDR s1, [r0]

    @ (N RES) - busca resultado N posicoes atras
    VCVT.S32.F32 s1, s1
    VMOV r1, s1
    LDR r2, =8
    SUB r1, r2, r1
    CMP r1, #0
    BGE res_ok_8_2
    @ indice invalido -> empilha 0.0
    LDR r2, =num_28
    VLDR s1, [r2]
    B res_end_8_2
res_ok_8_2:
    LDR r2, =res_array
    ADD r2, r2, r1, LSL #2
    VLDR s1, [r2]
res_end_8_2:

    @ Operacao *: s0 * s1 -> s0
    VMUL.F32 s0, s0, s1

    @ Salva resultado da linha 8 em res_array
    LDR r1, =res_array
    LDR r2, =8
    ADD r1, r1, r2, LSL #2
    VSTR s0, [r1]

    @ Exibe resultado de s0 nos LEDs
    PUSH {r4, r5}         @ salva r4/r5 (callee-saved AAPCS)
    VCVT.F64.F32 d0, s0
    VMOV r4, r5, d0
    LDR r1, =0xFF200000
    STR r5, [r1]          @ MSB (parte alta)
    MOV r0, #0
    STR r0, [r1]          @ apaga
    STR r4, [r1]          @ LSB (parte baixa)
    MOV r0, #0
    STR r0, [r1]          @ apaga
    POP {r4, r5}          @ restaura r4/r5

    @ ---- linha 9 ----

    @ (MEM): carrega MEM_var -> s0
    LDR r1, =MEM_var
    VLDR s0, [r1]

    @ Carrega 2 -> s1
    LDR r0, =num_29
    VLDR s1, [r0]

    @ (N RES) - busca resultado N posicoes atras
    VCVT.S32.F32 s1, s1
    VMOV r1, s1
    LDR r2, =9
    SUB r1, r2, r1
    CMP r1, #0
    BGE res_ok_9_2
    @ indice invalido -> empilha 0.0
    LDR r2, =num_30
    VLDR s1, [r2]
    B res_end_9_2
res_ok_9_2:
    LDR r2, =res_array
    ADD r2, r2, r1, LSL #2
    VLDR s1, [r2]
res_end_9_2:

    @ Operacao %: s0 % s1 -> s0
    VDIV.F32 s2, s0, s1
    VCVT.S32.F32 s2, s2
    VCVT.F32.S32 s2, s2
    VMUL.F32 s2, s2, s1
    VSUB.F32 s0, s0, s2

    @ Salva resultado da linha 9 em res_array
    LDR r1, =res_array
    LDR r2, =9
    ADD r1, r1, r2, LSL #2
    VSTR s0, [r1]

    @ Exibe resultado de s0 nos LEDs
    PUSH {r4, r5}         @ salva r4/r5 (callee-saved AAPCS)
    VCVT.F64.F32 d0, s0
    VMOV r4, r5, d0
    LDR r1, =0xFF200000
    STR r5, [r1]          @ MSB (parte alta)
    MOV r0, #0
    STR r0, [r1]          @ apaga
    STR r4, [r1]          @ LSB (parte baixa)
    MOV r0, #0
    STR r0, [r1]          @ apaga
    POP {r4, r5}          @ restaura r4/r5

    @ Fim da execucao
    BX LR

.data

MEM_var:
    .float 0.0

res_array:
    .space 40   @ 10 floats de 4 bytes

num_0:
    .float 3.0

num_1:
    .float 2.0

num_2:
    .float 4.0

num_3:
    .float 10.0

num_4:
    .float 2.0

num_5:
    .float 3.0

num_6:
    .float 2.0

num_7:
    .float 3.0

num_8:
    .float 1.0

num_9:
    .float 5.0

num_10:
    .float 9.0

num_11:
    .float 4.0

num_12:
    .float 3.0

num_13:
    .float 4.0

num_14:
    .float 5.0

num_15:
    .float 2.0

num_16:
    .float 3.0

num_17:
    .float 3.0

num_18:
    .float 4.0

num_19:
    .float 2.0

num_20:
    .float 1.0

num_21:
    .float 1.0

num_22:
    .float 50.0

num_23:
    .float 1

num_24:
    .float 0.0

num_25:
    .float 3.0

num_26:
    .float 2.0

num_27:
    .float 1

num_28:
    .float 0.0

num_29:
    .float 2

num_30:
    .float 0.0

