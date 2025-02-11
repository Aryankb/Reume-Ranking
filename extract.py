# import fitz  # PyMuPDF

# def parse_pdf(file_path):
#     # Open the PDF file
#     document = fitz.open(file_path)
    
#     # Iterate through each page
    
#     for page_num in range(len(document)):
#         page = document.load_page(page_num)
#         text = page.get_text()
#         print(f"Page {page_num + 1}:\n{text}\n")
    

# if __name__ == "__main__":
#     pdf_path = "/path/to/your/pdf_file.pdf"
#     parse_pdf(pdf_path)

from PyPDF2 import PdfReader

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF file.

    Args:
        pdf_path (str): Path to the PDF file.

    Returns:
        str: Extracted text from the PDF.
    """
    # Load the PDF file
    reader = PdfReader(pdf_path)
    
    # Extract text
    extracted_text = ""
    for page in reader.pages:
        extracted_text += page.extract_text()
    
    return extracted_text

if __name__=="__main__":
    # Example Usage
    pdf_path = "/home/aryan/Resume-2/Resumes/Vandit_tyagi_resume_latest1.pdf"  # Replace with the path to your PDF file
    extracted_text = extract_text_from_pdf(pdf_path)
    print(extracted_text)













