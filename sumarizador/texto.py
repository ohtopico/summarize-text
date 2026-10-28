"""Pré-processamento: divisão em frases, tokenização e radicalização leve."""

import re
import unicodedata

# Abreviações comuns que terminam com ponto e não encerram a frase.
ABREVIACOES = frozenset("""
sr sra srta dr dra prof profa exmo exma sto sta av rua pç etc ex obs pág pag
vol cap fig tab nº n art inc min máx seg ltda cia jr mr mrs ms vs
""".split())

_FIM_DE_FRASE = re.compile(r"([.!?…]+)[\"'”’)\]]*\s+")
_PALAVRA = re.compile(r"[^\W\d_]+(?:[-'][^\W\d_]+)*")


def dividir_frases(texto):
    """Divide o texto em frases, respeitando abreviações e números decimais."""
    texto = re.sub(r"[ \t]+", " ", texto.strip())
    frases = []
    inicio = 0
    for paragrafo_fim in re.finditer(r"\n\s*\n", texto):
        frases.extend(_dividir_bloco(texto[inicio:paragrafo_fim.start()]))
        inicio = paragrafo_fim.end()
    frases.extend(_dividir_bloco(texto[inicio:]))
    return frases


def _dividir_bloco(bloco):
    bloco = " ".join(bloco.split())
    frases = []
    inicio = 0
    for m in _FIM_DE_FRASE.finditer(bloco):
        antes = bloco[inicio:m.start()].split()
        ultima = antes[-1].lower().strip("(\"'") if antes else ""
        if m.group(1) == "." and (ultima in ABREVIACOES or len(ultima) == 1):
            continue
        proxima = bloco[m.end():m.end() + 1]
        if proxima and proxima.islower():
            continue
        frases.append(bloco[inicio:m.end()].strip())
        inicio = m.end()
    resto = bloco[inicio:].strip()
    if resto:
        frases.append(resto)
    return frases


def remover_acentos(palavra):
    nfkd = unicodedata.normalize("NFKD", palavra)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


# Sufixos removidos em ordem (mais longos primeiro). É um radicalizador
# simplificado, inspirado no RSLP, suficiente para agrupar flexões comuns.
_SUFIXOS_PT = (
    "amentos", "imentos", "amento", "imento", "adoras", "adores", "ações",
    "acoes", "mente", "idade", "idades", "ação", "acao", "ador", "adora",
    "ância", "ancia", "ência", "encia", "ismos", "istas", "ismo", "ista",
    "ões", "oes", "ais", "eis", "ns", "es", "as", "os", "s", "a", "o", "e",
)


def radical(palavra, idioma="pt"):
    """Reduz a palavra a um radical aproximado (minúsculo, sem acentos)."""
    p = remover_acentos(palavra.lower())
    if idioma != "pt":
        for suf in ("ing", "ed", "es", "s"):
            if p.endswith(suf) and len(p) - len(suf) >= 3:
                return p[: -len(suf)]
        return p
    for suf in _SUFIXOS_PT:
        if p.endswith(suf) and len(p) - len(suf) >= 3:
            return p[: -len(suf)]
    return p


def tokenizar(frase, stopwords, idioma="pt"):
    """Devolve os radicais das palavras relevantes de uma frase."""
    tokens = []
    for palavra in _PALAVRA.findall(frase):
        minuscula = palavra.lower()
        if minuscula in stopwords or len(minuscula) < 2:
            continue
        tokens.append(radical(minuscula, idioma))
    return tokens
