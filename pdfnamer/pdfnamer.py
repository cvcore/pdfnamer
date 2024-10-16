import os
import time
import shutil
import re
from datetime import datetime
from PyPDF2 import PdfReader
from pdf2image import convert_from_path
import openai
from PIL import Image
import pytesseract
import logging

# Set your OpenAI API key
openai.api_key = os.environ['OPENAI_API_KEY']

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PDFProcessor:
    def __init__(self, folder_to_watch, output_folder):
        self.folder_to_watch = folder_to_watch
        self.output_folder = output_folder

    def process_pdfs(self):
        while True:
            for file_name in os.listdir(self.folder_to_watch):
                if file_name.endswith('.pdf'):
                    file_path = os.path.join(self.folder_to_watch, file_name)
                    logger.info(f"Processing PDF: {file_path}")
                    self.process_pdf(file_path)
            time.sleep(10)  # Check every 10 seconds

    def process_pdf(self, file_path):
        try:
            text = self.extract_text_from_pdf(file_path)
            title = self.extract_title_from_text(text)
            title = self.sanitize_title(title)

            self.rename_pdf(file_path, title)
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")

    def extract_text_from_pdf(self, pdf_path):
        """Extract text from a PDF.
        - If the PDF contains searchable text, extract it directly.
        - Otherwise, use OCR to extract text from the images.

        Args:
            pdf_path (str): Path to the PDF file.

        Returns:
            str: Extracted text from the PDF.
        """
        text = ""
        try:
            # Step 1: Try to extract text using PyPDF2 (for OCR'ed PDFs)
            with open(pdf_path, 'rb') as f:
                reader = PdfReader(f)
                num_pages = len(reader.pages)

                for page_num in range(num_pages):
                    page = reader.pages[page_num]
                    page_text = page.extract_text()

                    # If any text is found, accumulate it
                    if page_text:
                        text += page_text

            # Step 2: If the extracted text is not found or empty, fallback to OCR
            if not text.strip():
                text = self.run_ocr_on_pdf(pdf_path)

        except Exception as e:
            logger.error(f"Error processing {pdf_path}: {e}")

        logger.debug(f"Extracted text from PDF: {text}")

        return text

    def run_ocr_on_pdf(self, pdf_path):
        """Perform OCR on each page of the PDF and return extracted text."""
        ocr_text = ""
        try:
            # Convert each page of the PDF into an image
            pages = convert_from_path(pdf_path, 300)

            # Run OCR on each page
            for page_num, page_image in enumerate(pages):
                logger.info(f"Running OCR on page {page_num + 1}...")
                page_text = pytesseract.image_to_string(page_image)
                ocr_text += page_text + "\n"

        except Exception as e:
            logger.error(f"Error performing OCR on {pdf_path}: {e}")

        return ocr_text

    def convert_pdf_to_jpg(self, pdf_path):
        # Convert the first page to an image
        pages = convert_from_path(pdf_path, 300, first_page=0, last_page=1)
        output_image_path = pdf_path.replace('.pdf', '.jpg')
        pages[0].save(output_image_path, 'JPEG')
        return output_image_path

    def extract_text_from_image(self, image_path):
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            logger.info(f"Extracted text from image: {text}")
            return text
        except Exception as e:
            logger.error(f"Error extracting text from image: {e}")
            return None


    def extract_title_from_text(self, text):
        prompt = f"The following text is extracted from a scanned letter:\n\n{text}\n\nPlease extract only the title of this letter. No additional description is needed."
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an assistant that extracts specific information from texts."},
                {"role": "user", "content": prompt}
            ]
        )
        return response['choices'][0]['message']['content'].strip()

    def sanitize_title(self, title):
        # Remove unwanted characters from the title
        title = re.sub(r'[^\w\s]', '', title)
        return title.strip().replace(' ', '_')

    def rename_pdf(self, pdf_path, title):
        # Extract the date from the original file name
        base_name = os.path.basename(pdf_path)
        date_match = re.match(r'(\d{8})', base_name)
        if date_match:
            pdf_date = date_match.group(1)
        else:
            pdf_date = datetime.now().strftime('%Y%m%d')

        new_name = f"{pdf_date}-{title}.pdf"

        # Escape any special characters in the title
        new_name = re.sub(r'[<>:"/\\|?*]', '_', new_name)

        new_pdf_path = os.path.join(self.output_folder, new_name)

        # Move and rename the file
        shutil.move(pdf_path, new_pdf_path)
        logger.info(f"Renamed PDF to: {new_pdf_path}")

if __name__ == '__main__':
    folder_to_watch = os.environ['INPUT_FOLDER']
    output_folder = os.environ['OUTPUT_FOLDER']
    pdf_processor = PDFProcessor(folder_to_watch, output_folder)
    pdf_processor.process_pdfs()
