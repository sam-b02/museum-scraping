import pymupdf

doc = pymupdf.open(r"data\museums.pdf") # open a document

out = open("output\text.txt", "wb") 
for x, page in enumerate(doc):
    if x >= 16: 
        text = page.get_text().encode("utf8") 
        out.write(text)
        out.write(bytes((12,)))
out.close()