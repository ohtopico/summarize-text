import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from sumarizador import ranquear_frases, sumarizar
from sumarizador.cli import main
from sumarizador.texto import dividir_frases, radical, tokenizar
from sumarizador.stopwords import PORTUGUES

EXEMPLO = (Path(__file__).parent.parent / "exemplos" / "acessibilidade.txt").read_text(
    encoding="utf-8"
)


class TestDivisaoDeFrases(unittest.TestCase):
    def test_frases_simples(self):
        self.assertEqual(
            dividir_frases("Olá mundo. Tudo bem? Sim!"),
            ["Olá mundo.", "Tudo bem?", "Sim!"],
        )

    def test_abreviacoes_e_decimais(self):
        texto = "O Dr. Silva mediu 3.5 metros. Depois saiu."
        self.assertEqual(dividir_frases(texto), ["O Dr. Silva mediu 3.5 metros.", "Depois saiu."])

    def test_paragrafos_sem_pontuacao_final(self):
        self.assertEqual(dividir_frases("Título\n\nTexto aqui."), ["Título", "Texto aqui."])

    def test_texto_vazio(self):
        self.assertEqual(dividir_frases("   "), [])


class TestTokenizacao(unittest.TestCase):
    def test_remove_stopwords_e_agrupa_flexoes(self):
        tokens = tokenizar("As redes neurais e a rede neural", PORTUGUES)
        self.assertEqual(tokens.count(radical("rede")), 2)
        self.assertNotIn("as", tokens)

    def test_ignora_acentos(self):
        self.assertEqual(radical("ação"), radical("acao"))


class TestSumarizar(unittest.TestCase):
    def test_numero_de_frases(self):
        for metodo in ("textrank", "frequencia"):
            resumo = sumarizar(EXEMPLO, frases=3, metodo=metodo)
            self.assertEqual(len(dividir_frases(resumo)), 3, metodo)

    def test_mantem_ordem_original(self):
        frases = dividir_frases(EXEMPLO)
        resumo = dividir_frases(sumarizar(EXEMPLO, frases=4))
        posicoes = [frases.index(f) for f in resumo]
        self.assertEqual(posicoes, sorted(posicoes))

    def test_proporcao(self):
        total = len(dividir_frases(EXEMPLO))
        resumo = sumarizar(EXEMPLO, proporcao=0.5)
        self.assertEqual(len(dividir_frases(resumo)), round(total * 0.5))

    def test_frases_vem_do_texto(self):
        frases = set(dividir_frases(EXEMPLO))
        for f in dividir_frases(sumarizar(EXEMPLO, frases=3)):
            self.assertIn(f, frases)

    def test_texto_vazio(self):
        self.assertEqual(sumarizar(""), "")

    def test_mais_frases_que_o_texto(self):
        self.assertEqual(sumarizar("Uma frase só.", frases=10), "Uma frase só.")

    def test_pontuacoes(self):
        lista = ranquear_frases(EXEMPLO)
        self.assertEqual(len(lista), len(dividir_frases(EXEMPLO)))
        self.assertTrue(all(p > 0 for _, p, _ in lista))

    def test_erros(self):
        with self.assertRaises(ValueError):
            sumarizar(EXEMPLO, metodo="magia")
        with self.assertRaises(ValueError):
            sumarizar(EXEMPLO, proporcao=1.5)
        with self.assertRaises(ValueError):
            sumarizar(EXEMPLO, frases=2, proporcao=0.5)
        with self.assertRaises(ValueError):
            sumarizar(EXEMPLO, idioma="fr")

    def test_ingles(self):
        texto = (
            "Cats are popular pets. Many people love cats. "
            "Dogs are loyal. The weather is nice today."
        )
        self.assertIn("cats", sumarizar(texto, frases=1, idioma="en").lower())


class TestCli(unittest.TestCase):
    def test_arquivo(self):
        caminho = Path(__file__).parent.parent / "exemplos" / "acessibilidade.txt"
        saida = io.StringIO()
        with redirect_stdout(saida):
            main([str(caminho), "-n", "2"])
        self.assertEqual(len(dividir_frases(saida.getvalue())), 2)


if __name__ == "__main__":
    unittest.main()
