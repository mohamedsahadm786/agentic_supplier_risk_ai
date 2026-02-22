"""
ADMIN ANALYTICS ENDPOINTS

Purpose:
    Give the product owner (admin) a complete view of:
    - Total system usage (tokens, costs, evaluations)
    - Per company usage breakdown
    - Monthly cost trends
    - Most expensive evaluations

Who can access:
    ONLY users with role = "admin"
    Analysts and viewers are blocked

Data source:
    - usage_tracking table (token + cost data per agent per evaluation)
    - evaluations table (evaluation counts, status, risk levels)
    - companies table (company names)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..database import get_db
from ..middleware import require_role

router = APIRouter()


# ============================================
# 1. USAGE SUMMARY
# ============================================

@router.get("/usage-summary")
async def get_usage_summary(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(["super_admin"]))
):
    """
    Overall system usage summary.

    Returns:
        - Total evaluations ever created
        - Total evaluations this month
        - Total tokens used (all time)
        - Total cost in USD (all time)
        - Total cost this month
        - Average cost per evaluation
    """

    # Total evaluations all time
    total_evaluations = db.execute(
        text("SELECT COUNT(*) FROM evaluations")
    ).scalar()

    # Total evaluations this month
    evaluations_this_month = db.execute(
        text("""
            SELECT COUNT(*)
            FROM evaluations
            WHERE DATE_TRUNC('month', created_at) = DATE_TRUNC('month', CURRENT_DATE)
        """)
    ).scalar()

    # Total tokens and cost from usage_tracking
    usage_totals = db.execute(
        text("""
            SELECT
                COALESCE(SUM(total_tokens), 0)   AS total_tokens,
                COALESCE(SUM(total_cost), 0.0)   AS total_cost_usd
            FROM usage_tracking
        """)
    ).fetchone()

    # Cost this month
    cost_this_month = db.execute(
        text("""
            SELECT COALESCE(SUM(total_cost), 0.0)
            FROM usage_tracking
            WHERE DATE_TRUNC('month', created_at) = DATE_TRUNC('month', CURRENT_DATE)
        """)
    ).scalar()

    # Average cost per evaluation
    avg_cost = float(usage_totals.total_cost_usd) / total_evaluations if total_evaluations > 0 else 0.0

    return {
        "summary": {
            "total_evaluations_all_time": total_evaluations,
            "total_evaluations_this_month": evaluations_this_month,
            "total_tokens_used": int(usage_totals.total_tokens),
            "total_cost_usd_all_time": round(float(usage_totals.total_cost_usd), 6),
            "total_cost_usd_this_month": round(float(cost_this_month), 6),
            "average_cost_per_evaluation_usd": round(avg_cost, 6)
        }
    }


# ============================================
# 2. COMPANY USAGE BREAKDOWN
# ============================================

@router.get("/company-usage")
async def get_company_usage(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(["super_admin"]))
):
    """
    Per company usage breakdown.

    Returns:
        For each company:
        - Company name
        - Total evaluations
        - Total tokens used
        - Total cost in USD
    """

    results = db.execute(
        text("""
            SELECT
                c.company_name,
                c.subscription_tier,
                COUNT(DISTINCT e.evaluation_id)     AS total_evaluations,
                COALESCE(SUM(ut.total_tokens), 0)   AS total_tokens,
                COALESCE(SUM(ut.total_cost), 0.0)   AS total_cost_usd
            FROM companies c
            LEFT JOIN evaluations e ON e.company_id = c.company_id
            LEFT JOIN usage_tracking ut ON ut.company_id = c.company_id
            GROUP BY c.company_id, c.company_name, c.subscription_tier
            ORDER BY total_cost_usd DESC
        """)
    ).fetchall()

    return {
        "companies": [
            {
                "company_name": row.company_name,
                "subscription_tier": row.subscription_tier,
                "total_evaluations": row.total_evaluations,
                "total_tokens_used": int(row.total_tokens),
                "total_cost_usd": round(float(row.total_cost_usd), 6)
            }
            for row in results
        ]
    }


# ============================================
# 3. MONTHLY COST TREND
# ============================================

@router.get("/monthly-cost")
async def get_monthly_cost(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(["super_admin"]))
):
    """
    Month by month cost breakdown.

    Returns:
        For each month (last 12 months):
        - Year and month
        - Total evaluations that month
        - Total tokens used that month
        - Total cost that month
    """

    results = db.execute(
        text("""
            SELECT
                TO_CHAR(DATE_TRUNC('month', ut.created_at), 'YYYY-MM') AS month,
                COUNT(DISTINCT ut.evaluation_id)                        AS total_evaluations,
                COALESCE(SUM(ut.total_tokens), 0)                      AS total_tokens,
                COALESCE(SUM(ut.total_cost), 0.0)                      AS total_cost_usd
            FROM usage_tracking ut
            WHERE ut.created_at >= NOW() - INTERVAL '12 months'
            GROUP BY DATE_TRUNC('month', ut.created_at)
            ORDER BY DATE_TRUNC('month', ut.created_at) DESC
        """)
    ).fetchall()

    return {
        "monthly_cost_trend": [
            {
                "month": row.month,
                "total_evaluations": row.total_evaluations,
                "total_tokens_used": int(row.total_tokens),
                "total_cost_usd": round(float(row.total_cost_usd), 6)
            }
            for row in results
        ]
    }


# ============================================
# 4. TOP EXPENSIVE EVALUATIONS
# ============================================

@router.get("/top-expensive-evaluations")
async def get_top_expensive_evaluations(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(["super_admin"]))
):
    """
    Most expensive evaluations by total OpenAI cost.

    Returns:
        Top N evaluations with:
        - Evaluation ID
        - Supplier name
        - Company name
        - Risk level result
        - Total tokens used
        - Total cost
        - Date created
    """

    results = db.execute(
        text("""
            SELECT
                e.evaluation_id,
                s.supplier_name,
                c.company_name,
                e.risk_level,
                e.status,
                COALESCE(SUM(ut.total_tokens), 0)  AS total_tokens,
                COALESCE(SUM(ut.total_cost), 0.0)  AS total_cost_usd,
                e.created_at
            FROM evaluations e
            JOIN suppliers s ON s.supplier_id = e.supplier_id
            JOIN companies c ON c.company_id = e.company_id
            LEFT JOIN usage_tracking ut ON ut.evaluation_id = e.evaluation_id
            GROUP BY
                e.evaluation_id,
                s.supplier_name,
                c.company_name,
                e.risk_level,
                e.status,
                e.created_at
            ORDER BY total_cost_usd DESC
            LIMIT :limit
        """),
        {"limit": limit}
    ).fetchall()

    return {
        "top_expensive_evaluations": [
            {
                "evaluation_id": str(row.evaluation_id),
                "supplier_name": row.supplier_name,
                "company_name": row.company_name,
                "risk_level": row.risk_level,
                "status": row.status,
                "total_tokens_used": int(row.total_tokens),
                "total_cost_usd": round(float(row.total_cost_usd), 6),
                "created_at": row.created_at.isoformat() if row.created_at else None
            }
            for row in results
        ]
    }

# ============================================
# 5. LIST ALL COMPANIES
# ============================================

@router.get("/companies")
async def list_all_companies(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(["super_admin"]))
):
    """
    List all companies registered in the SaaS platform.

    Purpose:
        Before deactivating or deleting a company, you need to
        see all companies and their IDs first.

    Returns:
        - company_id (use this for deactivate/delete actions)
        - company_name
        - subscription_tier
        - is_active status
        - total users in that company
        - created date
    """

    results = db.execute(
        text("""
            SELECT
                c.company_id,
                c.company_name,
                c.subscription_tier,
                c.is_active,
                c.created_at,
                COUNT(u.user_id) AS total_users
            FROM companies c
            LEFT JOIN users u ON u.company_id = c.company_id
            GROUP BY c.company_id, c.company_name, c.subscription_tier,
                     c.is_active, c.created_at
            ORDER BY c.created_at DESC
        """)
    ).fetchall()

    return {
        "total_companies": len(results),
        "companies": [
            {
                "company_id": str(row.company_id),
                "company_name": row.company_name,
                "subscription_tier": row.subscription_tier,
                "is_active": row.is_active,
                "total_users": row.total_users,
                "created_at": row.created_at.isoformat() if row.created_at else None
            }
            for row in results
        ]
    }


# ============================================
# 6. DEACTIVATE COMPANY (SOFT DELETE)
# ============================================

@router.patch("/companies/{company_id}/deactivate")
async def deactivate_company(
    company_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(["super_admin"]))
):
    """
    Deactivate a company (SAFE option — data is preserved).

    What happens:
        - Company is_active = False
        - All users in that company is_active = False
        - Their data (suppliers, evaluations, documents) stays in database
        - They cannot login anymore
        - You can reactivate them later if needed

    Why this is safer than permanent delete:
        - Data is recoverable
        - Billing history preserved
        - Audit trail maintained
        - Industry standard for SaaS platforms

    How to use:
        PATCH /api/admin/companies/{company_id}/deactivate
        (Get company_id from GET /api/admin/companies endpoint first)
    """

    # Check company exists
    company = db.execute(
        text("""
            SELECT company_id, company_name, is_active
            FROM companies
            WHERE company_id = :company_id
        """),
        {"company_id": company_id}
    ).fetchone()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )

    if not company.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Company '{company.company_name}' is already deactivated"
        )

    # Deactivate company
    db.execute(
        text("""
            UPDATE companies
            SET is_active = FALSE,
                updated_at = NOW()
            WHERE company_id = :company_id
        """),
        {"company_id": company_id}
    )

    # Deactivate ALL users in that company
    db.execute(
        text("""
            UPDATE users
            SET is_active = FALSE,
                updated_at = NOW()
            WHERE company_id = :company_id
        """),
        {"company_id": company_id}
    )

    db.commit()

    return {
        "message": f"Company '{company.company_name}' has been deactivated successfully",
        "company_id": company_id,
        "action": "deactivated",
        "effect": "All users in this company can no longer login",
        "reversible": True,
        "to_reactivate": f"Call PATCH /api/admin/companies/{company_id}/reactivate"
    }


# ============================================
# 7. REACTIVATE COMPANY
# ============================================

@router.patch("/companies/{company_id}/reactivate")
async def reactivate_company(
    company_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(["super_admin"]))
):
    """
    Reactivate a previously deactivated company.

    What happens:
        - Company is_active = True
        - All users in that company is_active = True
        - They can login again immediately
    """

    # Check company exists
    company = db.execute(
        text("""
            SELECT company_id, company_name, is_active
            FROM companies
            WHERE company_id = :company_id
        """),
        {"company_id": company_id}
    ).fetchone()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )

    if company.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Company '{company.company_name}' is already active"
        )

    # Reactivate company
    db.execute(
        text("""
            UPDATE companies
            SET is_active = TRUE,
                updated_at = NOW()
            WHERE company_id = :company_id
        """),
        {"company_id": company_id}
    )

    # Reactivate all users in that company
    db.execute(
        text("""
            UPDATE users
            SET is_active = TRUE,
                updated_at = NOW()
            WHERE company_id = :company_id
        """),
        {"company_id": company_id}
    )

    db.commit()

    return {
        "message": f"Company '{company.company_name}' has been reactivated successfully",
        "company_id": company_id,
        "action": "reactivated",
        "effect": "All users in this company can now login again"
    }


# ============================================
# 8. PERMANENT DELETE COMPANY (HARD DELETE)
# ============================================

@router.delete("/companies/{company_id}/permanent-delete")
async def permanent_delete_company(
    company_id: str,
    confirm: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(["super_admin"]))
):
    """
    PERMANENTLY delete a company and ALL their data.

    ⚠️  WARNING: This action is IRREVERSIBLE.

    What gets deleted (in order):
        1. usage_tracking records
        2. notifications
        3. documents metadata (files in MinIO are NOT deleted — manual cleanup needed)
        4. evaluations
        5. suppliers
        6. api_keys
        7. users
        8. company

    Safety requirement:
        You MUST pass ?confirm=DELETE_COMPANY_PERMANENTLY in the URL
        This prevents accidental deletion

    Example:
        DELETE /api/admin/companies/{company_id}/permanent-delete?confirm=DELETE_COMPANY_PERMANENTLY
    """

    # Safety confirmation check
    # User must explicitly pass ?confirm=DELETE_COMPANY_PERMANENTLY
    if confirm != "DELETE_COMPANY_PERMANENTLY":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Safety check failed. "
                "To permanently delete, you must pass: "
                "?confirm=DELETE_COMPANY_PERMANENTLY in the URL. "
                "This action cannot be undone."
            )
        )

    # Check company exists
    company = db.execute(
        text("""
            SELECT company_id, company_name
            FROM companies
            WHERE company_id = :company_id
        """),
        {"company_id": company_id}
    ).fetchone()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )

    company_name = company.company_name

    try:
        # Delete in correct order (respecting foreign key relationships)
        # Step 1: Delete usage_tracking
        db.execute(
            text("DELETE FROM usage_tracking WHERE company_id = :company_id"),
            {"company_id": company_id}
        )

        # Step 2: Delete notifications (via user_id in this company)
        db.execute(
            text("""
                DELETE FROM notifications
                WHERE user_id IN (
                    SELECT user_id FROM users WHERE company_id = :company_id
                )
            """),
            {"company_id": company_id}
        )

        # Step 3: Delete documents (metadata only — MinIO files need manual cleanup)
        db.execute(
            text("""
                DELETE FROM documents
                WHERE supplier_id IN (
                    SELECT supplier_id FROM suppliers WHERE company_id = :company_id
                )
            """),
            {"company_id": company_id}
        )

        # Step 4: Delete evaluations
        db.execute(
            text("DELETE FROM evaluations WHERE company_id = :company_id"),
            {"company_id": company_id}
        )

        # Step 5: Delete suppliers
        db.execute(
            text("DELETE FROM suppliers WHERE company_id = :company_id"),
            {"company_id": company_id}
        )

        # Step 6: Delete api_keys
        db.execute(
            text("""
                DELETE FROM api_keys
                WHERE company_id = :company_id
            """),
            {"company_id": company_id}
        )


        # Step 7: Delete users
        db.execute(
            text("DELETE FROM users WHERE company_id = :company_id"),
            {"company_id": company_id}
        )

        # Step 8: Delete company itself
        db.execute(
            text("DELETE FROM companies WHERE company_id = :company_id"),
            {"company_id": company_id}
        )

        db.commit()

        return {
            "message": f"Company '{company_name}' and ALL associated data permanently deleted",
            "company_id": company_id,
            "action": "permanent_delete",
            "reversible": False,
            "warning": "Files uploaded to MinIO object storage were NOT deleted. Manual cleanup required if needed."
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Deletion failed and was rolled back: {str(e)}"
        )