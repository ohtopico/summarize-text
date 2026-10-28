"""Listas de palavras vazias (stopwords) em português e inglês."""

PORTUGUES = frozenset("""
a à ao aos aquela aquelas aquele aqueles aquilo as às até com como contra
da das de dela delas dele deles depois do dos e é ela elas ele eles em entre
era eram essa essas esse esses esta está estão estas estava estavam este estes
eu foi foram há isso isto já lhe lhes mais mas me mesmo meu meus minha minhas
muito muitos na não nas nem no nos nós nossa nossas nosso nossos num numa o os
ou para pela pelas pelo pelos por qual quando que quem se sem ser será seu
seus só sua suas também te tem têm ter teu tua tuas tu um uma umas uns você
vocês vos sobre são sido seja sejam fosse fossem pode podem onde assim ainda
então porque pois cada todo toda todos todas outro outra outros outras
tão tal tais lá aqui ali bem sim tinha tinham havia houve vai vão estar
""".split())

INGLES = frozenset("""
a about above after again against all am an and any are as at be because been
before being below between both but by can could did do does doing down during
each few for from further had has have having he her here hers herself him
himself his how i if in into is it its itself just me more most my myself no
nor not now of off on once only or other our ours ourselves out over own same
she should so some such than that the their theirs them themselves then there
these they this those through to too under until up very was we were what when
where which while who whom why will with would you your yours yourself
""".split())

POR_IDIOMA = {"pt": PORTUGUES, "en": INGLES}
