import re
from dataclasses import dataclass

PALAVRAS_CHAVE = {
    "pipeline",
    "task",
    "from",
    "to",
    "map",
    "filter",
    "after",
    "and",
    "or"
}

ESPECIFICACAO_TOKENS = [
    ("COMENTARIO_BLOCO",  r"/\*.*?\*/", re.S),
    ("COMENTARIO_LINHA",  r"//[^\n]*"),

    ("NOVA_LINHA",        r"\n"),
    ("ESPACO",            r"[ \t\r]+"),

    ("NUMERO",            r"\d+(\.\d+)?"),
    ("STRING",            r"'[^']*'"),

    ("IDENTIFICADOR",     r"[A-Za-z_]\w*"),

    ("IGUAL",             r"=="),
    ("DIFERENTE",         r"!="),
    ("MENOR_IGUAL",       r"<="),
    ("MAIOR_IGUAL",       r">="),
    ("MENOR",             r"<"),
    ("MAIOR",             r">"),

    ("ATRIBUICAO",        r"="),

    ("MAIS",              r"\+"),
    ("MENOS",             r"-"),
    ("VEZES",             r"\*"),
    ("DIVIDIR",           r"/"),

    ("ABRE_PARENTESES",   r"\("),
    ("FECHA_PARENTESES",  r"\)"),
    ("ABRE_CHAVES",       r"\{"),
    ("FECHA_CHAVES",      r"\}"),
    ("PONTO_VIRGULA",     r";"),
    ("VIRGULA",           r","),
    ("BARRA_VERTICAL",    r"\|"),
    ("PONTO",             r"\."),
]

partes = []
flags = 0
for nome, padrao, *extra in ESPECIFICACAO_TOKENS:
    partes.append(f"(?P<{nome}>{padrao})")
    if extra:
        flags |= extra[0]
REGEX_MESTRE = re.compile("|".join(partes), flags)

@dataclass
class Token:
    tipo: str
    lexema: str
    linha: int
    coluna: int

    def __str__(self):
        return f"Token({self.tipo}, '{self.lexema}', {self.linha}, {self.coluna})"

    def __repr__(self):
        return self.__str__()

class ErroLexico(Exception):
    def __init__(self, mensagem, linha, coluna):
        super().__init__(f"[Linha {linha}, Coluna {coluna}] Erro Léxico: {mensagem}")
        self.linha = linha
        self.coluna = coluna

class AnalisadorLexico:
    def __init__(self, codigo_fonte: str):
        self.codigo_fonte = codigo_fonte
        self.linha_atual = 1
        self.inicio_linha = 0

    def analisar(self):
        tokens = []
        posicao = 0
        codigo = self.codigo_fonte

        match = REGEX_MESTRE.match(codigo, posicao)

        while match:
            tipo_token = match.lastgroup
            lexema = match.group(tipo_token)
            inicio = match.start()
            coluna = (inicio - self.inicio_linha) + 1

            if tipo_token == "NOVA_LINHA":
                self.linha_atual += 1
                self.inicio_linha = match.end()

            elif tipo_token in ("ESPACO", "COMENTARIO_LINHA", "COMENTARIO_BLOCO"):
                if tipo_token == "COMENTARIO_BLOCO":
                    num_quebras = lexema.count("\n")
                    if num_quebras:
                        self.linha_atual += num_quebras
                        ultima_quebra = lexema.rfind("\n")
                        if ultima_quebra != -1:
                            self.inicio_linha = match.start() + ultima_quebra + 1

            elif tipo_token == "IDENTIFICADOR":
                lexema_lower = lexema.lower()
                if lexema_lower in PALAVRAS_CHAVE:
                    tipo_final = f"PC_{lexema_lower.upper()}"
                else:
                    tipo_final = "IDENTIFICADOR"
                tokens.append(Token(tipo_final, lexema, self.linha_atual, coluna))

            else:
                tokens.append(Token(tipo_token, lexema, self.linha_atual, coluna))

            posicao = match.end()
            match = REGEX_MESTRE.match(codigo, posicao)

        if posicao != len(codigo):
            caractere_invalido = codigo[posicao]
            coluna = (posicao - self.inicio_linha) + 1
            raise ErroLexico(
                f"Caractere não reconhecido: {repr(caractere_invalido)}",
                self.linha_atual,
                coluna
            )

        tokens.append(Token("FIM_ARQUIVO", "$", self.linha_atual,
                          (len(codigo) - self.inicio_linha) + 1))

        return tokens


if __name__ == "__main__":
    codigo_exemplo = """
    pipeline vendas {
        task extrair from 'database' to 'raw_data';

        task transformar {
            from 'raw_data'
            filter idade > 18 and salario >= 1000.50 or cargo == 'gerente'
            to 'processed'
        }

        task carregar {
            from 'processed'
            to 'warehouse'
            after extrair, transformar
        }
    }
    """

    print("=== ANÁLISE LÉXICA DO CÓDIGO PIPELANG ===\n")
    print("Código fonte:")
    print("-" * 60)
    print(codigo_exemplo)
    print("-" * 60)
    print("\nTokens identificados:")
    print("-" * 60)

    try:
        analisador = AnalisadorLexico(codigo_exemplo)
        tokens = analisador.analisar()

        print(f"{'LINHA':<6} {'COLUNA':<7} {'TIPO':<20} {'LEXEMA'}")
        print("-" * 60)

        for token in tokens:
            if token.tipo != "FIM_ARQUIVO":
                print(f"{token.linha:<6} {token.coluna:<7} {token.tipo:<20} '{token.lexema}'")

        print("-" * 60)
        print(f"\n[OK] Total de tokens: {len(tokens) - 1}")
        print("[OK] Analise lexica concluida com sucesso!")

    except ErroLexico as erro:
        print(f"\n[ERRO] {erro}")
