"""
DOCUMENT MANAGEMENT ROUTES

Handles:
- Uploading supplier documents to MinIO
- Storing metadata in PostgreSQL
"""
from botocore.client import Config
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from uuid import UUID
from datetime import datetime
import boto3
import os
from dotenv import load_dotenv

from ..database import get_db
from ..middleware import get_current_user, require_role
from ..models import DocumentUploadResponse

load_dotenv()
router = APIRouter()


# ============================================
# UPLOAD DOCUMENT
# ============================================

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    supplier_id: UUID = Form(...),
    document_type: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(["admin", "analyst"]))
  
):
    """
    Upload a PDF document for a supplier.
    """

    company_id = current_user["company_id"]

    # Verify supplier belongs to company
    supplier = db.execute(
        text("""
            SELECT supplier_id
            FROM suppliers
            WHERE supplier_id = :supplier_id
            AND company_id = :company_id
        """),
        {"supplier_id": supplier_id, "company_id": company_id}
    ).fetchone()

    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )

    # Connect to MinIO
    # Connect to MinIO
    s3_client = boto3.client(
        "s3",
        endpoint_url=os.getenv("MINIO_ENDPOINT", "http://localhost:9000"),
        aws_access_key_id=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
        aws_secret_access_key=os.getenv("MINIO_SECRET_KEY", "minioadmin123"),
        region_name="us-east-1",
        config=Config(signature_version="s3v4"),
    )


    bucket_name = os.getenv("MINIO_BUCKET_NAME", "supplier-documents")

    # Create bucket if it doesn't exist
    existing_buckets = [b["Name"] for b in s3_client.list_buckets()["Buckets"]]

    if bucket_name not in existing_buckets:
        s3_client.create_bucket(Bucket=bucket_name)


    # Create structured file path
    file_path = f"company_{company_id}/supplier_{supplier_id}/{file.filename}"

    # ✅ Calculate file size safely
    file_size = len(await file.read())
    file.file.seek(0)  # Reset pointer after reading

    # Upload file to MinIO
    s3_client.upload_fileobj(file.file, bucket_name, file_path)



    # Insert metadata into PostgreSQL
    result = db.execute(
        text("""
            INSERT INTO documents (
                supplier_id,
                document_type,
                file_name,
                file_path,
                file_size_bytes
            )
            VALUES (
                :supplier_id,
                :document_type,
                :file_name,
                :file_path,
                :file_size_bytes
            )
            RETURNING document_id, file_name, file_path, file_size_bytes, upload_date
        """),
        {
            "supplier_id": supplier_id,
            "document_type": document_type,
            "file_name": file.filename,
            "file_path": file_path,
            "file_size_bytes": file_size
        }
    )

    document = result.fetchone()
    db.commit()

    return DocumentUploadResponse(
        document_id=document.document_id,
        file_name=document.file_name,
        file_path=document.file_path,
        file_size_bytes=document.file_size_bytes,
        uploaded_at=document.upload_date
    )

# ============================================
# GET DOCUMENTS BY SUPPLIER
# ============================================

@router.get("/", )
async def get_documents(
    supplier_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all documents uploaded for a specific supplier.
    
    Purpose:
        After logging back in, user can retrieve all previously
        uploaded document IDs for a supplier.
        These IDs are then used when creating a new evaluation.
    
    Usage:
        GET /api/documents/?supplier_id=your-supplier-uuid
    
    Returns:
        List of documents with their IDs, names, types, and upload dates
    """
    company_id = current_user["company_id"]

    # First verify the supplier belongs to this company
    # (security check — users cannot see other companies' documents)
    supplier = db.execute(
        text("""
            SELECT supplier_id
            FROM suppliers
            WHERE supplier_id = :supplier_id
            AND company_id = :company_id
        """),
        {"supplier_id": supplier_id, "company_id": company_id}
    ).fetchone()

    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found or does not belong to your company"
        )

    # Fetch all documents for this supplier
    documents = db.execute(
        text("""
            SELECT
                document_id,
                document_type,
                file_name,
                file_path,
                file_size_bytes,
                upload_date
            FROM documents
            WHERE supplier_id = :supplier_id
            ORDER BY upload_date DESC
        """),
        {"supplier_id": supplier_id}
    ).fetchall()

    if not documents:
        return {
            "supplier_id": str(supplier_id),
            "total_documents": 0,
            "documents": []
        }

    return {
        "supplier_id": str(supplier_id),
        "total_documents": len(documents),
        "documents": [
            {
                "document_id": str(doc.document_id),
                "document_type": doc.document_type,
                "file_name": doc.file_name,
                "file_size_bytes": doc.file_size_bytes,
                "uploaded_at": doc.upload_date.isoformat() if doc.upload_date else None
            }
            for doc in documents
        ]
    }