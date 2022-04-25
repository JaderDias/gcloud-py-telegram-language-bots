from copyreg import remove_extension
from curses import flash
from lxml import etree
import io
import re
# import resource # to print memory usage

remove_other_languages = re.compile("\n==[^=].*$", flags=re.DOTALL)
section_splitter = re.compile("===([^\n=]*)===[^=]", flags=re.DOTALL)
skip_sections = re.compile("Alternative forms|Anagrams|Conjugation|Etymology|Further reading|Letter|Prefix|Proper noun|Quotations|References|See also")
undesired_pronunciation = re.compile("\* (?:|{{[a-z]*-[a-z]*}} ){{[a-z]*-IPA(?:|\|pos=[a-z]*)}}[^*]*", flags=re.DOTALL)
verb_form = re.compile(r"{{head\|[^|}]*\|verb form}}")
verb_conjugation = re.compile(r"{{[^}-]*-([^|}]*)\|")
undesired_definitions = re.compile("{{[^|]*(?:alt form|alt sp| of|prefixsee|prefixusex|topics)[|][^}]*}}")
missing_definitions = re.compile(r"{{rfdef\|")
undesired_tags = re.compile("<ref>[^<]*</ref>")
undesired_brackets = re.compile(r"\[\[Category[^\]]*\]\]")
undesired_dashes = re.compile("-+$")
undesired_subsections = re.compile("====(?:Conjugation|Descendants|Quotations|Related terms|See also)====.*", flags=re.DOTALL)

def filter(language: str, allowed_characters: str, file_pointer: io.BufferedIOBase) -> None:
    title = ""
    language_capture_group = re.compile(f"=={language}==(.*)", flags=re.DOTALL)
    allowed_characters = re.compile(f"^[{allowed_characters}]", flags=re.IGNORECASE)
    context = etree.iterparse(file_pointer, events=('end',))
    for _, elem in context:
        if elem.tag != '{http://www.mediawiki.org/xml/export-0.10/}page':
            continue
        for child in elem:
            if child.tag == "{http://www.mediawiki.org/xml/export-0.10/}title":
                title = child.text
                match = re.match(allowed_characters, title)
                if not match:
                    title = ""
                continue
            if title == "":
                continue
            if child.tag != "{http://www.mediawiki.org/xml/export-0.10/}revision":
                continue
            for grandchild in child:
                if grandchild.tag != "{http://www.mediawiki.org/xml/export-0.10/}text":
                    continue
                if not grandchild.text:
                    continue
                match = re.search(language_capture_group, grandchild.text)
                if match:
                    content = remove_other_languages.sub("", match.groups()[0])
                    sections = section_splitter.split(content)
                    result = []
                    pronunciation = ""
                    for i in range(1, len(sections), 2):
                        section_name = sections[i]
                        if section_name == "Pronunciation":
                            pronunciation = undesired_pronunciation.sub("", sections[i+1])
                            continue
                        if skip_sections.match(section_name):
                            continue
                        definition = sections[i+1]
                        if section_name == "Verb":
                            if verb_form.match(definition):
                                continue
                            verb_match = verb_conjugation.match(definition)
                            if verb_match and verb_match.groups()[0] != 'verb':
                                continue
                        if undesired_definitions.search(definition):
                            continue
                        definition = undesired_tags.sub("", definition)
                        definition = undesired_brackets.sub("", definition)
                        definition = undesired_dashes.sub("", definition)
                        definition = undesired_subsections.sub("", definition)
                        result.append(f"==={sections[i]}===\n{definition}")
                    if not result:
                        continue
                    if pronunciation:
                        result.insert(0, f"===Pronunciation===\n{pronunciation}")
                    result = "".join(result).strip()
                    result = result.replace("\n", "\\n")
                    print(f"{title}{result}")
        # memory usage
        #print(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)

        # cleanup
        # first empty children from current element
            # This is not absolutely necessary if you are also deleting siblings,
            # but it will allow you to free memory earlier.
        elem.clear()
        # second, delete previous siblings (records)
        while elem.getprevious() is not None:
            del elem.getparent()[0]
        # make sure you have no references to Element objects outside the loop