#!/usr/bin/env python

from thesaurus import thesaurus
import sys

class Color:
    """ ANSI color codes """
    BLACK =  "30"
    RED =    "31"
    GREEN =  "32"
    YELLOW = "33"
    BLUE =   "34"
    PURPLE = "35"
    CYAN =   "36"
    GRAY =   "37"
    NONE =   "0"

class FontStyle:
    BOLD = "1"
    FAINT = "2"
    ITALIC = "3"
    UNDERLINE = "4"
    BLINK = "5"
    NEGATIVE = "7"
    CROSSED = "9"
    NONE = "0"


def ansicode(style :str = FontStyle.NONE, color :str = Color.NONE) -> str:
    """
    Returns ANSI code with defined font style and color.
    Example: ansicode(FontStyle.BOLD, Colors.RED) -> "\\033[1;31m"
    """
    return f"\033[{style};{color}m"


def print_synonyms(defn):

    definition = defn["definition"]
    synonyms = defn["synonyms"]
    
    # Formatting based on level of similarity
    formats = {}
    formats["100"] = ansicode(style=FontStyle.BOLD,  color=Color.RED)
    formats["50"]  = ansicode(style=FontStyle.BOLD,  color=Color.YELLOW)
    default_fmt = ansicode(style=FontStyle.FAINT, color=Color.GRAY)
    end_fmt = ansicode()

    print("Definition: ", definition)
    print("Synonyms:")

    for s in synonyms:
        term = s['term']
        sim = s['similarity']
        color = formats.get(sim, default_fmt)
        print(" "*10 + color + term + end_fmt)
    print(" ")


def sanitise_input():

    if(len(sys.argv) < 2):
        print("Usage:\n\t $ thesaurus [word or expression]")
        exit(-1)

    search_term = " ".join(sys.argv[1:])

    all_valid_chars = all(c.isalnum() or c.isspace() or c == '-' for c in search_term)

    if(all_valid_chars is False):
        print("Illegal characters found in search term")
        exit(-1)
    
    search_fmt = search_term.replace(" ", r"%20")
    return search_term, search_fmt


def cli_main():
    search_term, search_fmt = sanitise_input()

    fmt_relevant = ansicode(FontStyle.UNDERLINE, Color.GREEN)
    fmt_not_found = ansicode(FontStyle.BOLD, Color.YELLOW)
    fmt_end = ansicode()
    max_suggestions = 10

    print("")
    print(f"Search term: '{fmt_relevant + search_term + fmt_end}'", end="\n\n")
    
    word_list, term_found = thesaurus.fetch_synonyms(search_fmt)

    if term_found is True:
        for defn in word_list:
            print_synonyms(defn)
    
    else: # Suggest alternate spellings
        print(f"{fmt_not_found}No results for '{search_term}'{fmt_end}")
        print("Did you mean...")
        for i,suggestion in enumerate(word_list):
            if (i +1 == max_suggestions):
                break
            # First suggestion is most relevant
            if (i==0):
                print("\t" + fmt_relevant + suggestion['term'] + fmt_end)
            else:
                print("\t" + suggestion['term'])
        print("")



if __name__ == "__main__":
    cli_main()
    exit(0)

