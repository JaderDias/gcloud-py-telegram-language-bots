import Filter
import bz2
import sys

language = sys.argv[1]
allowed_characters = sys.argv[2]
with bz2.open(sys.argv[3], "rb") as file_pointer:
    Filter.filter(language, allowed_characters, file_pointer)