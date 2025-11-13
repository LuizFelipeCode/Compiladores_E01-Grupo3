from dataclasses import dataclass, field
from typing import List, Optional, Union

@dataclass
class NoAST:
    pass

@dataclass
class Pipeline(NoAST):
    nome: str
    tarefas: List['Tarefa']

    def __str__(self):
        tarefas_str = '\n  '.join(str(t) for t in self.tarefas)
        return f"Pipeline '{self.nome}':\n  {tarefas_str}"

@dataclass
class Tarefa(NoAST):
    nome: str
    origem: 'Origem'
    transformacao: Optional['Transformacao']
    saida: 'Saida'
    dependencias: Optional[List[str]]

    def __str__(self):
        deps = f" (depende de: {', '.join(self.dependencias)})" if self.dependencias else ""
        trans = f"\n    {self.transformacao}" if self.transformacao else ""
        return f"Task '{self.nome}': {self.origem} -> {self.saida}{trans}{deps}"

@dataclass
class Origem(NoAST):
    fonte: str

    def __str__(self):
        return f"from '{self.fonte}'"

@dataclass
class Saida(NoAST):
    destino: str

    def __str__(self):
        return f"to '{self.destino}'"

@dataclass
class Transformacao(NoAST):
    pass

@dataclass
class TransformacaoMap(Transformacao):
    campo: str
    valor: Union[str, float]

    def __str__(self):
        return f"map {self.campo} = {self.valor}"

@dataclass
class TransformacaoFilter(Transformacao):
    expressao: 'ExpressaoLogica'

    def __str__(self):
        return f"filter {self.expressao}"

@dataclass
class ExpressaoLogica(NoAST):
    pass

@dataclass
class ExpressaoBinaria(ExpressaoLogica):
    esquerda: ExpressaoLogica
    operador: str
    direita: ExpressaoLogica

    def __str__(self):
        return f"({self.esquerda} {self.operador} {self.direita})"

@dataclass
class ExpressaoComparacao(ExpressaoLogica):
    campo: str
    operador: str
    valor: Union[str, float, int]

    def __str__(self):
        return f"{self.campo} {self.operador} {self.valor}"

class ErroSintatico(Exception):
    def __init__(self, mensagem, linha=None, coluna=None):
        if linha and coluna:
            super().__init__(f"[Linha {linha}, Coluna {coluna}] Erro Sintático: {mensagem}")
        else:
            super().__init__(f"Erro Sintático: {mensagem}")
        self.linha = linha
        self.coluna = coluna


class AnalisadorSintatico:
    def __init__(self, tokens):
        self.tokens = tokens
        self.posicao = 0
        self.token_atual = tokens[0] if tokens else None

    def avancar(self):
        self.posicao += 1
        if self.posicao < len(self.tokens):
            self.token_atual = self.tokens[self.posicao]
        else:
            self.token_atual = None

    def verificar(self, tipo_esperado):
        return self.token_atual and self.token_atual.tipo == tipo_esperado

    def consumir(self, tipo_esperado):
        if not self.token_atual:
            raise ErroSintatico(f"Fim inesperado do arquivo. Esperado: {tipo_esperado}")

        if self.token_atual.tipo != tipo_esperado:
            raise ErroSintatico(
                f"Token inesperado. Esperado: {tipo_esperado}, Encontrado: {self.token_atual.tipo}",
                self.token_atual.linha,
                self.token_atual.coluna
            )

        lexema = self.token_atual.lexema
        self.avancar()
        return lexema

    def analisar(self):
        ast = self.pipeline()

        if self.token_atual and self.token_atual.tipo != "FIM_ARQUIVO":
            raise ErroSintatico(
                f"Token inesperado após o fim do pipeline: {self.token_atual.tipo}",
                self.token_atual.linha,
                self.token_atual.coluna
            )

        return ast

    def pipeline(self):
        self.consumir("PC_PIPELINE")
        nome = self.consumir("IDENTIFICADOR")
        self.consumir("ABRE_CHAVES")
        tarefas = self.lista_tarefas()
        self.consumir("FECHA_CHAVES")

        return Pipeline(nome, tarefas)

    def lista_tarefas(self):
        tarefas = []
        if not self.verificar("PC_TASK"):
            raise ErroSintatico(
                "Esperado pelo menos uma tarefa no pipeline",
                self.token_atual.linha if self.token_atual else None,
                self.token_atual.coluna if self.token_atual else None
            )

        tarefas.append(self.tarefa())

        while self.verificar("PONTO_VIRGULA"):
            self.avancar()

            if self.verificar("PC_TASK"):
                tarefas.append(self.tarefa())
            elif self.verificar("FECHA_CHAVES"):
                break
            else:
                raise ErroSintatico(
                    "Esperado 'task' ou '}' após ';'",
                    self.token_atual.linha,
                    self.token_atual.coluna
                )

        return tarefas

    def tarefa(self):
        self.consumir("PC_TASK")
        nome = self.consumir("IDENTIFICADOR")

        origem, transformacao, saida, dependencias = self.bloco_tarefa()

        return Tarefa(nome, origem, transformacao, saida, dependencias)

    def bloco_tarefa(self):
        if self.verificar("ABRE_CHAVES"):
            self.avancar()

            origem = self.origem()

            transformacao = None
            if self.verificar("PC_MAP") or self.verificar("PC_FILTER"):
                transformacao = self.transformacao()

            saida = self.saida()

            dependencias = None
            if self.verificar("PC_AFTER"):
                dependencias = self.dependencias()

            self.consumir("FECHA_CHAVES")

        else:
            origem = self.origem()
            saida = self.saida()
            transformacao = None

            dependencias = None
            if self.verificar("PC_AFTER"):
                dependencias = self.dependencias()

        return origem, transformacao, saida, dependencias

    def origem(self):
        self.consumir("PC_FROM")
        fonte = self.consumir("STRING")
        fonte = fonte.strip("'")
        return Origem(fonte)

    def saida(self):
        self.consumir("PC_TO")
        destino = self.consumir("STRING")
        destino = destino.strip("'")
        return Saida(destino)

    def transformacao(self):
        if self.verificar("PC_MAP"):
            return self.transformacao_map()
        elif self.verificar("PC_FILTER"):
            return self.transformacao_filter()
        else:
            raise ErroSintatico(
                "Esperado 'map' ou 'filter' para transformação",
                self.token_atual.linha,
                self.token_atual.coluna
            )

    def transformacao_map(self):
        self.consumir("PC_MAP")
        campo = self.consumir("IDENTIFICADOR")
        self.consumir("ATRIBUICAO")
        valor = self.valor()
        return TransformacaoMap(campo, valor)

    def transformacao_filter(self):
        self.consumir("PC_FILTER")
        expr = self.expressao_ou()
        return TransformacaoFilter(expr)

    def expressao_ou(self):
        esquerda = self.expressao_e()

        while self.verificar("PC_OR"):
            self.avancar()
            direita = self.expressao_e()
            esquerda = ExpressaoBinaria(esquerda, "or", direita)

        return esquerda

    def expressao_e(self):
        esquerda = self.expressao_comparacao()

        while self.verificar("PC_AND"):
            self.avancar()
            direita = self.expressao_comparacao()
            esquerda = ExpressaoBinaria(esquerda, "and", direita)

        return esquerda

    def expressao_comparacao(self):
        if self.verificar("ABRE_PARENTESES"):
            self.avancar()
            expr = self.expressao_ou()
            self.consumir("FECHA_PARENTESES")
            return expr

        campo = self.campo()
        operador = self.operador_comparacao()
        valor = self.valor()
        return ExpressaoComparacao(campo, operador, valor)

    def campo(self):
        campo = self.consumir("IDENTIFICADOR")

        while self.verificar("PONTO"):
            self.avancar()
            campo += "." + self.consumir("IDENTIFICADOR")

        return campo

    def operador_comparacao(self):
        operadores = ["IGUAL", "DIFERENTE", "MENOR", "MAIOR", "MENOR_IGUAL", "MAIOR_IGUAL"]

        if self.token_atual and self.token_atual.tipo in operadores:
            op = self.token_atual.lexema
            self.avancar()
            return op
        else:
            raise ErroSintatico(
                "Esperado operador de comparação (==, !=, <, >, <=, >=)",
                self.token_atual.linha if self.token_atual else None,
                self.token_atual.coluna if self.token_atual else None
            )

    def valor(self):
        if self.verificar("STRING"):
            valor = self.consumir("STRING").strip("'")
            return valor
        elif self.verificar("NUMERO"):
            valor = self.consumir("NUMERO")
            return float(valor) if '.' in valor else int(valor)
        elif self.verificar("IDENTIFICADOR"):
            return self.consumir("IDENTIFICADOR")
        else:
            raise ErroSintatico(
                "Esperado valor (string, número ou identificador)",
                self.token_atual.linha if self.token_atual else None,
                self.token_atual.coluna if self.token_atual else None
            )

    def dependencias(self):
        self.consumir("PC_AFTER")

        deps = []
        deps.append(self.consumir("IDENTIFICADOR"))

        while self.verificar("VIRGULA"):
            self.avancar()
            deps.append(self.consumir("IDENTIFICADOR"))

        return deps


if __name__ == "__main__":
    from lexer import AnalisadorLexico, Token

    codigo_exemplo = """
    pipeline vendas {
        task extrair {
            from 'database'
            to 'raw_data'
        };
        task transformar {
            from 'raw_data'
            filter idade > 18 and salario >= 1000.50 or cargo == 'gerente'
            to 'processed'
            after extrair
        }
    }
    """

    print("=== ANÁLISE SINTÁTICA PIPELANG ===\n")
    print("Código fonte:")
    print("-" * 60)
    print(codigo_exemplo)
    print("-" * 60)

    try:
        lexer = AnalisadorLexico(codigo_exemplo)
        tokens = lexer.analisar()

        print(f"\n[OK] Analise lexica: {len(tokens) - 1} tokens identificados")

        parser = AnalisadorSintatico(tokens)
        ast = parser.analisar()

        print("[OK] Analise sintatica concluida com sucesso!\n")
        print("Arvore Sintatica Abstrata (AST):")
        print("-" * 60)
        print(ast)

    except Exception as erro:
        print(f"[ERRO] {erro}")
