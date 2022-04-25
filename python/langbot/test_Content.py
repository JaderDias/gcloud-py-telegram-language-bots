import unittest
import Content

class TestParse(unittest.TestCase):

    def test_parse(self):
        line = r"opzicht===Pronunciation===\n* {{audio|nl|Nl-opzicht.ogg|Audio}}\n* {{hyphenation|nl|op|zicht}}\n\n===Noun===\n{{nl-noun|n|-en|opzichtje}}\n\n# {{l|en|supervision}}\n# {{l|en|relation}}, {{l|en|regard}}\n#: ''In welk '''opzicht'''?'' - In what regard?\n\n====Derived terms====\n* {{l|nl|opzichter}}\n* {{l|nl|ten opzichte van}}"
        (title, definition, grammatical_class, main_definition) = Content._parse(line)
        self.assertEqual(title, "opzicht")
        self.assertEqual(definition, """## Noun
(opzichtje)

* supervision
* (relation), (regard)
*: ''In welk '''opzicht'''?'' - In what regard?

""")
        self.assertEqual(grammatical_class, "Noun")
        self.assertEqual(main_definition, "supervision")

if __name__ == '__main__':
    unittest.main()