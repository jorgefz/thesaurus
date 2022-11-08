#!/usr/bin/env python

from thesaurus import thesaurus
import sys


def sanitise_input():

    if(len(sys.argv) < 2):
        print("Usage: thesaurus.py [word or expression]")
        exit(-1)

    search_term = " ".join(sys.argv[1:])

    all_valid_chars = all(c.isalnum() or c.isspace() for c in search_term)

    if(all_valid_chars is False):
        print("Illegal characters found in search term")
        exit(-1)
    
    search_term = search_term.replace(" ", r"%20")
    return search_term


def cli_main():
    search_term = sanitise_input()
    print(f"Search term: '{search_term}'")

    response = thesaurus.fetch_synonyms(search_term)

    for defn in response:
        thesaurus.print_synonyms(defn)



if __name__ == "__main__":
    cli_main()
    exit(0)

