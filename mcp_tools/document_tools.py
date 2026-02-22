"""
MCP-1: Document Tools
---------------------
Tools for reading PDFs and extracting structured data.

Functions:
- read_pdf(file_path): Extract text from PDF (downloads from MinIO first)
- extract_tables(file_path): Extract tables from PDF

Libraries used: PyPDF2, pdfplumber, pymupdf, boto3 (for MinIO)
"""

import logging
import os
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any
import PyPDF2
import pdfplumber
import fitz  # pymupdf
import boto3
from botocore.client import Config
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================
# MINIO DOWNLOAD HELPER
# ============================================

def download_from_minio(file_path: str) -> Optional[str]:
    """
    Downloads a file from MinIO to a temporary local file.

    Args:
        file_path: The path inside MinIO bucket
                   e.g. "company_xxx/supplier_xxx/Resume.pdf"

    Returns:
        Local temp file path if successful, None if failed
    """
    try:
        s3_client = boto3.client(
            "s3",
            endpoint_url=os.getenv("MINIO_ENDPOINT", "http://localhost:9000"),
            aws_access_key_id=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
            aws_secret_access_key=os.getenv("MINIO_SECRET_KEY", "minioadmin"),
            region_name="us-east-1",
            config=Config(signature_version="s3v4"),
        )

        bucket_name = os.getenv("MINIO_BUCKET_NAME", "supplier-documents")

        # Create a temporary file to store the downloaded PDF
        # delete=False means the file won't be deleted when closed
        # We will manually delete it after reading
        suffix = Path(file_path).suffix or ".pdf"
        temp_file = tempfile.NamedTemporaryFile(
            suffix=suffix,
            delete=False
        )
        temp_path = temp_file.name
        temp_file.close()

        # Download from MinIO
        logger.info(f"Downloading from MinIO: {bucket_name}/{file_path}")
        s3_client.download_file(bucket_name, file_path, temp_path)
        logger.info(f"Downloaded to temp file: {temp_path}")

        return temp_path

    except Exception as e:
        logger.error(f"Failed to download from MinIO: {file_path} → {e}")
        return None


def cleanup_temp_file(temp_path: str):
    """
    Deletes a temporary file after we are done reading it.
    """
    try:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
            logger.info(f"Cleaned up temp file: {temp_path}")
    except Exception as e:
        logger.warning(f"Could not delete temp file {temp_path}: {e}")


# ============================================
# READ PDF
# ============================================

def read_pdf(file_path: str) -> Dict[str, Any]:
    """
    Extract text from a PDF file.

    This function:
    1. Downloads the PDF from MinIO to a temp file
    2. Reads the temp file using PyPDF2 (falls back to pymupdf)
    3. Deletes the temp file
    4. Returns extracted text

    Args:
        file_path (str): Path inside MinIO bucket
                         e.g. "company_xxx/supplier_xxx/Resume.pdf"

    Returns:
        Dict containing:
        - 'success' (bool): Whether extraction was successful
        - 'text' (str): Full extracted text
        - 'pages' (List[str]): Text per page
        - 'page_count' (int): Number of pages
        - 'file_name' (str): Name of the file
        - 'error' (str, optional): Error message if failed
    """
    temp_path = None

    try:
        file_name = Path(file_path).name

        # Step 1: Download from MinIO to temp file
        temp_path = download_from_minio(file_path)

        if not temp_path:
            return {
                'success': False,
                'error': f"Could not download file from MinIO: {file_path}",
                'text': '',
                'pages': [],
                'page_count': 0,
                'file_name': file_name
            }

        pdf_path = Path(temp_path)

        # Step 2: Try PyPDF2 first (faster)
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                page_count = len(pdf_reader.pages)

                pages_text = []
                for page_num in range(page_count):
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text() or ""
                    pages_text.append(page_text)

                full_text = "\n\n".join(pages_text)

                logger.info(
                    f"Successfully extracted {page_count} pages "
                    f"from {file_name} using PyPDF2"
                )

                return {
                    'success': True,
                    'text': full_text,
                    'pages': pages_text,
                    'page_count': page_count,
                    'file_name': file_name,
                    'extraction_method': 'PyPDF2'
                }

        except Exception as pypdf_error:
            logger.warning(
                f"PyPDF2 failed for {file_name}, trying pymupdf: {pypdf_error}"
            )

            # Step 3: Fallback to pymupdf
            doc = fitz.open(pdf_path)
            page_count = doc.page_count

            pages_text = []
            for page_num in range(page_count):
                page = doc[page_num]
                page_text = page.get_text()
                pages_text.append(page_text)

            full_text = "\n\n".join(pages_text)
            doc.close()

            logger.info(
                f"Successfully extracted {page_count} pages "
                f"from {file_name} using pymupdf"
            )

            return {
                'success': True,
                'text': full_text,
                'pages': pages_text,
                'page_count': page_count,
                'file_name': file_name,
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

    finally:
        # Step 4: Always clean up temp file, even if an error occurred
        cleanup_temp_file(temp_path)


# ============================================
# EXTRACT TABLES
# ============================================

def extract_tables(
    file_path: str,
    page_numbers: Optional[List[int]] = None
) -> Dict[str, Any]:
    """
    Extract tables from a PDF file.

    Downloads from MinIO first, then extracts tables using pdfplumber.

    Args:
        file_path (str): Path inside MinIO bucket
        page_numbers (List[int], optional): Specific pages (0-indexed).
                                            If None, extracts from all pages.

    Returns:
        Dict containing:
        - 'success' (bool): Whether extraction was successful
        - 'tables' (List): List of tables found
        - 'table_count' (int): Number of tables found
        - 'pages_with_tables' (List[int]): Pages that contain tables
        - 'file_name' (str): Name of the file
        - 'error' (str, optional): Error message if failed
    """
    temp_path = None

    try:
        file_name = Path(file_path).name

        # Download from MinIO first
        temp_path = download_from_minio(file_path)

        if not temp_path:
            return {
                'success': False,
                'error': f"Could not download file from MinIO: {file_path}",
                'tables': [],
                'table_count': 0,
                'pages_with_tables': [],
                'file_name': file_name
            }

        logger.info(f"Extracting tables from: {file_name}")

        all_tables = []
        pages_with_tables = []

        with pdfplumber.open(temp_path) as pdf:
            if page_numbers:
                pages_to_process = [
                    pdf.pages[i] for i in page_numbers
                    if i < len(pdf.pages)
                ]
            else:
                pages_to_process = pdf.pages

            for page_num, page in enumerate(pages_to_process):
                tables_on_page = page.extract_tables()

                if tables_on_page:
                    for table in tables_on_page:
                        cleaned_table = []
                        for row in table:
                            cleaned_row = [
                                cell if cell is not None else ''
                                for cell in row
                            ]
                            cleaned_table.append(cleaned_row)

                        all_tables.append({
                            'page_number': page_num,
                            'table_data': cleaned_table,
                            'row_count': len(cleaned_table),
                            'column_count': (
                                len(cleaned_table[0]) if cleaned_table else 0
                            )
                        })

                        if page_num not in pages_with_tables:
                            pages_with_tables.append(page_num)

        table_count = len(all_tables)
        logger.info(
            f"Extracted {table_count} tables from "
            f"{len(pages_with_tables)} pages in {file_name}"
        )

        return {
            'success': True,
            'tables': all_tables,
            'table_count': table_count,
            'pages_with_tables': pages_with_tables,
            'file_name': file_name
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

    finally:
        cleanup_temp_file(temp_path)