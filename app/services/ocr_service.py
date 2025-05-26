import os
import logging
import tempfile
from typing import List, Dict, Any
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import io

logger = logging.getLogger(__name__)

class OCRService:
    """
    Service to perform OCR on images and PDFs
    """
    
    @staticmethod
    def extract_text_from_pdf(pdf_path: str) -> str:
        """
        Extract text content from a PDF file using OCR
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            str: Extracted text from the PDF
        """
        try:
            logger.info(f"Processing PDF: {pdf_path}")
            
            # Convert PDF to images
            images = convert_from_path(pdf_path)
            
            # Extract text from each image
            text_content = []
            
            for i, image in enumerate(images):
                logger.info(f"Processing page {i+1}/{len(images)}")
                
                # Extract text from the image using pytesseract
                text = pytesseract.image_to_string(image, lang='eng')
                text_content.append(text)
                
            # Combine text from all pages
            full_text = "\n\n".join(text_content)
            
            logger.info(f"PDF processing complete: extracted {len(full_text)} characters")
            return full_text
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise
    
    @staticmethod
    def extract_text_from_image(image_path: str) -> str:
        """
        Extract text content from an image file using OCR
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            str: Extracted text from the image
        """
        try:
            logger.info(f"Processing image: {image_path}")
            
            # Open the image
            image = Image.open(image_path)
            
            # Extract text from the image using pytesseract
            text = pytesseract.image_to_string(image, lang='eng')
            
            logger.info(f"Image processing complete: extracted {len(text)} characters")
            return text
            
        except Exception as e:
            logger.error(f"Error extracting text from image: {str(e)}")
            raise
    
    @staticmethod
    def extract_text(file_path: str) -> str:
        """
        Extract text content from a file (auto-detects file type)
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            str: Extracted text from the file
        """
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension in ['.pdf']:
            return OCRService.extract_text_from_pdf(file_path)
        elif file_extension in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']:
            return OCRService.extract_text_from_image(file_path)
        else:
            # For other file types, try to read as text
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except UnicodeDecodeError:
                # If not text, try as image
                try:
                    return OCRService.extract_text_from_image(file_path)
                except:
                    logger.error(f"Unsupported file format: {file_extension}")
                    raise ValueError(f"Unsupported file format: {file_extension}")
