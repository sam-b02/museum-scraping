import re
import json

def clean_data(rawdata):
    museums = []
    pattern = re.compile(
        r'\n(?=\d+[a-zA-Z]?\.\d+\n)'
        r'(.*?)(?:\n(?:Facilities|Amenities):.*?)(?=\n\S|\Z)',
        re.DOTALL | re.MULTILINE
    )

    museums_sections = pattern.findall(rawdata)
    
    for i in museums_sections:
        lines = i.splitlines()
        museums.append(lines[1:])
    jsonify(museums)


def jsonify(museums):
    for section in museums:
        print("**********************")
        for line in section:
            print(line)
            split = line.split(":", 1)
            print(split)

def main():

    with open(r"output\text.txt", "r", encoding="utf-8") as file:
        rawdata = file.read()
    
    clean_data(rawdata)

if __name__ == "__main__":
    main()