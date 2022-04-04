import Storage
import re

title_matcher = re.compile("^([^=]+)(=.*)$")
escaped_new_line = re.compile("\\\\n")

def get(language: str, subscription: dict) -> str:
    with open(f"/tmp/{language}", "r") as file_obj:
        line_count = 0
        line = file_obj.readline()
        while line:
            if line_count == subscription["publication_count"]:
                title_match = title_matcher.match(line).groups()
                title = title_match[0]
                definition = title_match[1]
                definition = escaped_new_line.sub("\n", definition)
                return f"=={title}==\n\n{definition}"
            line_count += 1
            line = file_obj.readline()
    return None