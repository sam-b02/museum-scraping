import re
import json
import os

def clean_data(rawdata):
    museums = []
    pattern = re.compile(
        r'\n(?=\d+[a-zA-Z]?\.\d+\n)'
        r'(.*?)(?:\n(?:Facilities|Amenities):.*?)(?=\n\S|\Z)',
        re.DOTALL | re.MULTILINE
    )

    museums_sections = pattern.findall(rawdata)
    
    for sections in museums_sections:
        lines = sections.splitlines()

        clean_sections = []

        for i in range(1, len(lines)):
            if lines[i] != " ":
                if ":" not in lines[i]:
                    clean_sections[-1] += lines[i]
                else:
                    clean_sections.append(lines[i]) 

        museums.append(clean_sections)

    jsonify(museums)

def jsonify(museums):
    
    count = 0
    json_data = {}

    for section in museums:

        temp_json = {}

        for line in section:

            split = line.split(":", 1)
            
            temp_json[split[0].strip().lower()] = split[1].strip().lower()

        count += 1
        print(count)
        json_data[str(count)] = temp_json
        
    with open(r"output\output.json", "w", encoding="utf-8") as json_file:
        json.dump(json_data, json_file, indent=4, ensure_ascii=False)
    print(f"JSON data successfully dumped")

        


def main():

    with open(r"output\text.txt", "r", encoding="utf-8") as file:
        rawdata = file.read()
    
    clean_data(rawdata)

if __name__ == "__main__":
    main()