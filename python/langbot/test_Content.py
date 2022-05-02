import unittest
import Content

class TestParse(unittest.TestCase):

    def test_sole_link(self):
        line = r"opzicht===Pronunciation===\n* {{audio|nl|Nl-opzicht.ogg|Audio}}\n* {{hyphenation|nl|op|zicht}}\n\n===Noun===\n{{nl-noun|n|-en|opzichtje}}\n\n# {{l|en|supervision}}\n# {{l|en|relation}}, {{l|en|regard}}\n#: ''In welk '''opzicht'''?'' - In what regard?\n\n====Derived terms====\n* {{l|nl|opzichter}}\n* {{l|nl|ten opzichte van}}"
        (title, definition, grammatical_class, main_definition) = Content._parse(line)
        self.assertEqual(title, "opzicht")
        self.assertEqual(definition, """## Noun
alternative spelling: opzichtje

* supervision
* relation, regard
*: ''In welk '''opzicht'''?'' - In what regard?

""")
        self.assertEqual(grammatical_class, "Noun")
        self.assertEqual(main_definition, "supervision")

    def test_double_link(self):
        line = r"priesterschap===Pronunciation===\n* {{IPA|nl|/ˈpris.tərˌsxɑp/}}\n* {{audio|nl|Nl-priesterschap.ogg|Audio}}\n* {{hyphenation|nl|pries|ter|schap}}\n\n===Noun===\n{{nl-noun|f|-en|-}}\n\n# {{l|en|priesthood}} (referring to priests as a whole)\n\n===Noun===\n{{nl-noun|n|-en|-}}\n\n# [[priesthood]] {{gloss|state of being a priest}}\n# {{lb|nl|Roman Catholicism}} one of the three major orders of the {{l|en|Roman Catholic Church}} - the {{l|en|priestly}} order"
        (title, definition, grammatical_class, main_definition) = Content._parse(line)
        self.assertEqual(title, "priesterschap")
        self.assertEqual(definition, """## Noun
(feminine)

* priesthood (referring to priests as a whole)

## Noun
(neuter)

* priesthood (state of being a priest)
* (Roman Catholicism) one of the three major orders of the Roman Catholic Church - the priestly order""")
        self.assertEqual(grammatical_class, "Noun")
        self.assertEqual(main_definition, "priesthood (referring to priests as a whole)")

    def test_transitive(self):
        line = r"rendre la monnaie de sa pièce===Pronunciation===\n* {{audio|fr|LL-Q150 (fra)-WikiLucas00-rendre la monnaie de sa pièce.wav|Audio}}\n\n===Verb===\n{{fr-verb}}\n\n# {{indtr|fr|à}} to give someone a [[taste of one's own medicine|taste of their own medicine]], to [[retaliate]], to [[pay back in someone's own coin]], to [[pay back]] [[in kind]]\n#: {{syn|fr|rendre la pareille}}"
        (title, definition, grammatical_class, main_definition) = Content._parse(line)
        self.assertEqual(title, "rendre la monnaie de sa pièce")
        self.assertEqual(definition, """## Verb

* (transitive with 'à') to give someone a taste of their own medicine, to retaliate, to pay back in someone's own coin, to pay back in kind
* synonym: rendre la pareille""")
        self.assertEqual(grammatical_class, "Verb")
        self.assertEqual(main_definition, "to give someone a taste of their own medicine, to retaliate, to pay back in someone's own coin, to pay back in kind")

    def test_relational(self):
        line = r"životinjski===Pronunciation===\n* {{a|adjective}} {{IPA|sh|/ʒiʋǒtiːɲskiː/}}\n* {{a|adverb}} {{IPA|sh|/ʒiʋǒtiːɲski/}}\n* {{hyphenation|sh|ži|vo|tinj|ski}}\n\n===Adjective===\n{{sh-adj|head=živòtīnjskī}}\n\n# {{lb|sh|relational}} [[animal]]\n# {{lb|sh|figuratively}} [[animal]], [[beast]], like an animal\n\n====Declension====\n{{sh-adj-def|životinjsk|o}}\n\n===Adverb===\n{{sh-adverb|head=živòtīnjski}}\n\n# like an animal; [[beastly]], [[brutally]]"
        (title, definition, grammatical_class, main_definition) = Content._parse(line)
        self.assertEqual(title, "životinjski")
        self.assertEqual(definition, """## Adjective
živòtīnjskī

* (relational) animal
* (figuratively) animal, beast, like an animal

## Adverb
živòtīnjski

* like an animal; beastly, brutally""")
        self.assertEqual(grammatical_class, "Adjective")
        self.assertEqual(main_definition, "animal")

    def test_uncountable(self):
        line = r"štetnost===Pronunciation===\n* {{IPA|sh|/ʃtêtnoːst/}}\n* {{hyphenation|sh|štet|nost}}\n\n===Noun===\n{{sh-noun|g=f|head=štȅtnōst}}\n\n# {{lb|sh|uncountable}} [[harmfulness]]\n\n====Declension====\n{{sh-decl-noun-unc\n|štetnost\n|štetnosti\n|štetnosti\n|štetnost\n|štetnosti\n|štetnosti\n|štetnosti/štetnošću\n}}"
        (title, definition, grammatical_class, main_definition) = Content._parse(line)
        self.assertEqual(title, "štetnost")
        self.assertEqual(definition, """## Noun
štȅtnōst

* (uncountable) harmfulness

""")
        self.assertEqual(grammatical_class, "Noun")
        self.assertEqual(main_definition, "harmfulness")

if __name__ == '__main__':
    unittest.main()