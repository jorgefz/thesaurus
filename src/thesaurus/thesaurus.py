
import sys
import json
import requests as reqs
import bs4
import argparse

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

class Error:
    NONE = "Success"
    CONNECTION_FAILED = "Could not connect to thesaurus.com"
    WORD_NOT_FOUND = "No matching words found"


class Thesaurus:

    
    @staticmethod
    def _ansicode(style :str = FontStyle.NONE, color :str = Color.NONE) -> str:
        """
        Returns ANSI code with defined font style and color.
        Example: ansicode(FontStyle.BOLD, Colors.RED) -> "\\033[1;31m"
        """
        return f"\033[{style};{color}m"

    _formats :dict = {
        100:        _ansicode(style=FontStyle.BOLD,  color=Color.RED),
        50 :        _ansicode(style=FontStyle.BOLD,  color=Color.YELLOW),
        10 :        _ansicode(style=FontStyle.FAINT, color=Color.GRAY),
        'bold':     _ansicode(style=FontStyle.BOLD, color=Color.CYAN),
        'relevant': _ansicode(FontStyle.UNDERLINE, Color.GREEN),
        'end':      _ansicode()
    }


    def __init__(self, search_term :str):
        self.search_term :str  = search_term
        self.url         :str  = f"https://thesaurus.com/browse/{self.search_term}"
        self.definitions :dict = {}
        self.suggestions :list = []
        self.error       :str  = ""

    def fetch_definitions(self) -> tuple[dict,Error]:
        """
        Retrieve list of synonyms and antonyms for a word
        from thesaurus.com
        """
        response = reqs.get(self.url)

        if response.status_code not in [200, 404]:
            self.error = Error.CONNECTION_FAILED
            return {}, self.error

        soup = bs4.BeautifulSoup(response.text, features="lxml")
        str_payload = soup.find(id = 'preloaded-state').string[40:]
        json_response = json.loads(str_payload)    

        if(response.status_code == 404):
            self.error = Error.WORD_NOT_FOUND
            self.suggestions = json_response['luna']['spellSuggestions']['data']['luna']
            return {'suggestions': self.suggestions}, self.error

        entries = json_response['lexigraph']['thesaurusData']['data']['slugs'][0]['entries']
        
        word_data = list(filter(lambda item: 'partOfSpeechGroups' in item, entries))[0]
        word_classes = word_data['partOfSpeechGroups']

        for wclass in word_classes:
            wclass_name = wclass['partOfSpeech']
            syns_ants = wclass['shortDefinitions']

            for sa in syns_ants:
                short_def = sa['shortDef']
                syns = {syn['targetWord']:abs(syn['similarity'])  for syn in sa['synonyms'] }
                ants = {ant['targetWord']:abs(ant['similarity'])  for ant in sa['antonyms'] }
                self.definitions[wclass_name] = {
                    'definition':short_def,
                    'synonyms':syns,
                    'antonyms':ants
                }

        self.error = Error.NONE
        return self.definitions, self.error


    def print_suggestions(self, max_words :int = 5) -> None:
        if(not self.suggestions):
            return

        fmt = Thesaurus._formats

        print("Did you mean ...")
        for i,s in enumerate(self.suggestions):
            if i >= max_words:
                return
            print(f"  {fmt['relevant'] + s + fmt['end']}")


    def print_definitions(self, max_words :int = 5) -> None:
        """
        Prints synonyms and antonyms to console,
        prettyfied with ANSI fonts and colors.

        Parameters
        ----------
            max_words: Max number of synonyms or antonyms to print for a given definition.
        """
        if self.definitions is None:
            return

        formats = Thesaurus._formats

        print(f"\nSearch term: {formats['relevant'] + self.search_term + formats['end']}\n")

        for wclass,data in self.definitions.items():
            print(f"  ({formats['bold'] + wclass + formats['end']}) {data['definition']}\n")

            syns = data['synonyms']
            ants = data['antonyms']
            
            print(f"    Synonyms: ", end='')
            for i in range(min(len(syns), max_words)):
                word = list(syns.keys())[i]
                sim = syns[word]
                print(f"{formats[sim] + word + formats['end']}, ", end='')
            print("")

            print(f"    Antonyms: ", end='')
            for i in range(min(len(ants), max_words)):
                word = list(ants.keys())[i]
                sim = ants[word]
                print(f"{formats[sim] + word + formats['end']}, ", end='')
            print("\n")


def cli_main():
    
    parser = argparse.ArgumentParser(
        prog = 'thesaurus',
        description = 'Fetch synonyms and antonyms from thesaurus.com',
        epilog = 'Author: Jorge Fernandez. Check out the source code at github.com/jorgefz/thesaurus'
    )

    parser.add_argument('words', nargs='+')
    parser.add_argument('-m', '--max-words', type=int, default=5)

    args = parser.parse_args()
    words = args.words
    max_words = args.max_words
    search_term = ' '.join(words)
    
    th = Thesaurus(search_term)
    data, err = th.fetch_definitions()
    
    match err:
        case Error.NONE:
            th.print_definitions(max_words)
            
        case Error.WORD_NOT_FOUND:
            print(err)
            th.print_suggestions(max_words)
            
        case Error.CONNECTION_FAILED:
            print(err)
            

if __name__ == "__main__":
    cli_main()
