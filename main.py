import os
import re
from io import BytesIO
from PyPDF2 import PdfWriter, PdfReader

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase.pdfmetrics import stringWidth

# Folder containing PDFs
USERNAME = "" # Place Username Dynamic Variable
UEI = "" # Place UEI Dynamic Variable
FOLDER_PATH = "C:\Temp\Cody\{USERNAME}\{UEI}"

# DELETE these two lines when done testing # EXAMPLE
TEST_PATH = "/Users/Username/Downloads/Python PDF Testing"
FOLDER_PATH = TEST_PATH
#

file_list = []
merged_pdf_output = FOLDER_PATH + '/merged.pdf'
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
    
    sorted_list = sorted(file_list, key=alphanumeric_key)

    return sorted_list

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
            # Remove file extension
            file_name = os.path.splitext(file_name)[0]
            # Remove excess numbers/symbols from file name & store each word of name into a list element
            title_parts = re.findall(r'[a-zA-Z]+', file_name)
            # Join the returned list items into a string
            title = ' '.join(title_parts)

            # Iterate over titles and increment page numbers to create ToC reference
            # If the file is after 1st header file, adjust page_counter to account for ToC file injection after header page
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
def createTOC(toc_entries):
    # Create a BytesIO object to hold the PDF content
    buffer = BytesIO()

    # Create a new PDF using the BytesIO buffer
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    # Create object to call styles class
    styles = getSampleStyleSheet()

    # Customize the style for the Table of Contents title
    toc_title_style = styles['Heading1']
    toc_title_style.alignment = 1  # Center alignment

    # Create a list to hold the PDF elements for the ToC
    elements = []

    # Create Page Heading and add to elements list
    toc_title = Paragraph("Table of Contents", toc_title_style)
    elements.append(toc_title)

    # Add ToC Entries to list
    toc_data = []
    for page_num, title in toc_entries:
        # Add an empty line as a spacer between entries
        toc_data.append(Spacer(1, 12))  # Adjust the second parameter for spacing

        # Calculate the width of the title in points (1 inch = 72 points)
        title_width = stringWidth(title, 'Helvetica-Bold', 12)  # You can adjust the font and size

        # Calculate the number of dots needed to align the page number
        max_width = 6.5 * inch  # Adjust this based on your page width
        num_dots = int((max_width - title_width) / stringWidth('.', 'Helvetica', 12))  # Assuming dots are '.' characters
        dots = "." * num_dots

        # Format the entry with right-justified page number
        entry = f"<b>{title}</b>{dots}{page_num}"
        # Create a paragraph with customized style for the entry
        entry_paragraph = Paragraph(entry, styles['Normal'])
        
        toc_data.append(entry_paragraph)
       
    elements.extend(toc_data)

    # Build the PDF & Reset the buffer
    doc.build(elements)
    buffer.seek(0)

    # Return BytesIO object containing PDF content
    return buffer

def integrateTOC(merged_pdf_path, final_pdf_path, toc_entries):
    merged_pdf = PdfReader(merged_pdf_path)

    final_pdf = PdfWriter()

    # Add the first page of the merged PDF
    final_pdf.add_page(merged_pdf.pages[0])
    
    # Call the updated createTOC function to get the PDF content
    toc_content = createTOC(toc_entries)

    # Append the ToC pages to the final PDF
    toc_pdf = PdfReader(toc_content)
    final_pdf.append_pages_from_reader(toc_pdf)

    # Add the remaining pages of the merged PDF
    for page in merged_pdf.pages[1:]:
        final_pdf.add_page(page)

    # Add PDF Configurations

    # Add the Table of Contents as entries in the outline (bookmarks)
    toc_outline = final_pdf.add_outline_item("Table of Contents", 1, parent=None, color=None)
    
    for page_num, title in toc_entries:
        final_pdf.add_outline_item(title, page_num-1, parent=toc_outline, color=None)

    final_pdf.page_mode = '/UseOutlines'

    # Write the final PDF file
    with open(final_pdf_path, 'wb') as output_file:
        final_pdf.write(output_file)

if __name__ == "__main__":
    print(f"Reading from {FOLDER_PATH}")
    file_list = getFiles(FOLDER_PATH)
    sorted_file_list = alphanumeric_sort(file_list)

    # Merge the input files into a single PDF
    mergeFiles(merged_pdf_output, sorted_file_list)
    print(f"Merged PDF created: {merged_pdf_output}")

    # Generate table of contents data
    toc_entries = extractTOC(sorted_file_list)

    # Integrate ToC into merged PDF and create final output PDF
    integrateTOC(merged_pdf_output, final_pdf_output, toc_entries)
    print(f"Final PDF created: {final_pdf_output}")