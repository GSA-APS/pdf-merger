import os
import re
from PyPDF2 import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

USERNAME = "" # Place Username Dynamic Variable
UEI = "" # Place UEI Dynamic Variable
FOLDER_PATH = "C:\Temp\Cody\{USERNAME}\{UEI}"

# DELETE these two lines when done testing
TEST_PATH = "/Users/Angel/Downloads/Python PDF Testing"
FOLDER_PATH = TEST_PATH
#

file_list = []
pdf_output = FOLDER_PATH + '/merged.pdf'
toc_pdf_output = FOLDER_PATH + '/toc.pdf'
final_pdf_output = FOLDER_PATH + '/final.pdf'

merger = PdfWriter()

def getFiles(folder_path):
    for file in os.listdir(folder_path):
        true_path = os.path.join(folder_path, file)
        if os.path.isfile(true_path) and file.lower().endswith(".pdf"):  # Exclude non-PDF files
            file_list.append(true_path)  # Append the full file path
    return file_list

def alphanumeric_sort(file_list):
    def alphanumeric_key(file_name):
        # Extracts the numeric part of the file name for sorting
        parts = re.split('([0-9]+)', file_name)
        return [int(part) if part.isdigit() else part for part in parts]
    
    return sorted(file_list, key=alphanumeric_key)

# Merge the input files into a single PDF
def mergeFiles(pdf_output, file_list):
    for file_path in file_list:
        try:
            pdf = PdfReader(file_path)
            for page_num in range(len(pdf.pages)):  # Loop over all pages
                page = pdf.pages[page_num]
                merger.add_page(page)
        except Exception as e:
            print(f"Error reading PDF file: {file_path}\n{e}")
            continue

    with open(pdf_output, 'wb') as output_file:
        merger.write(output_file)

# Extract table of contents from file names and generate continuous page numbers
def extractTOC(file_list):
    table_of_contents = []
    page_counter = 1
    
    for file_path in file_list:
        try:
            pdf = PdfReader(file_path)
            num_pages = len(pdf.pages)
            file_name = os.path.basename(file_path)
            file_name = os.path.splitext(file_name)[0]  # Remove file extension
            file_name = file_name[:-4] if file_name.lower().endswith(".pdf") else file_name  # Remove "pdf" ending
            title_parts = re.findall(r'[a-zA-Z]+', file_name)
            title = ' '.join(title_parts)

            if page_counter > 1:
                table_of_contents.append((page_counter+1, title))
            else:
                table_of_contents.append((page_counter, title))
            page_counter += num_pages
        except Exception as e:
            print(f"Error reading PDF file: {file_path}\n{e}")
            continue
    
    return table_of_contents

# Generate a table of contents PDF
def createTOC(pdf_path, toc_entries):
    toc_canvas = canvas.Canvas(pdf_path, pagesize=letter)
    
    toc_canvas.setFont("Helvetica-Bold", 14)
    toc_canvas.drawString(50, 750, "Table of Contents")
    
    toc_canvas.setFont("Helvetica", 12)
    toc_canvas.setFillColor(colors.blue)
    y = 700
    
    for entry in toc_entries:
        page_num, title = entry
        toc_canvas.setFillColor(colors.blue)
        toc_canvas.drawString(50, y, f"{title} - {page_num}")
        y -= 20
    
    toc_canvas.save()

def integrateTOC(merged_pdf_path, toc_pdf_path, final_pdf_path):
    merged_pdf = PdfReader(merged_pdf_path)
    toc_pdf = PdfReader(toc_pdf_path)

    final_pdf = PdfWriter()

    # Add the first page of the merged PDF
    final_pdf.add_page(merged_pdf.pages[0])
    
    # Add the pages from the ToC PDF
    for page in toc_pdf.pages:
        final_pdf.add_page(page)

    # Add the remaining pages of the merged PDF
    for page in merged_pdf.pages[1:]:
        final_pdf.add_page(page)

    # Write the final PDF file
    with open(final_pdf_path, 'wb') as output_file:
        final_pdf.write(output_file)

if __name__ == "__main__":
    print(f"Reading from {FOLDER_PATH}")
    file_list = getFiles(FOLDER_PATH)
    sorted_file_list = alphanumeric_sort(file_list)
    
    # Merge the input files into a single PDF
    mergeFiles(pdf_output, sorted_file_list)
    print(f"Merged PDF created: {pdf_output}")

    # Generate table of contents
    toc_pdf_path = toc_pdf_output ## redundant?
    toc_entries = extractTOC(sorted_file_list)
    createTOC(toc_pdf_path, toc_entries)
    print(f"Table of Contents PDF created: {toc_pdf_output}")

    # Integrate ToC into merged PDF and create final output PDF
    final_pdf_output = FOLDER_PATH + '/final.pdf'
    integrateTOC(pdf_output, toc_pdf_output, final_pdf_output)
    print(f"Final PDF created: {final_pdf_output}")