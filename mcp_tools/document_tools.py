"""
MCP-1: Document Tools
---------------------
Tools for reading PDFs and extracting structured data.

Functions:
- read_pdf(file_path): Extract text from PDF
- extract_tables(file_path): Extract tables from PDF

Libraries used: PyPDF2, pdfplumber, pymupdf
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import PyPDF2
import pdfplumber
import fitz  # pymupdf

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def read_pdf(file_path: str) -> Dict[str, Any]:
    """
    Extract text from a PDF file.
    
    This function reads a PDF and extracts all text content page by page.
    It uses PyPDF2 for text extraction and falls back to pymupdf if PyPDF2 fails.
    
    Args:
        file_path (str): Path to the PDF file
        
    Returns:
        Dict containing:
        - 'success' (bool): Whether extraction was successful
        - 'text' (str): Full extracted text
        - 'pages' (List[str]): Text per page
        - 'page_count' (int): Number of pages
        - 'file_name' (str): Name of the file
        - 'error' (str, optional): Error message if failed
        
    Example:
        >>> result = read_pdf("data/raw_documents/guide_to_exporting.pdf")
        >>> print(result['page_count'])
        45
        >>> print(result['text'][:200])
        "Guide to Exporting... [first 200 characters]"
    """
    try:
        # Convert to Path object for easier handling
        pdf_path = Path(file_path)
        
        # Check if file exists
        if not pdf_path.exists():
            logger.error(f"PDF file not found: {file_path}")
            return {
                'success': False,
                'error': f"File not found: {file_path}",
                'text': '',
                'pages': [],
                'page_count': 0,
                'file_name': pdf_path.name
            }
        
        logger.info(f"Reading PDF: {pdf_path.name}")
        
        # Try PyPDF2 first (faster)
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                page_count = len(pdf_reader.pages)
                
                # Extract text from each page
                pages_text = []
                for page_num in range(page_count):
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    pages_text.append(page_text)
                
                full_text = "\n\n".join(pages_text)
                
                logger.info(f"Successfully extracted {page_count} pages using PyPDF2")
                
                return {
                    'success': True,
                    'text': full_text,
                    'pages': pages_text,
                    'page_count': page_count,
                    'file_name': pdf_path.name,
                    'extraction_method': 'PyPDF2'
                }
                
        except Exception as pypdf_error:
            logger.warning(f"PyPDF2 failed, trying pymupdf: {pypdf_error}")
            
            # Fallback to pymupdf (more robust)
            doc = fitz.open(pdf_path)
            page_count = doc.page_count
            
            pages_text = []
            for page_num in range(page_count):
                page = doc[page_num]
                page_text = page.get_text()
                pages_text.append(page_text)
            
            full_text = "\n\n".join(pages_text)
            doc.close()
            
            logger.info(f"Successfully extracted {page_count} pages using pymupdf")
            
            return {
                'success': True,
                'text': full_text,
                'pages': pages_text,
                'page_count': page_count,
                'file_name': pdf_path.name,
                'extraction_method': 'pymupdf'
            }
    
    except Exception as e:
        logger.error(f"Failed to read PDF {file_path}: {e}")
        return {
            'success': False,
            'error': str(e),
            'text': '',
            'pages': [],
            'page_count': 0,
            'file_name': Path(file_path).name
        }


def extract_tables(file_path: str, page_numbers: Optional[List[int]] = None) -> Dict[str, Any]:
    """
    Extract tables from a PDF file.
    
    This function uses pdfplumber to extract tables from PDF pages.
    It's particularly useful for financial statements, invoices, and structured data.
    
    Args:
        file_path (str): Path to the PDF file
        page_numbers (List[int], optional): Specific pages to extract from (0-indexed).
                                           If None, extracts from all pages.
        
    Returns:
        Dict containing:
        - 'success' (bool): Whether extraction was successful
        - 'tables' (List[List[List]]): List of tables (each table is a list of rows)
        - 'table_count' (int): Number of tables found
        - 'pages_with_tables' (List[int]): Page numbers that contain tables
        - 'file_name' (str): Name of the file
        - 'error' (str, optional): Error message if failed
        
    Example:
        >>> result = extract_tables("supplier_invoice.pdf")
        >>> print(f"Found {result['table_count']} tables")
        >>> print(result['tables'][0])  # First table
        [['Item', 'Quantity', 'Price'], ['Widget A', '100', '$50.00'], ...]
    """
    try:
        # Convert to Path object
        pdf_path = Path(file_path)
        
        # Check if file exists
        if not pdf_path.exists():
            logger.error(f"PDF file not found: {file_path}")
            return {
                'success': False,
                'error': f"File not found: {file_path}",
                'tables': [],
                'table_count': 0,
                'pages_with_tables': [],
                'file_name': pdf_path.name
            }
        
        logger.info(f"Extracting tables from PDF: {pdf_path.name}")
        
        all_tables = []
        pages_with_tables = []
        
        with pdfplumber.open(pdf_path) as pdf:
            # Determine which pages to process
            if page_numbers:
                pages_to_process = [pdf.pages[i] for i in page_numbers if i < len(pdf.pages)]
            else:
                pages_to_process = pdf.pages
            
            # Extract tables from each page
            for page_num, page in enumerate(pages_to_process):
                tables_on_page = page.extract_tables()
                
                if tables_on_page:
                    for table in tables_on_page:
                        # Clean the table (remove None values)
                        cleaned_table = []
                        for row in table:
                            cleaned_row = [cell if cell is not None else '' for cell in row]
                            cleaned_table.append(cleaned_row)
                        
                        all_tables.append({
                            'page_number': page_num,
                            'table_data': cleaned_table,
                            'row_count': len(cleaned_table),
                            'column_count': len(cleaned_table[0]) if cleaned_table else 0
                        })
                        
                        if page_num not in pages_with_tables:
                            pages_with_tables.append(page_num)
        
        table_count = len(all_tables)
        
        logger.info(f"Successfully extracted {table_count} tables from {len(pages_with_tables)} pages")
        
        return {
            'success': True,
            'tables': all_tables,
            'table_count': table_count,
            'pages_with_tables': pages_with_tables,
            'file_name': pdf_path.name
        }
    
    except Exception as e:
        logger.error(f"Failed to extract tables from {file_path}: {e}")
        return {
            'success': False,
            'error': str(e),
            'tables': [],
            'table_count': 0,
            'pages_with_tables': [],
            'file_name': Path(file_path).name
        }


# Test function (only runs when this file is executed directly)
if __name__ == "__main__":
    print("=" * 80)
    print("TESTING MCP-1: DOCUMENT TOOLS")
    print("=" * 80)
    
    # Test 1: Read a PDF
    print("\n[TEST 1] Reading PDF...")
    test_pdf = "data/raw_documents/guide_to_exporting.pdf"
    result = read_pdf(test_pdf)
    
    if result['success']:
        print(f"✅ Success!")
        print(f"   File: {result['file_name']}")
        print(f"   Pages: {result['page_count']}")
        print(f"   Text length: {len(result['text'])} characters")
        print(f"   First 200 chars: {result['text'][:200]}...")
    else:
        print(f"❌ Failed: {result['error']}")
    
    # Test 2: Extract tables
    print("\n[TEST 2] Extracting tables...")
    result_tables = extract_tables(test_pdf)
    
    if result_tables['success']:
        print(f"✅ Success!")
        print(f"   File: {result_tables['file_name']}")
        print(f"   Tables found: {result_tables['table_count']}")
        print(f"   Pages with tables: {result_tables['pages_with_tables']}")
        
        if result_tables['table_count'] > 0:
            first_table = result_tables['tables'][0]
            print(f"\n   First table preview:")
            print(f"   - Page: {first_table['page_number']}")
            print(f"   - Rows: {first_table['row_count']}")
            print(f"   - Columns: {first_table['column_count']}")
            print(f"   - First row: {first_table['table_data'][0]}")
    else:
        print(f"❌ Failed: {result_tables['error']}")
    
    print("\n" + "=" * 80)
    print("DOCUMENT TOOLS TEST COMPLETE")
    print("=" * 80)