import requests

query_url = "https://api.openalex.org/concepts"

page_number = 1
next_page = True
with open("../front/res/concepts.csv","w") as concepts_file:
    concepts_file.write(f"concept_name,concept_id")
    while next_page:
        query_param = {
            'page':page_number,
            'filter':"level:0|1"
        }
        r = requests.get(query_url,params=query_param)
        if r.status_code == 200:
            r_json = r.json()
            if not r_json["results"]:
                next_page = False
            else:
                for concept in r_json["results"]:
                    concept_name = concept["display_name"]
                    concept_id = concept['id']
                    concept_id = concept_id.replace("https://openalex.org/","")
                    
                    concepts_file.write(f"\n{concept_name},{concept_id}")
                page_number += 1