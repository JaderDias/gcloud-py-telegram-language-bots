import unittest

import io
from contextlib import redirect_stdout
import Filter

class TestFilter(unittest.TestCase):
    def test_pt_verb(self):
        actual = ""
        with open("test_sample.xml", "rb") as file_pointer,\
                io.StringIO() as buf,\
                redirect_stdout(buf):
            Filter.filter("Portuguese", "A-Zãáàâçéêíõóôúü", file_pointer)
            actual = buf.getvalue()
        print(actual)
        expected = r"""LED===Pronunciation===\n{{pt-IPA|pt=léd(e)}}\n* {{a|Brazil}} {{IPA|pt|/ˈlɛd͡ʒ/}}\n\n===Noun===\n{{pt-noun|m|s}}\n\n# {{l|en|LED}} {{gloss|light-emitting diode}}\n#: {{syn|pt|díodo emissor de luz}}
piar===Verb===\n{{pt-verb|pi|ar}}\n\n# to {{l|en|chirp}} {{gloss|to make a short, sharp sound, as of small birds}}\n# {{lb|pt|by extension}} to {{l|en|chat}}\n#: {{syn|pt|falar}}
remontar===Verb===\n{{pt-verb|remont|ar}}\n\n# to [[remount]]\n# to [[reassemble]]
abater===Pronunciation===\n{{pt-IPA|abatêr}}\n* {{hyphenation|pt|a|ba|ter}}\n\n===Verb===\n{{pt-verb|abat|er}}\n\n# {{lb|pt|intransitive}} to [[collapse]]\n# {{lb|pt|intransitive}} to [[topple]]\n# {{lb|pt|transitive}} to [[slaughter]]\n# {{lb|pt|intransitive}} to [[abate]], [[weaken]]\n# {{lb|pt|transitive}} to [[reduce]]\n# {{pt-verb-form-of|abater}}
"""
        self.assertEqual(actual, expected)
        
    def test_sh_dated(self):
        self.maxDiff = None
        actual = ""
        with open("test_sample.xml", "rb") as file_pointer,\
                io.StringIO() as buf,\
                redirect_stdout(buf):
            Filter.filter("Serbo-Croatian", "A-ZÁČĆĐÍĽŇÔŠŤÚÝŽ", file_pointer)
            actual = buf.getvalue()
        print(actual)
        expected = r"""drug===Pronunciation===\n* {{IPA|sh|/drûːɡ/}}\n\n===Noun===\n{{sh-noun|g=m|head=drȗg}}\n\n# {{lb|sh|Bosnia|Serbia|Montenegro}} [[friend]]\n\n====Declension====\n{{sh-decl-noun\n|drȗg|drȕgovi / drȗzi\n|druga|drugova / druga\n|drugu|drugovima / druzima\n|druga|drugove / druge\n|drȗže|drugovi / druzi\n|drugu|drugovima / druzima\n|drugom|drugovima / druzima\n}}\n\n====Synonyms====\n* {{l|sh|prijatelj}}\n* {{l|sh|drugar}}\n* {{l|sh|frend}} {{qualifier|slang|Croatia}}\n\n====Derived terms====\n{{top2}}\n* {{l|sh|drúga}}\n* {{l|sh|drùgār}}\n* {{l|sh|drugòvati}}\n* {{l|sh|drùškan}}\n* {{l|sh|drúštven}}\n* {{l|sh|drúštvo}}\n* {{l|sh|društvoslovlje}}\n* {{l|sh|drùžba}}\n{{mid2}}\n* {{l|sh|drȕžbenīk}}\n* {{l|sh|druželjùbiv}}\n* {{l|sh|druželjùbivo}}\n* {{l|sh|druželjùbivost}}\n* {{l|sh|drùžica}}\n* {{l|sh|drùžina}}\n* {{l|sh|drúžiti}}\n{{bottom}}
"""
        self.assertEqual(actual, expected)

if __name__ == '__main__':
    unittest.main()