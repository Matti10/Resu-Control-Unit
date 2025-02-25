import re
import os


def find_endpoints_inFrontend(frontEndPath):

    matches = []

    ignores = [
        "/json"
    ]

    endpoint_selection_patterns = {
        "test": re.compile(r'/([^"\']+)["\']')
    }


    files = [f for f in os.listdir(frontEndPath) if f.endswith('.html') or f.endswith('.js')]

    for file in files:
        with open(f"{frontEndPath}/{file}", "r") as f:
            for line in f:
                for key,pattern in endpoint_selection_patterns.items():
                    search = pattern.search(line)
                    if None != search:
                        result = search.group(0).replace('"','').replace("'","")
                        if "//" not in result and result not in ignores:
                            print(result)
                            matches.append(result)

    return matches


