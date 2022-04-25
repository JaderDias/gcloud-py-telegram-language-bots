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
        expected = r"""piar===Verb===\n{{pt-verb|pi|ar}}\n\n# to {{l|en|chirp}} {{gloss|to make a short, sharp sound, as of small birds}}\n# {{lb|pt|by extension}} to {{l|en|chat}}\n#: {{syn|pt|falar}}
remontar===Verb===\n{{pt-verb|remont|ar}}\n\n# to [[remount]]\n# to [[reassemble]]
abater===Pronunciation===\n{{pt-IPA|abatêr}}\n* {{hyphenation|pt|a|ba|ter}}\n\n===Verb===\n{{pt-verb|abat|er}}\n\n# {{lb|pt|intransitive}} to [[collapse]]\n# {{lb|pt|intransitive}} to [[topple]]\n# {{lb|pt|transitive}} to [[slaughter]]\n# {{lb|pt|intransitive}} to [[abate]], [[weaken]]\n# {{lb|pt|transitive}} to [[reduce]]\n# {{pt-verb-form-of|abater}}
"""
        self.assertEqual(actual, expected)

if __name__ == '__main__':
    unittest.main()