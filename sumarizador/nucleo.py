"""Algoritmos de sumarização extrativa."""

import math
from collections import Counter

from .stopwords import POR_IDIOMA
from .texto import dividir_frases, tokenizar

METODOS = ("textrank", "frequencia")


def sumarizar(texto, frases=None, proporcao=None, metodo="textrank", idioma="pt"):
    """Resume ``texto`` escolhendo as frases mais representativas.

    Use ``frases`` para fixar quantas frases o resumo terá, ou ``proporcao``
    (entre 0 e 1) para escolher uma fração do texto. Sem nenhum dos dois,
    o resumo terá cerca de 30% das frases (no mínimo 1).

    As frases escolhidas são devolvidas na ordem em que aparecem no texto.
    """
    lista = ranquear_frases(texto, metodo=metodo, idioma=idioma)
    if not lista:
        return ""
    total = len(lista)
    n = _quantidade(total, frases, proporcao)
    melhores = sorted(lista, key=lambda item: item[1], reverse=True)[:n]
    escolhidas = sorted(melhores, key=lambda item: item[0])
    return " ".join(frase for _, _, frase in escolhidas)


def ranquear_frases(texto, metodo="textrank", idioma="pt"):
    """Devolve uma lista de ``(posição, pontuação, frase)`` para cada frase."""
    if metodo not in METODOS:
        raise ValueError(f"método desconhecido: {metodo!r} (use um de {METODOS})")
    if idioma not in POR_IDIOMA:
        raise ValueError(f"idioma desconhecido: {idioma!r} (use um de {tuple(POR_IDIOMA)})")

    frases = dividir_frases(texto)
    stopwords = POR_IDIOMA[idioma]
    tokens = [tokenizar(f, stopwords, idioma) for f in frases]
    if metodo == "frequencia":
        pontuacoes = _pontuar_por_frequencia(tokens)
    else:
        pontuacoes = _pontuar_por_textrank(tokens)
    return [(i, pontuacoes[i], frases[i]) for i in range(len(frases))]


def _quantidade(total, frases, proporcao):
    if frases is not None and proporcao is not None:
        raise ValueError("informe 'frases' ou 'proporcao', não os dois")
    if frases is not None:
        if frases < 1:
            raise ValueError("'frases' deve ser pelo menos 1")
        return min(frases, total)
    if proporcao is None:
        proporcao = 0.3
    if not 0 < proporcao <= 1:
        raise ValueError("'proporcao' deve estar entre 0 e 1")
    return max(1, min(total, round(total * proporcao)))


def _pontuar_por_frequencia(tokens):
    """Pontua cada frase pela frequência média normalizada de suas palavras."""
    freq = Counter(t for frase in tokens for t in frase)
    if not freq:
        return [0.0] * len(tokens)
    maior = max(freq.values())
    pontuacoes = []
    for frase in tokens:
        if not frase:
            pontuacoes.append(0.0)
            continue
        soma = sum(freq[t] / maior for t in frase)
        # Divide pela raiz do tamanho para não favorecer demais frases longas.
        pontuacoes.append(soma / math.sqrt(len(frase)))
    return pontuacoes


def _pontuar_por_textrank(tokens, amortecimento=0.85, iteracoes=100, tolerancia=1e-6):
    """TextRank: PageRank sobre o grafo de similaridade entre frases."""
    n = len(tokens)
    if n == 0:
        return []
    conjuntos = [set(t) for t in tokens]
    pesos = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            s = _similaridade(conjuntos[i], conjuntos[j])
            pesos[i][j] = pesos[j][i] = s
    somas = [sum(linha) for linha in pesos]

    pontos = [1.0 / n] * n
    for _ in range(iteracoes):
        novos = []
        for i in range(n):
            entrada = sum(
                pesos[j][i] / somas[j] * pontos[j] for j in range(n) if somas[j] > 0
            )
            novos.append((1 - amortecimento) / n + amortecimento * entrada)
        # Frases sem ligação distribuem sua pontuação igualmente.
        perdido = sum(pontos[j] for j in range(n) if somas[j] == 0)
        novos = [p + amortecimento * perdido / n for p in novos]
        if sum(abs(a - b) for a, b in zip(novos, pontos)) < tolerancia:
            pontos = novos
            break
        pontos = novos
    return pontos


def _similaridade(a, b):
    """Similaridade do artigo original do TextRank (Mihalcea e Tarau, 2004)."""
    comuns = len(a & b)
    if comuns == 0 or len(a) < 2 or len(b) < 2:
        return 0.0
    return comuns / (math.log(len(a)) + math.log(len(b)))
