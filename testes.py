"""Testes automáticos da arquitetura, instruções e programas completos."""

import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from cpu import CPU
from programas import PROGRAMA_EXEMPLO, PROGRAMA_PROPRIO, PROGRAMA_8BITS
from ula import limitar_8bits, ula


class TestesULA(unittest.TestCase):
    def test_limitar_8bits(self):
        for entrada, esperado in [(0, 0), (255, 255), (256, 0), (300, 44), (-1, 255)]:
            with self.subTest(entrada=entrada):
                self.assertEqual(limitar_8bits(entrada), esperado)

    def test_add(self):
        self.assertEqual(ula("ADD", 5, 8), 13)

    def test_add_overflow(self):
        self.assertEqual(ula("ADD", 255, 1), 0)
        self.assertEqual(ula("ADD", 200, 100), 44)

    def test_sub(self):
        self.assertEqual(ula("SUB", 17, 3), 14)

    def test_sub_abaixo_de_zero(self):
        self.assertEqual(ula("SUB", 0, 1), 255)

    def test_and(self):
        self.assertEqual(ula("AND", 14, 5), 4)
        self.assertEqual(ula("AND", 255, 0), 0)

    def test_or(self):
        self.assertEqual(ula("OR", 4, 3), 7)
        self.assertEqual(ula("OR", 0, 255), 255)

    def test_xor(self):
        self.assertEqual(ula("XOR", 7, 5), 2)
        self.assertEqual(ula("XOR", 255, 255), 0)

    def test_operandos_limitados(self):
        self.assertEqual(ula("ADD", 256, 257), 1)

    def test_operacao_invalida(self):
        with self.assertRaises(ValueError):
            ula("MUL", 3, 2)


class TestesCPU(unittest.TestCase):
    def executar_programa(self, programa):
        cpu = CPU()
        cpu.carregar_programa(programa)
        cpu.executar(exibir=False)
        return cpu

    def test_estado_inicial(self):
        cpu = CPU()
        self.assertEqual(cpu.registradores, {"R0": 0, "R1": 0, "R2": 0, "R3": 0})
        self.assertEqual(cpu.memoria, [0] * 16)
        self.assertEqual(cpu.pc, 0)
        self.assertFalse(cpu.halted)

    def test_load_quatro_registradores(self):
        cpu = self.executar_programa([
            "LOAD R0, 25", "LOAD R1, 40", "LOAD R2, 60", "LOAD R3, 255", "HALT",
        ])
        self.assertEqual(list(cpu.registradores.values()), [25, 40, 60, 255])

    def test_load_8bits(self):
        cpu = self.executar_programa(["LOAD R0, 300", "LOAD R1, -1", "HALT"])
        self.assertEqual(cpu.registradores["R0"], 44)
        self.assertEqual(cpu.registradores["R1"], 255)

    def test_store(self):
        cpu = self.executar_programa(["LOAD R3, 42", "STORE R3, 15", "HALT"])
        self.assertEqual(cpu.memoria[15], 42)
        self.assertEqual(cpu.registradores["R3"], 42)

    def test_store_limites_memoria(self):
        cpu = CPU()
        cpu.executar_instrucao("LOAD R0, 23")
        cpu.executar_instrucao("STORE R0, 0")
        cpu.executar_instrucao("STORE R0, 15")
        self.assertEqual(cpu.memoria[0], 23)
        self.assertEqual(cpu.memoria[15], 23)

    def test_operacoes_integradas(self):
        # Resultados independentes, conferidos também em exemplos binários.
        for operacao, a, b, esperado in [
            ("ADD", 5, 8, 13), ("SUB", 17, 3, 14),
            ("AND", 14, 5, 4), ("OR", 4, 3, 7), ("XOR", 7, 5, 2),
        ]:
            with self.subTest(operacao=operacao):
                cpu = self.executar_programa([
                    f"LOAD R0, {a}", f"LOAD R1, {b}", f"{operacao} R0, R1", "HALT",
                ])
                self.assertEqual(cpu.registradores["R0"], esperado)
                self.assertEqual(cpu.registradores["R1"], b)
                self.assertEqual(cpu.pc, 3)

    def test_operacao_mesmo_registrador(self):
        cpu = self.executar_programa(["LOAD R0, 7", "ADD R0, R0", "XOR R0, R0", "HALT"])
        self.assertEqual(cpu.historico[1]["depois"]["R0"], 14)
        self.assertEqual(cpu.registradores["R0"], 0)

    def test_pc_avanca(self):
        cpu = CPU()
        cpu.carregar_programa(["LOAD R0, 1", "STORE R0, 15", "ADD R0, R0", "HALT"])
        for esperado in [1, 2, 3]:
            cpu.ciclo(exibir=False)
            self.assertEqual(cpu.pc, esperado)

    def test_jmp_pula_instrucao(self):
        cpu = self.executar_programa([
            "LOAD R0, 10", "JMP 4", "LOAD R0, 99", "HALT", "LOAD R1, 20", "HALT",
        ])
        self.assertEqual(cpu.registradores["R0"], 10)
        self.assertEqual(cpu.registradores["R1"], 20)
        self.assertEqual([h["pc_antes"] for h in cpu.historico], [0, 1, 4, 5])

    def test_jmp_para_15(self):
        cpu = CPU()
        cpu.memoria[0], cpu.memoria[15] = "JMP 15", "HALT"
        cpu.executar(exibir=False)
        self.assertEqual(cpu.pc, 15)
        self.assertTrue(cpu.halted)

    def test_halt_interrompe(self):
        cpu = self.executar_programa(["HALT", "LOAD R0, 99"])
        self.assertTrue(cpu.halted)
        self.assertEqual(cpu.pc, 0)
        self.assertEqual(cpu.registradores["R0"], 0)
        self.assertIsNone(cpu.ciclo(exibir=False))
        cpu.executar_instrucao("LOAD R0, 99")
        self.assertEqual(cpu.registradores["R0"], 0)
        self.assertEqual(len(cpu.historico), 1)

    def test_programa_exemplo(self):
        cpu = self.executar_programa(PROGRAMA_EXEMPLO)
        self.assertEqual(cpu.memoria[15], 13)
        self.assertEqual(len(cpu.historico), 5)

    def test_programa_proprio_e_evolucao(self):
        cpu = self.executar_programa(PROGRAMA_PROPRIO)
        self.assertEqual(cpu.registradores, {"R0": 2, "R1": 5, "R2": 3, "R3": 0})
        self.assertEqual((cpu.memoria[14], cpu.memoria[15], cpu.pc), (5, 2, 12))
        self.assertEqual([h["pc_antes"] for h in cpu.historico], [0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12])
        self.assertEqual([h["depois"]["R0"] for h in cpu.historico], [12, 12, 17, 17, 14, 4, 7, 2, 2, 2, 2, 2])
        self.assertTrue(cpu.halted)

    def test_programa_8bits(self):
        cpu = self.executar_programa(PROGRAMA_8BITS)
        self.assertEqual(cpu.historico[2]["depois"]["R0"], 0)
        self.assertEqual(cpu.historico[3]["depois"]["R0"], 255)
        self.assertEqual(cpu.memoria[15], 255)

    def test_valores_sempre_8bits(self):
        cpu = self.executar_programa(PROGRAMA_8BITS)
        for linha in cpu.historico:
            self.assertTrue(all(0 <= v <= 255 for v in linha["depois"].values()))

    def test_historico_independente(self):
        cpu = self.executar_programa(["LOAD R0, 1", "LOAD R0, 2", "HALT"])
        self.assertEqual(cpu.historico[0]["antes"]["R0"], 0)
        self.assertEqual(cpu.historico[0]["depois"]["R0"], 1)
        self.assertEqual(cpu.historico[1]["depois"]["R0"], 2)

    def test_carregar_reinicia_cpu(self):
        cpu = self.executar_programa(PROGRAMA_EXEMPLO)
        cpu.carregar_programa(["HALT"])
        self.assertEqual(cpu.registradores["R0"], 0)
        self.assertEqual(cpu.memoria[15], 0)
        self.assertEqual(cpu.pc, 0)
        self.assertFalse(cpu.halted)
        self.assertEqual(cpu.historico, [])

    def test_programa_tamanho_invalido(self):
        for programa in [[], ["HALT"] * 17, [0], [""]]:
            with self.subTest(programa=programa), self.assertRaises(ValueError):
                CPU().carregar_programa(programa)

    def test_instrucao_invalida_sem_alterar_estado(self):
        for instrucao in ["", 0, "MUL R0, R1", "LOAD R4, 1", "ADD R0, R4", "LOAD R0", "HALT 1", "LOAD R0, abc"]:
            cpu = CPU()
            with self.subTest(instrucao=instrucao), self.assertRaises(ValueError):
                cpu.executar_instrucao(instrucao)
            self.assertEqual(cpu.pc, 0)
            self.assertEqual(cpu.registradores, {"R0": 0, "R1": 0, "R2": 0, "R3": 0})

    def test_enderecos_invalidos(self):
        for instrucao in ["STORE R0, -1", "STORE R0, 16", "JMP -1", "JMP 16"]:
            cpu = CPU()
            with self.subTest(instrucao=instrucao), self.assertRaises(ValueError):
                cpu.executar_instrucao(instrucao)
            self.assertEqual(cpu.pc, 0)

    def test_fetch_pc_invalido(self):
        for endereco in [-1, 16]:
            cpu = CPU()
            cpu.pc = endereco
            with self.subTest(endereco=endereco), self.assertRaises(ValueError):
                cpu.ciclo(exibir=False)

    def test_fetch_dado_nao_e_instrucao(self):
        with self.assertRaises(ValueError):
            CPU().ciclo(exibir=False)

    def test_limite_ciclos(self):
        cpu = CPU()
        cpu.carregar_programa(["JMP 0"])
        with self.assertRaises(RuntimeError):
            cpu.executar(max_ciclos=3, exibir=False)
        self.assertEqual(len(cpu.historico), 3)

    def test_limite_ciclos_invalido(self):
        with self.assertRaises(ValueError):
            CPU().executar(max_ciclos=0, exibir=False)

    def test_saida_do_ciclo(self):
        cpu = CPU()
        cpu.carregar_programa(["LOAD R0, 5", "HALT"])
        saida = io.StringIO()
        with redirect_stdout(saida):
            cpu.ciclo()
        for trecho in ["PC: 00", "LOAD R0, 5", "Antes:", "Depois:", "R0=  5", "PC depois: 01"]:
            self.assertIn(trecho, saida.getvalue())

    def test_modo_passo_a_passo(self):
        cpu = CPU()
        cpu.carregar_programa(["LOAD R0, 5", "HALT"])
        with patch("builtins.input", return_value="") as entrada:
            cpu.executar(exibir=False, passo_a_passo=True)
        self.assertEqual(entrada.call_count, 2)
        self.assertTrue(cpu.halted)


if __name__ == "__main__":
    unittest.main(verbosity=2)
