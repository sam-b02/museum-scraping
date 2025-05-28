import pymupdf

#this is a document to scrape the raw text from the pdf and dump it into a text file

doc = pymupdf.open(r"data\museums.pdf")

out = open(r"output\text.txt", "wb") 
for x, page in enumerate(doc):
    if x >= 16 and x <= 796: 
        text = page.get_text().encode("utf8") 
        out.write(text)
        out.write(bytes((12,)))
out.close()