# Compilador PipeLang

Compilador completo para a linguagem PipeLang, uma DSL (Domain-Specific Language) para definição e execução de pipelines de dados ETL (Extract, Transform, Load).

---

## 📋 Objetivo

O objetivo deste projeto é desenvolver um **compilador completo** que:

- Compila código escrito em PipeLang (arquivos `.pipe`)
- Realiza análise léxica, sintática e semântica
- Gera representação intermediária (IR) em formato JSON
- Valida dependências entre tarefas e detecta erros (ciclos, variáveis não definidas, etc.)
- **Simula a execução** do pipeline, respeitando a ordem de dependências

O compilador permite criar pipelines de dados de forma declarativa, definindo tarefas de extração, transformação e carregamento de dados, com suas respectivas dependências.

---

## 🛠️ Linguagem e Ferramentas Utilizadas

### Linguagem
- **Python 3.x** (versão 3.8 ou superior)

### Bibliotecas Python Utilizadas
- `sys` - Gerenciamento de argumentos e códigos de saída
- `json` - Manipulação de arquivos JSON (IR)
- `argparse` - Parse de argumentos da linha de comando
- `dataclasses` - Estruturas de dados para AST
- `collections` (defaultdict, deque) - Estruturas auxiliares
- `datetime` - Timestamp para metadados
- `time` - Simulação de tempo de execução
- `random` - Delays aleatórios na simulação
- `tempfile` - Arquivos temporários para IR
- `os` - Operações de sistema

### Estrutura do Projeto
```
Compiladores_E01-Grupo3/
├── src/
│   ├── lexer.py        # Analisador Léxico
│   ├── parser.py       # Analisador Sintático (AST)
│   ├── semantic.py     # Analisador Semântico + Tabela de Símbolos
│   ├── codegen.py      # Gerador de IR
│   ├── compiler.py     # Orquestrador principal
│   └── simulator.py    # Simulador de execução
├── exemplos/           # Arquivos de exemplo .pipe
├── demo/               # IRs geradas (JSON)
└── docs/               # Documentação e relatórios
```

---

## 🚀 Instruções de Execução

### Pré-requisitos
- Python 3.8 ou superior instalado
- Nenhuma biblioteca externa necessária (usa apenas bibliotecas padrão)

### 1. Compilar um arquivo PipeLang

Compila o código e exibe a tabela de símbolos e pseudo-código:

```bash
python src/compiler.py exemplos/vendas_completo.pipe
```

**Saída:**
- Relatório de compilação (5 fases)
- Tabela de símbolos
- Pseudo-código gerado

---

### 2. Compilar e salvar IR em JSON

Compila e salva a representação intermediária em um arquivo JSON:

```bash
python src/compiler.py exemplos/vendas_completo.pipe output.json
```

**Saída:**
- Mesmo que opção 1
- Arquivo `output.json` criado com a IR

---

### 3. Compilar e Simular Automaticamente ⭐ (RECOMENDADO)

Compila e executa o simulador automaticamente:

```bash
python src/compiler.py exemplos/vendas_completo.pipe --simulate
```

ou usando a forma curta:

```bash
python src/compiler.py exemplos/vendas_completo.pipe -s
```

**Saída:**
- Relatório de compilação
- Tabela de símbolos
- Pseudo-código
- **Execução simulada do pipeline com logs em tempo real**
- Resumo com tempo de execução

---

### 4. Executar Simulador com IR existente

Se você já tem um arquivo JSON (IR), pode executar apenas o simulador:

```bash
python src/simulator.py demo/pipeline_simples.json
```

**Saída:**
- Execução simulada das tarefas
- Logs coloridos do progresso
- Resumo final

---

### Exemplos Disponíveis

O projeto inclui vários exemplos na pasta `exemplos/`:

- `vendas_completo.pipe` - Pipeline de vendas com filtros e métricas
- `pipeline_simples.pipe` - Pipeline linear básico (EXTRACT → TRANSFORM → LOAD)
- `pipeline_paralelo.pipe` - Pipeline com tarefas paralelas
- `pipeline_complexo.pipe` - Pipeline com múltiplas dependências

---

## 👥 Responsabilidades de Cada Integrante

### SEMANA 01 - Análise Semântica

- **Caio Vasconcelos Araújo Figueiredo**: Implementação do código principal (`semantic.py`), construção da Tabela de Símbolos e lógica de verificação semântica

- **Gabriel Oliveira Evangelista Luiz**: Testes de execução com `ok.pipe` e `erros.pipe`, documentação dos resultados e análise dos erros detectados

- **Felipe Prudente Borges**: Criação dos repositórios, estruturação do relatório, revisão teórica sobre análise semântica e padronização do documento acadêmico

---

### SEMANA 02 - Representação Intermediária

- **Caio Vasconcelos Araújo Figueiredo**: Implementação do gerador de código intermediário (`codegen.py`), algoritmo de ordenação topológica e geração de representação JSON

- **Gabriel Oliveira Evangelista Luiz**: Criação de exemplos de pipelines (`pipeline_simples.pipe`, `pipeline_complexo.pipe`, `pipeline_paralelo.pipe`) e validação da geração de IR

- **Felipe Prudente Borges**: Correção do parser para suporte a comentários, geração de pseudo-código e refinamento da saída do compilador

---

### SEMANA 03 - Simulador de Execução

- **Caio Vasconcelos Araújo Figueiredo**: Implementação do simulador (`simulator.py`), classes ArtifactManager, TaskExecutor e PipelineSimulator com lógica de execução e rastreamento de artefatos

- **Gabriel Oliveira Evangelista Luiz**: Validação com exemplos (pipeline_simples, pipeline_paralelo, pipeline_complexo), testes de execução e análise dos resultados

- **Felipe Prudente Borges**: Integração do simulador com o compilador (flag --simulate), documentação e refinamento da interface CLI

---

## 📸 Exemplos de Saída

### Exemplo 1: Compilação Bem-Sucedida

```
============================================================
COMPILADOR PIPELANG
============================================================
Arquivo: exemplos/vendas_completo.pipe

[1/5] Analise Lexica...
      61 tokens identificados
[2/5] Analise Sintatica...
      Pipeline 'vendas' com 4 tarefa(s)
[3/5] Conversao AST -> Tabela de Simbolos...
      4 tarefa(s) na tabela de simbolos
[4/5] Analise Semantica...
      Nenhum erro semantico encontrado
[5/5] Geracao de Codigo Intermediario...
      IR gerada com sucesso

============================================================
[OK] COMPILACAO CONCLUIDA COM SUCESSO!
============================================================

== Tabela de Símbolos ==
- extrair_dados : EXTRACT
    outputs: dados_brutos
- filtrar_clientes : TRANSFORM
    inputs:  dados_brutos
    outputs: clientes_validos
    deps:    extrair_dados
- calcular_metricas : TRANSFORM
    inputs:  clientes_validos
    outputs: metricas
    deps:    filtrar_clientes
- carregar_warehouse : LOAD
    inputs:  metricas
    deps:    calcular_metricas
```

---

### Exemplo 2: Simulação de Pipeline

```
============================================================
SIMULADOR DE PIPELINE - PipeLang v1.0
============================================================

Pipeline: exemplos/vendas_completo.pipe
Total de tarefas: 4

[1/4] Executando: extrair_dados (EXTRACT)
  -> Extraindo dados da fonte...
  -> Artefato gerado: 'dados_brutos' OK
  -> Tempo: 0.67s
  -> Status: COMPLETO OK

[2/4] Executando: filtrar_clientes (TRANSFORM)
  -> Dependência satisfeita: extrair_dados OK
  -> Lendo artefato: 'dados_brutos' (de extrair_dados) OK
  -> Transformando dados...
  -> Artefato gerado: 'clientes_validos' OK
  -> Tempo: 0.70s
  -> Status: COMPLETO OK

[3/4] Executando: calcular_metricas (TRANSFORM)
  -> Dependência satisfeita: filtrar_clientes OK
  -> Lendo artefato: 'clientes_validos' (de filtrar_clientes) OK
  -> Transformando dados...
  -> Artefato gerado: 'metricas' OK
  -> Tempo: 0.89s
  -> Status: COMPLETO OK

[4/4] Executando: carregar_warehouse (LOAD)
  -> Dependência satisfeita: calcular_metricas OK
  -> Lendo artefato: 'metricas' (de calcular_metricas) OK
  -> Carregando dados no destino final...
  -> Dados carregados com sucesso OK
  -> Tempo: 0.56s
  -> Status: COMPLETO OK

============================================================
EXECUÇÃO CONCLUÍDA COM SUCESSO! OK

Tarefas executadas: 4/4
Tempo total: 2.82s

Tempo por tarefa:
  * extrair_dados: 0.67s (completed)
  * filtrar_clientes: 0.70s (completed)
  * calcular_metricas: 0.89s (completed)
  * carregar_warehouse: 0.56s (completed)
============================================================
```

---

### Exemplo 3: Detecção de Erros

```
============================================================
COMPILADOR PIPELANG
============================================================
Arquivo: exemplos/erro_ciclo.pipe

[1/5] Analise Lexica...
      45 tokens identificados
[2/5] Analise Sintatica...
      Pipeline 'teste' com 3 tarefa(s)
[3/5] Conversao AST -> Tabela de Simbolos...
      3 tarefa(s) na tabela de simbolos
[4/5] Analise Semantica...
[ERRO] Erros semanticos encontrados:
       [E-CYCLE] Ciclo detectado no grafo de dependencias.

============================================================
[FALHA] COMPILACAO FALHOU
============================================================
```

---

## 📝 Formato da Linguagem PipeLang

### Exemplo de Código

```
pipeline vendas {
    task extrair_dados {
        from 'database_vendas'
        to 'dados_brutos'
    };

    task filtrar_clientes {
        from 'dados_brutos'
        filter idade >= 18 and status == 'ativo'
        to 'clientes_validos'
        after extrair_dados
    };

    task calcular_metricas {
        from 'clientes_validos'
        map total_vendas = 'sum(vendas)'
        to 'metricas'
        after filtrar_clientes
    };

    task carregar_warehouse {
        from 'metricas'
        to 'data_warehouse'
        after calcular_metricas
    }
}
```

### Conceitos Principais

- **pipeline**: Define um conjunto de tarefas relacionadas
- **task**: Define uma tarefa individual (EXTRACT, TRANSFORM ou LOAD)
- **from/to**: Define artefatos de entrada e saída
- **after**: Define dependências entre tarefas
- **filter**: Aplica filtros aos dados
- **map**: Aplica transformações aos dados

---

## 📚 Documentação Adicional

Consulte a pasta `docs/` para relatórios detalhados de cada semana:
- `# Relatorio Semana 01.txt` - Análise Semântica
- `# Relatorio Semana 02.txt` - Representação Intermediária
- `Relatorio Semana 03.txt` - Simulador de Execução

---

## 🎓 Projeto Acadêmico

Este projeto foi desenvolvido como parte da disciplina de Compiladores.

**Disciplina:** Compiladores
**Grupo:** 3

---

**Desenvolvido por Caio, Gabriel e Felipe**
