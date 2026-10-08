"""Programas da demonstração e da verificação da CPU."""

PROGRAMA_EXEMPLO = [
    "LOAD R0, 5", "LOAD R1, 8", "ADD R0, R1", "STORE R0, 15", "HALT",
]

# Programa próprio: 13 instruções na memória, 12 ciclos executados.
# O endereço 9 é pulado; os dados ficam nas posições livres 14 e 15.
PROGRAMA_PROPRIO = [
    "LOAD R0, 12",      # 00: R0 = 12
    "LOAD R1, 5",       # 01: R1 = 5
    "ADD R0, R1",       # 02: R0 = 17
    "LOAD R2, 3",       # 03: R2 = 3
    "SUB R0, R2",       # 04: R0 = 14
    "AND R0, R1",       # 05: 14 AND 5 = 4
    "OR R0, R2",        # 06: 4 OR 3 = 7
    "XOR R0, R1",       # 07: 7 XOR 5 = 2
    "JMP 10",           # 08: pula LOAD R0, 99
    "LOAD R0, 99",      # 09: não executada
    "STORE R0, 15",     # 10: MEM[15] = 2
    "STORE R1, 14",     # 11: MEM[14] = 5
    "HALT",             # 12: encerra
]

PROGRAMA_SALTO = [
    "LOAD R0, 5", "JMP 4", "LOAD R0, 99", "HALT", "LOAD R1, 8", "HALT",
]

PROGRAMA_8BITS = [
    "LOAD R0, 255", "LOAD R1, 1", "ADD R0, R1", "SUB R0, R1",
    "STORE R0, 15", "HALT",
]

PROGRAMAS = {
    "proprio": PROGRAMA_PROPRIO, "exemplo": PROGRAMA_EXEMPLO,
    "salto": PROGRAMA_SALTO, "8bits": PROGRAMA_8BITS,
}
