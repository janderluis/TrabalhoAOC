# CPU simulada de 8 bits

Trabalho de Arquitetura de Computadores, UFC Sobral, 2026.2.

**Integrantes:** Jander Luis Magalhães Coutinho e Arthur Fernandes Viana.

Implementação baseada no código-base fornecido pelo professor Wendley S. Silva.

Repositório: https://github.com/janderluis/TrabalhoAOC

Material de apoio: [guia simplificado](docs/Guia_CPU_Simulada.pdf).

## Execução

É necessário Python 3. Não há bibliotecas externas para executar a CPU ou os testes.
Abra o terminal nesta pasta. No Windows, se `python` não estiver disponível, substitua por `py`.

```bash
python main.py
python main.py --passo
python main.py --resumo
python testes.py
```

`--passo` aguarda Enter antes de cada instrução. A saída mostra PC, instrução, registradores antes/depois, alterações de memória e o PC seguinte. Os valores são exibidos em decimal e hexadecimal; `0x0E` equivale a 14 decimal.

Outras demonstrações:

```bash
python main.py --programa exemplo --resumo
python main.py --programa salto --resumo
python main.py --programa 8bits --resumo
python main.py --resumo --csv evolucao.csv
```

## Arquitetura

| Componente | Representação |
| --- | --- |
| Dados | Inteiros sem sinal de 8 bits, de 0 a 255 |
| Registradores | Dicionário com R0, R1, R2 e R3 |
| Memória | Lista com 16 posições, endereços de 0 a 15 |
| PC | Índice da próxima instrução |
| ULA | ADD, SUB, AND, OR e XOR |
| Controle | Métodos da classe CPU que buscam, decodificam e executam |
| Encerramento | `halted = True` após HALT |

As instruções são strings, por exemplo `"ADD R0, R1"`. Os dados são inteiros. Código e dados compartilham a mesma lista, conforme a representação didática permitida no enunciado. Uma string de instrução não é codificada em um byte real; a regra de 8 bits aplica-se aos valores numéricos.

`LOAD` carrega um **valor imediato**. Em `LOAD R0, 5`, 5 é o próprio valor, não o endereço de memória. Essa escolha segue o conjunto mínimo de instruções e o código-base do professor. O texto geral do enunciado menciona transferências entre memória e registradores, mas não define uma instrução de leitura de dados por endereço.

O PC normalmente avança em uma posição. `JMP` substitui o PC pelo endereço de destino. `HALT` interrompe a execução e mantém o PC na instrução de parada, como no código-base. Depois de `HALT`, novas chamadas de ciclo não executam instruções.

## Conjunto de instruções

| Instrução | Efeito |
| --- | --- |
| `LOAD R0, 5` | R0 recebe 5, limitado a 8 bits |
| `STORE R0, 15` | MEM[15] recebe o valor de R0 |
| `ADD R0, R1` | R0 recebe R0 + R1 |
| `SUB R0, R1` | R0 recebe R0 - R1 |
| `AND R0, R1` | R0 recebe o AND bit a bit |
| `OR R0, R1` | R0 recebe o OR bit a bit |
| `XOR R0, R1` | R0 recebe o XOR bit a bit |
| `JMP 10` | PC recebe 10 |
| `HALT` | Encerra a execução |

Nas operações com dois registradores, o primeiro recebe o resultado. O segundo é apenas lido, exceto quando ambos os operandos indicam o mesmo registrador.

## Ciclo Fetch / Decode / Execute

1. **Fetch:** `ciclo()` lê `memoria[pc]`.
2. **Decode:** `decodificar()` separa operação e operandos, verifica os registradores e endereços.
3. **Execute:** `executar_instrucao()` faz a transferência, chama a ULA, modifica o PC ou encerra.

Cada ciclo salva uma cópia dos registradores antes e depois, o PC antes e depois e as posições de memória que mudaram. Esse histórico produz a tabela final.

## Representação de 8 bits

A função `limitar_8bits(valor)` aplica `valor & 0xFF`, preservando os oito bits menos significativos. Para inteiros, o efeito equivale ao resto da divisão por 256.

- 5 + 8 = 13.
- 255 + 1 = 256; em 8 bits, o resultado armazenado é 0.
- 0 - 1 = -1; o padrão de 8 bits é `11111111`, exibido como 255 sem sinal.

Não há flags de carry, overflow ou sinal nesta arquitetura.

## Programa próprio

O programa transforma o valor inicial 12 por operações aritméticas e lógicas, grava o resultado na posição 15 e salva o valor de R1 na posição 14. Inclui as cinco operações da ULA, LOAD, STORE, JMP e HALT.

```text
00: LOAD R0, 12
01: LOAD R1, 5
02: ADD R0, R1
03: LOAD R2, 3
04: SUB R0, R2
05: AND R0, R1
06: OR R0, R2
07: XOR R0, R1
08: JMP 10
09: LOAD R0, 99
10: STORE R0, 15
11: STORE R1, 14
12: HALT
```

Há 13 instruções armazenadas e 12 efetivamente executadas. O salto pula o endereço 9. As posições 14 e 15 estão livres para dados; STORE não sobrescreve as instruções desse programa.

### Evolução esperada e verificada pelos testes

Todos os valores desta tabela são decimais e correspondem ao estado **depois** da instrução.

| Ciclo | PC antes | Instrução | R0 | R1 | R2 | R3 | PC depois |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 0 | LOAD R0, 12 | 12 | 0 | 0 | 0 | 1 |
| 2 | 1 | LOAD R1, 5 | 12 | 5 | 0 | 0 | 2 |
| 3 | 2 | ADD R0, R1 | 17 | 5 | 0 | 0 | 3 |
| 4 | 3 | LOAD R2, 3 | 17 | 5 | 3 | 0 | 4 |
| 5 | 4 | SUB R0, R2 | 14 | 5 | 3 | 0 | 5 |
| 6 | 5 | AND R0, R1 | 4 | 5 | 3 | 0 | 6 |
| 7 | 6 | OR R0, R2 | 7 | 5 | 3 | 0 | 7 |
| 8 | 7 | XOR R0, R1 | 2 | 5 | 3 | 0 | 8 |
| 9 | 8 | JMP 10 | 2 | 5 | 3 | 0 | 10 |
| 10 | 10 | STORE R0, 15 | 2 | 5 | 3 | 0 | 11 |
| 11 | 11 | STORE R1, 14 | 2 | 5 | 3 | 0 | 12 |
| 12 | 12 | HALT | 2 | 5 | 3 | 0 | 12 |

Resultado final: **MEM[15] = 2; MEM[14] = 5; PC = 12; CPU encerrada.**

Exemplos das operações lógicas em 8 bits:

```text
AND: 00001110 (14) AND 00000101 (5) = 00000100 (4)
 OR: 00000100 ( 4)  OR 00000011 (3) = 00000111 (7)
XOR: 00000111 ( 7) XOR 00000101 (5) = 00000010 (2)
```

## Testes

`testes.py` usa `unittest`, da biblioteca padrão. Verifica as cinco operações da ULA, LOAD, STORE, avanço do PC, salto, parada, exemplo do enunciado, programa próprio e limites de 8 bits. Também cobre registradores e endereços inválidos, limite de ciclos e execução passo a passo.

Resultado da execução local em Python 3.14: **36 testes aprovados**.

O exemplo do enunciado produz **MEM[15] = 13**. O programa `8bits` demonstra a volta para zero em 255 + 1 e para 255 em 0 - 1.

## Arquivos

- `cpu.py`: registradores, memória, PC e ciclo de execução.
- `ula.py`: operações aritméticas/lógicas e limitação de 8 bits.
- `programas.py`: programa próprio e exemplos.
- `main.py`: terminal, passo a passo, tabela e exportação CSV.
- `testes.py`: testes automáticos.

## Limites do modelo

É uma simulação didática. Não há clock físico, pipeline, interrupções, entrada/saída ou instruções binárias reais. Saltar para uma posição que contém um dado gera erro. Um programa sem HALT é interrompido pelo limite de ciclos, não por uma instrução de parada.
