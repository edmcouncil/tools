from pdf2docx import Converter

pdf_file = '/Users/pawel.garbacz/Library/CloudStorage/OneDrive-MakoLabS.A/idmp/ISO Standards/ISO_TS_19844_2018(en).PDF'
docx_file = '/Users/pawel.garbacz/Library/CloudStorage/OneDrive-MakoLabS.A/idmp/ISO Standards/ISO_TS_19844_2018(en)(en).docx'

# convert pdf to docx
cv = Converter(pdf_file)
cv.convert(docx_file)      # all pages by default
cv.close()