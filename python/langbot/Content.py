import Storage
from Logger import logger
import random
import re
import string
import Firestore.Poll

title_matcher = re.compile("^([^=]+)(=.*)$")
main_definition_searcher = re.compile("===([^=]+)===[^#]*# ([^\n]*)", re.DOTALL)
escaped_new_line = re.compile("\\\\n")
undesired_sections = re.compile("====?(?:Conjugation|Declension|Derived terms|Pronunciation)====?[^=]*", re.DOTALL)
quiz_grammatical_classes = re.compile("Adjective|Noun|Verb")
hashtag_search = re.compile("#")
gender_feminine = re.compile(r"{{[^|}]*\|f\|-[^|}]*\|-}}")
gender_masculine = re.compile(r"{{[^|}]*\|m\|-[^|}]*\|-}}")
gender_neuter = re.compile(r"{{[^|}]*\|n\|-[^|}]*\|-}}")
synonym = re.compile(r"\n#: {{syn\|[^}|]*\|([^}|]*)}}")
alternative_spelling = re.compile(r"=\n\{\{[^|}]*\|[^|}]*\|[^|}]*\|([^|}]*)\}\}", re.DOTALL)
preserve_curly_link = re.compile(r"{{(?:lb|gloss)[^}]*[|=]([^|}=]+)}}")
transitive = re.compile(r"{{indtr\|[^}|]*\|([^}])}}")
qualifier_main_definition = re.compile(r"^\((?:(?:ambi|in|)transitive|relational)[^)]*\) ")
remove_curly_link = re.compile(r"{{[^}]*[|=]([^|}=]+)}}")
remove_curly_link_2 = re.compile(r"{{([^|}=]+)}}\n")
square_link_search_1 = re.compile(r"\[\[[^|]*\|([^|\]]*)\]\]")
square_link_search_2 = re.compile(r"\[\[([^|\]]*)\]\]")
h3_search = re.compile(r"===([^=]+)===")
h4_search = re.compile(r"====([^=]+)====")

def _parse(line: str) -> tuple:
    title_match = title_matcher.match(line).groups()
    title = title_match[0]
    definition = title_match[1]
    definition = escaped_new_line.sub("\n", definition)
    definition = undesired_sections.sub("", definition)
    definition = gender_feminine.sub(r"(feminine)", definition)
    definition = gender_masculine.sub(r"(masculine)", definition)
    definition = gender_neuter.sub(r"(neuter)", definition)
    definition = synonym.sub(r"\n# synonym: \1", definition)
    definition = alternative_spelling.sub(r"=\nalternative spelling: \1", definition)
    definition = preserve_curly_link.sub(r"(\1)", definition)
    definition = transitive.sub(r"(transitive with '\1')", definition)
    definition = remove_curly_link.sub(r"\1", definition)
    definition = remove_curly_link_2.sub("", definition)
    definition = square_link_search_1.sub(r"\1", definition)    
    definition = square_link_search_2.sub(r"\1", definition)
    main_definition = main_definition_searcher.search(definition)
    grammatical_class = None
    if main_definition:
        grammatical_class = main_definition.groups()[0]
        main_definition = main_definition.groups()[1]
        main_definition = qualifier_main_definition.sub("", main_definition)
    definition = hashtag_search.sub("*", definition)
    definition = h4_search.sub(r"### \1", definition)
    definition = h3_search.sub(r"## \1", definition)
    return (title, definition, grammatical_class, main_definition)

def get(language: str, subscription: dict) -> str:
    with open(f"/tmp/{language}", "r") as file_obj:
        line_count = 0
        line = file_obj.readline()
        while line:
            if line_count == subscription["publication_count"]:
                (title, definition, grammatical_class, main_definition) = _parse(line)
                return f"{title} ({grammatical_class}) {main_definition}\n\n{definition}"
            line_count += 1
            line = file_obj.readline()
    return None

def get_quiz(
        language: str,
        chat_id: int,
        publication_count: int,
) -> list:
    max_index = max(publication_count, 15000)
    term_index = random.randint(0, max_index)
    if random.random() > .5:
        min_correct_term_index = Firestore.Poll.get_min_correct_term_index(
            language,
            chat_id,
        )
        if min_correct_term_index >= 0:
            term_index = min_correct_term_index
    logger.info(f"term_index {term_index}")
    result = []
    grammatical_class = ""
    with open(f"/tmp/{language}", "r") as file_obj:
        line_count = 0
        line = file_obj.readline()
        while line:
            if line_count >= term_index:
                (title, _, grammatical_class_i, main_definition) = _parse(line)
                if main_definition:
                    if grammatical_class == "" \
                        and quiz_grammatical_classes.match(grammatical_class_i):
                        grammatical_class = grammatical_class_i
                    if grammatical_class == grammatical_class_i:
                        result.append((title, grammatical_class, main_definition, line_count))
                        term_index = line_count + random.randint(2, 10)
                        if len(result) == 3:
                            return result
            line_count += 1
            line = file_obj.readline()
    return None
