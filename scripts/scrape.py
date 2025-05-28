import re
import json

with open(r"output\text.txt", "r", encoding="utf-8") as file:
    rawdata = file.read()

museums = []

museums_sections = re.split(r'\n(?=\d+[a-zA-Z]?\.\d+)', rawdata) #takes the raw data and splits into sections based on the starting character (digit,dot,digit)

