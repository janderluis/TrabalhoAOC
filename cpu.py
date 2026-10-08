"""CPU didática baseada na estrutura fornecida em AOC 2026.2."""

from ula import ula, limitar_8bits


class CPU:
    def __init__(self):
        self.registradores = {"R0": 0, "R1": 0, "R2": 0, "R3": 0}
        # Instruções são strings; dados são inteiros de 8 bits.
        self.memoria = [0] * 16
        self.pc = 0
        self.halted = False
        self.historico = []

    def validar_endereco(self, endereco):
        if not 0 <= endereco < len(self.memoria):
            raise ValueError(f"Endereço inválido: {endereco}. Use 0 a 15.")

    def validar_registrador(self, nome):
        if nome not in self.registradores:
            raise ValueError(f"Registrador inválido: {nome}. Use R0 a R3.")

    def carregar_programa(self, programa):
        """Carrega instruções a partir do endereço zero em uma CPU nova."""
        programa = list(programa)
        if not programa or len(programa) > 16:
            raise ValueError("O programa precisa ter de 1 a 16 instruções.")
        if any(not isinstance(item, str) or not item.strip() for item in programa):
            raise ValueError("Cada instrução precisa ser um texto não vazio.")
        self.registradores = {"R0": 0, "R1": 0, "R2": 0, "R3": 0}
        self.memoria = [0] * 16
        self.memoria[:len(programa)] = programa
        self.pc = 0
        self.halted = False
        self.historico = []

    def decodificar(self, instrucao):
        """DECODE: separa operação e operandos e verifica a instrução."""
        if not isinstance(instrucao, str) or not instrucao.strip():
            raise ValueError(f"MEM[{self.pc}] não contém uma instrução válida.")
        partes = instrucao.replace(",", " ").upper().split()
        operacao, operandos = partes[0], partes[1:]
        quantidades = {
            "LOAD": 2, "STORE": 2, "ADD": 2, "SUB": 2,
            "AND": 2, "OR": 2, "XOR": 2, "JMP": 1, "HALT": 0,
        }
        if operacao not in quantidades:
            raise ValueError(f"Instrução desconhecida: {operacao}")
        if len(operandos) != quantidades[operacao]:
            raise ValueError(f"{operacao} exige {quantidades[operacao]} operando(s).")
        if operacao in ("LOAD", "STORE", "ADD", "SUB", "AND", "OR", "XOR"):
            self.validar_registrador(operandos[0])
        if operacao in ("ADD", "SUB", "AND", "OR", "XOR"):
            self.validar_registrador(operandos[1])
        if operacao in ("LOAD", "STORE"):
            operandos[1] = int(operandos[1])
        if operacao == "STORE":
            self.validar_endereco(operandos[1])
        if operacao == "JMP":
            operandos[0] = int(operandos[0])
            self.validar_endereco(operandos[0])
        return operacao, operandos

    def executar_instrucao(self, instrucao):
        """Decodifica e executa uma instrução, preservando a interface-base."""
        if self.halted:
            return
        operacao, operandos = self.decodificar(instrucao)

        if operacao == "LOAD":
            registrador, valor = operandos
            self.registradores[registrador] = limitar_8bits(valor)
            self.pc += 1
        elif operacao == "STORE":
            registrador, endereco = operandos
            self.memoria[endereco] = limitar_8bits(self.registradores[registrador])
            self.pc += 1
        elif operacao in ("ADD", "SUB", "AND", "OR", "XOR"):
            destino, origem = operandos
            # O primeiro registrador recebe o resultado; o segundo é lido.
            self.registradores[destino] = ula(
                operacao, self.registradores[destino], self.registradores[origem]
            )
            self.pc += 1
        elif operacao == "JMP":
            self.pc = operandos[0]
        elif operacao == "HALT":
            # Como no código-base, HALT mantém o PC na instrução de parada.
            self.halted = True

    def ciclo(self, exibir=True):
        """FETCH, DECODE e EXECUTE de uma instrução; registra antes/depois."""
        if self.halted:
            return None
        self.validar_endereco(self.pc)
        # FETCH: usa o PC para buscar a instrução na memória.
        pc_antes = self.pc
        instrucao = self.memoria[pc_antes]
        antes = self.registradores.copy()
        memoria_antes = self.memoria.copy()
        if exibir:
            print(f"\nFETCH | PC: {pc_antes:02d} | Instrução: {instrucao}")
            print("Antes: ", end="")
            self.mostrar_estado()
            print("DECODE + EXECUTE")
        self.executar_instrucao(instrucao)
        alteracoes = {
            i: self.memoria[i] for i in range(16)
            if self.memoria[i] != memoria_antes[i]
        }
        registro = {
            "ciclo": len(self.historico) + 1, "pc_antes": pc_antes,
            "instrucao": instrucao, "antes": antes,
            "depois": self.registradores.copy(), "pc_depois": self.pc,
            "memoria_alterada": alteracoes, "halted": self.halted,
        }
        self.historico.append(registro)
        if exibir:
            print("Depois: ", end="")
            self.mostrar_estado()
            for endereco, valor in alteracoes.items():
                print(f"MEM[{endereco}] = {valor}")
            print(f"PC depois: {self.pc:02d} | HALT: {self.halted}")
        return registro

    def executar(self, max_ciclos=100, exibir=True, passo_a_passo=False):
        """Executa até HALT; o limite identifica programas que não encerram."""
        if max_ciclos <= 0:
            raise ValueError("max_ciclos deve ser positivo.")
        ciclos = 0
        while not self.halted:
            if ciclos >= max_ciclos:
                raise RuntimeError("Número máximo de ciclos atingido. Verifique se existe um loop infinito.")
            if passo_a_passo:
                input("\nPressione Enter para executar a próxima instrução...")
            self.ciclo(exibir=exibir)
            ciclos += 1

    def mostrar_estado(self):
        print(" | ".join(
            f"{nome}={valor:3d} (0x{valor:02X})"
            for nome, valor in self.registradores.items()
        ))
