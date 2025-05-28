import re
import json

with open(r"output\text.txt", "r", encoding="utf-8") as file:
    rawdata = file.read()
    