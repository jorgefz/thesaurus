
import json
import requests as reqs
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

    print("Definition: ", definition)
    print("Synonyms:")

    fmtsyns = []
    for s in synonyms:
        term = s['term']
        sim = s['similarity']
        if("100" in sim):  color = ansicode(style=FontStyle.BOLD,  color=Color.RED)
        elif("50" in sim): color = ansicode(style=FontStyle.BOLD,  color=Color.YELLOW)
        else:              color = ansicode(style=FontStyle.FAINT, color=Color.GRAY)
        fmtsyns.append( color + term + ansicode() )
        
    ncols = 3
    max_indent = 25

    for i,fs in enumerate(fmtsyns):
        print("".ljust(10) + fs.ljust(max_indent))
    print("\n")



def fetch_synonyms(search_term: str) -> list[dict]:
    
    url_search = f"https://www.thesaurus.com/browse/{search_term}"
    
    try:
        response = reqs.get(url_search)
    except:
        print("Failed to access thesaurus.com")
        exit(-1)

    if(response.status_code != 200):
        # Also offer suggestions if not found
        # "Did you mean..."
        print("Failed to access thesaurus.com")
        exit(-1)

    json_str_search = "<script>window.INITIAL_STATE ="
    json_str_end = """\n;</script>\n      </body>\n    </html>\n"""

    start = response.text.find(json_str_search) + len(json_str_search)
    end = len(response.text) - len(json_str_end) + 1
    
    json_str = response.text[start:end].replace("undefined", "null") 
    data = json.loads(json_str)
    
    definitions = data["searchData"]["tunaApiData"]["posTabs"]

    return definitions



