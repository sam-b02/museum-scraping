import re
import json

def clean_data(rawdata):
    museums = []

    museums_sections = re.split(r'\n(?=\d+[a-zA-Z]?\.\d+)', rawdata) #takes the raw data and splits into sections based on the starting character (digit,dot,digit)

    for i in museums_sections:
        print(i)
        
def main():

    with open(r"output\text.txt", "r", encoding="utf-8") as file:
        rawdata = file.read()
    
    clean_data(rawdata)

if __name__ == "__main__":
    main()