from enum import Enum
class Regex(Enum):
    PROPER_CASE = 0
    CAPS = 1
    LOWER_CASE = 2
    DIGITS = 3
    ALPHABETS = 4
    ALPHANUMERIC = 5
    WHITESPACE = 6
    PUNCT = 7
    CONSTANT = 8
    START_T = 9
    END_T = 10
    SPECIAL_CASE_FOR_DAG_EDGE = 11

regexes = [
    '^[A-Z][a-z]+', # proper_case
    '^[A-Z]+',  # caps
    '^[a-z]+',  # lower case
    '^[0-9]+',  # digitst
    '^[a-zA-Z]+',  # alphabets
    '^[a-zA-Z0-9]+',  #  alphanum
    '^\s+', # whitespace
    '^[\:\.\,\;\'\"\&\*\-\+\=\/\$]+' # punctuation
]

regexes_2 = [
    '[A-Z][a-z]+', # proper_case
    '[A-Z]+',  # caps
    '[a-z]+',  # lower case
    '[0-9]+',  # digitst
    '[a-zA-Z]+',  # alphabets
    '[a-zA-Z0-9]+',  #  alphanum
    '\s+', # whitespace
    '[\:\.\,\;\'\"\&\*\-\+\=\/]+' # punctuation
]

regex_str = [
    "Proper_case",
    "Capitals",
    "Lower case",
    "Digitals",
    "Alphabets",
    "Alphanums",
    "White Space",
    "Punctuation",
    "Constant",
    "Start_Token",
    "End_Token",
    "Very_Special_for_Path"
]