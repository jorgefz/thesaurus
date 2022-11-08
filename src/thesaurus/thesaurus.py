
import json
import requests as reqs
import sys
from typing import List


def _fetch_json_from_source(source: str) -> dict:
    """
    Finds and returns the response from the website in json format
    """
    json_str_start = "<script>window.INITIAL_STATE ="
    json_str_end   = """\n;</script>\n      </body>\n    </html>\n"""

    json_idx_start = source.find(json_str_start) + len(json_str_start)
    json_idx_end = len(source) - len(json_str_end) + 1

    if(json_idx_start == -1 or json_idx_end == -1):
        return None

    json_str = source[json_idx_start:json_idx_end]
    json_str = json_str.replace("undefined", "null")
    data = json.loads(json_str)

    return data



def fetch_synonyms(search_term: str) -> List[dict]:
    """
    Requests the synonyms for a given search_term
    and returns a dict object with its definitions
    and synonyms.
    """
    
    url_search = f"https://www.thesaurus.com/browse/{search_term}"
    
    try:
        response = reqs.get(url_search)
    except:
        print("Failed to access thesaurus.com")
        exit(-1)

    if( response.status_code == 200):
        json_response = _fetch_json_from_source(response.text)
        definitions = json_response["searchData"]["tunaApiData"]["posTabs"]
        return definitions, True

    elif( response.status_code == 404 ):
        try:
            json_response = _fetch_json_from_source(response.text)
        except:
            print(f"Failed to access thesaurus.com ({response.status_code})")
            exit(-1)
        suggestions = json_response["searchData"]["spellSuggestionsData"]
        return suggestions, False

    else:
        print(f"Failed to access thesaurus.com ({response.status_code})")
        exit(-1)
    
    return list(), False



