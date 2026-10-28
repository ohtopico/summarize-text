"""Interface de linha de comando: ``sumarizar arquivo.txt``."""

import argparse
import sys

from .nucleo import METODOS, sumarizar


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="sumarizar",
        description="Resume um texto escolhendo suas frases mais importantes.",
    )
    parser.add_argument(
        "arquivo", nargs="?", help="arquivo de texto (sem ele, lê da entrada padrão)"
    )
    grupo = parser.add_mutually_exclusive_group()
    grupo.add_argument("-n", "--frases", type=int, help="número de frases do resumo")
    grupo.add_argument(
        "-p", "--proporcao", type=float, help="fração do texto, entre 0 e 1 (padrão: 0.3)"
    )
    parser.add_argument(
        "-m", "--metodo", choices=METODOS, default="textrank", help="algoritmo (padrão: textrank)"
    )
    parser.add_argument(
        "-i", "--idioma", choices=("pt", "en"), default="pt", help="idioma do texto (padrão: pt)"
    )
    parser.add_argument("--encoding", default="utf-8", help="codificação do arquivo (padrão: utf-8)")
    args = parser.parse_args(argv)

    if args.arquivo:
        with open(args.arquivo, encoding=args.encoding) as f:
            texto = f.read()
    else:
        texto = sys.stdin.read()

    try:
        resumo = sumarizar(
            texto,
            frases=args.frases,
            proporcao=args.proporcao,
            metodo=args.metodo,
            idioma=args.idioma,
        )
    except ValueError as erro:
        parser.error(str(erro))
    print(resumo)
    return 0


if __name__ == "__main__":
    sys.exit(main())
