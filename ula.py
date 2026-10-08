"""Operações da Unidade Lógica e Aritmética de 8 bits."""


def limitar_8bits(valor):
    """Mantém os oito bits menos significativos: valores de 0 a 255."""
    return valor & 0xFF


def ula(operacao, a, b=0):
    """Calcula uma operação e aplica a representação de 8 bits."""
    a = limitar_8bits(a)
    b = limitar_8bits(b)

    if operacao == "ADD":
        resultado = a + b
    elif operacao == "SUB":
        resultado = a - b
    elif operacao == "AND":
        resultado = a & b
    elif operacao == "OR":
        resultado = a | b
    elif operacao == "XOR":
        resultado = a ^ b
    else:
        raise ValueError(f"Operação inválida: {operacao}")

    return limitar_8bits(resultado)
