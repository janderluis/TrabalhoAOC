# CPU simulada de 8 bits

Projeto da disciplina de Arquitetura de Computadores da UFC Sobral, semestre 2026.2.

**Integrantes:** Jander Luis Magalhães Coutinho e Arthur Fernandes Viana.

O projeto usa o código-base fornecido pelo professor Wendley S. Silva.

Repositório: https://github.com/janderluis/TrabalhoAOC

## Execução

Para executar a CPU e os testes, basta ter o Python 3 instalado. Não é preciso instalar bibliotecas externas.
Abra o terminal nesta pasta. No Windows, se `python` não estiver disponível, use `py`.

```bash
python main.py
python main.py --passo
python main.py --resumo
python testes.py
```

Com `--passo`, pressione Enter para executar cada instrução. O terminal mostra o PC atual, a instrução, os registradores antes e depois, as mudanças na memória e o próximo PC. Os valores aparecem em decimal e hexadecimal: `0x0E`, por exemplo, corresponde a 14 em decimal.

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

As instruções são guardadas como strings, por exemplo `"ADD R0, R1"`, e os dados como números inteiros. Ambos ficam na mesma lista, como permite o enunciado. A limitação de 8 bits vale para os números; as instruções em texto não são codificadas em um byte real.

`LOAD` carrega um valor imediato. Em `LOAD R0, 5`, o número 5 é o valor que vai para R0, não um endereço de memória. Esse comportamento segue a tabela de instruções e o código-base do professor. O enunciado também menciona transferências entre memória e registradores, mas não define uma instrução para ler dados por endereço.

O PC normalmente avança uma posição após a instrução. Com `JMP`, ele recebe o endereço do salto. `HALT` encerra a execução e mantém o PC na instrução de parada, como no código-base. Depois de `HALT`, chamar outro ciclo não executa nenhuma instrução.

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

Nas operações com dois registradores, o resultado fica no primeiro. O segundo mantém seu valor, exceto quando os dois operandos apontam para o mesmo registrador.

## Ciclo Fetch / Decode / Execute

1. **Fetch:** `ciclo()` lê `memoria[pc]`.
2. **Decode:** `decodificar()` separa operação e operandos, verifica os registradores e endereços.
3. **Execute:** `executar_instrucao()` faz a transferência, chama a ULA, modifica o PC ou encerra.

O histórico guarda cópias dos registradores e os valores do PC antes e depois de cada ciclo, além das posições de memória que mudaram. A tabela final é montada a partir desses registros.

## Representação de 8 bits

A função `limitar_8bits(valor)` usa a máscara `valor & 0xFF` para manter os oito bits menos significativos. Com números inteiros, isso equivale a calcular o resto da divisão por 256.

- 5 + 8 = 13.
- 255 + 1 = 256; em 8 bits, o resultado armazenado é 0.
- 0 - 1 = -1; o padrão de 8 bits é `11111111`, exibido como 255 sem sinal.

Não há flags de carry, overflow ou sinal nesta arquitetura.

## Programa próprio

O programa começa com o valor 12 e aplica operações aritméticas e lógicas. Ao final, grava o resultado na posição 15 e o valor de R1 na posição 14. Ele usa as cinco operações da ULA, além de LOAD, STORE, JMP e HALT.

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

Das 13 instruções armazenadas, 12 são executadas: o salto pula o endereço 9. As posições 14 e 15 ficam livres para os dados, então STORE não sobrescreve nenhuma instrução desse programa.

### Evolução esperada e verificada pelos testes

A tabela mostra os valores em decimal, depois de cada instrução.

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

Os testes de `testes.py` usam `unittest`, da biblioteca padrão do Python. Conferem as cinco operações da ULA, LOAD, STORE, o avanço e o salto do PC, a parada, os limites de 8 bits e os dois programas: o exemplo do enunciado e o programa próprio. Também verificam registradores e endereços inválidos, o limite de ciclos e o modo passo a passo.

Na execução local com Python 3.14, os 36 testes passaram.

O exemplo do enunciado grava MEM[15] = 13. Já o programa `8bits` mostra como o resultado volta para zero em 255 + 1 e passa a 255 em 0 - 1.

## Arquivos

- `cpu.py`: registradores, memória, PC e ciclo de execução.
- `ula.py`: operações aritméticas/lógicas e limitação de 8 bits.
- `programas.py`: programa próprio e exemplos.
- `main.py`: terminal, passo a passo, tabela e exportação CSV.
- `testes.py`: testes automáticos.

## Limites do modelo

Nesta simulação didática, não há clock físico, pipeline, interrupções, entrada/saída ou instruções binárias reais. Se o PC apontar para uma posição que contém um dado, a busca da instrução gera um erro. Um programa sem HALT para ao atingir o limite de ciclos, não por uma instrução de parada.
