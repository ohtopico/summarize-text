# summarize-text

Sumarizador **extrativo** de textos em Python, pensado para o português (também funciona em inglês).
Ele escolhe as frases mais importantes do texto e as devolve na ordem original. Não usa nenhuma
biblioteca externa: só a biblioteca padrão do Python (3.8 ou mais recente).

## Instalação

```bash
git clone https://github.com/ohtopico/summarize-text
cd summarize-text
pip install .
```

Também dá para usar sem instalar, rodando `python -m sumarizador` dentro da pasta do projeto.

## Uso na linha de comando

```bash
# resumo com 3 frases
sumarizar exemplos/acessibilidade.txt -n 3

# resumo com 20% das frases, usando o método de frequência
sumarizar artigo.txt -p 0.2 -m frequencia

# lendo da entrada padrão, texto em inglês
cat article.txt | sumarizar -n 5 -i en
```

| Opção | O que faz |
| --- | --- |
| `-n`, `--frases` | número de frases do resumo |
| `-p`, `--proporcao` | fração das frases do texto, entre 0 e 1 (padrão: `0.3`) |
| `-m`, `--metodo` | `textrank` (padrão) ou `frequencia` |
| `-i`, `--idioma` | `pt` (padrão) ou `en` |
| `--encoding` | codificação do arquivo (padrão: `utf-8`; use `latin-1` para arquivos antigos do Windows) |

## Uso no Python

```python
from sumarizador import sumarizar, ranquear_frases

texto = open("artigo.txt", encoding="utf-8").read()

print(sumarizar(texto, frases=3))
print(sumarizar(texto, proporcao=0.2, metodo="frequencia"))

# pontuação de cada frase: (posição, pontuação, frase)
for posicao, pontuacao, frase in ranquear_frases(texto):
    print(f"{pontuacao:.3f}  {frase}")
```

## Como funciona

1. **Divisão em frases.** O texto é quebrado em `.`, `!`, `?` e `…`, sem quebrar em abreviações
   (`Dr.`, `Sra.`, `etc.`), iniciais (`J. R.`) ou números decimais (`3.5`). Parágrafos sem ponto
   final, como títulos, viram frases próprias.
2. **Pré-processamento.** Cada frase vira uma lista de palavras em minúsculas, sem acentos e sem
   *stopwords* (artigos, preposições etc.). Um radicalizador simples agrupa flexões como
   "rede"/"redes" e "neural"/"neurais".
3. **Pontuação das frases**, com um de dois métodos:
   - **`textrank`** (padrão): monta um grafo em que cada frase é um nó e as arestas medem
     quantas palavras duas frases compartilham. Aplica o PageRank nesse grafo, então frases
     "centrais", que se parecem com muitas outras, ganham mais pontos
     ([Mihalcea e Tarau, 2004](https://aclanthology.org/W04-3252/)).
   - **`frequencia`**: soma a frequência normalizada das palavras de cada frase e divide pela raiz
     do tamanho da frase. É mais rápido e funciona bem em textos curtos.
4. **Montagem do resumo.** As frases com mais pontos são escolhidas e recolocadas na ordem em que
   aparecem no texto original.

### Limitações

- É um resumo **extrativo**: copia frases do texto, não reescreve. Para resumos que reescrevem o
  texto (abstrativos) seria preciso um modelo de linguagem.
- O TextRank compara todas as frases entre si, então fica lento em textos com milhares de frases.
  Nesses casos, prefira `-m frequencia`.
- O radicalizador é simplificado; ele erra em algumas palavras, mas isso pouco afeta o ranking.

## Testes

```bash
python -m unittest -v
```
