"""Execução automática ou passo a passo, sem dependências externas."""

import argparse
import csv
from pathlib import Path

from cpu import CPU
from programas import PROGRAMAS


def mostrar_tabela(cpu):
    print("\nEVOLUÇÃO DOS REGISTRADORES (valores decimais após cada instrução)")
    print("Ciclo PC  Instrução       R0  R1  R2  R3  PC depois")
    for linha in cpu.historico:
        r = linha["depois"]
        print(f"{linha['ciclo']:5d} {linha['pc_antes']:02d}  "
              f"{linha['instrucao']:<15} {r['R0']:3d} {r['R1']:3d} "
              f"{r['R2']:3d} {r['R3']:3d}     {linha['pc_depois']:02d}")


def exportar_csv(cpu, caminho):
    with Path(caminho).open("w", encoding="utf-8-sig", newline="") as arquivo:
        escritor = csv.writer(arquivo, delimiter=";")
        escritor.writerow(["ciclo", "pc_antes", "instrucao", "R0", "R1", "R2", "R3", "pc_depois", "memoria_alterada", "halted"])
        for linha in cpu.historico:
            escritor.writerow([
                linha["ciclo"], linha["pc_antes"], linha["instrucao"],
                *linha["depois"].values(), linha["pc_depois"],
                str(linha["memoria_alterada"]), linha["halted"],
            ])


def main():
    parser = argparse.ArgumentParser(description="CPU simulada de 8 bits - AOC")
    parser.add_argument("--programa", choices=PROGRAMAS, default="proprio")
    parser.add_argument("--passo", action="store_true", help="aguarda Enter a cada instrução")
    parser.add_argument("--resumo", action="store_true", help="mostra somente tabela e resultado")
    parser.add_argument("--csv", help="salva a evolução em arquivo CSV")
    args = parser.parse_args()
    cpu = CPU()
    cpu.carregar_programa(PROGRAMAS[args.programa])
    print(f"CPU SIMULADA - 8 BITS | Programa: {args.programa}")
    try:
        cpu.executar(exibir=not args.resumo, passo_a_passo=args.passo)
    except (ValueError, RuntimeError) as erro:
        parser.exit(1, f"Erro na simulação: {erro}\n")
    mostrar_tabela(cpu)
    print(f"\nResultado: MEM[14] = {cpu.memoria[14]} | MEM[15] = {cpu.memoria[15]}")
    print(f"CPU encerrada: {cpu.halted} | Ciclos: {len(cpu.historico)}")
    if args.csv:
        exportar_csv(cpu, args.csv)


if __name__ == "__main__":
    main()
