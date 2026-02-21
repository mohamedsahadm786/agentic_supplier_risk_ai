"""
LLM SERVICE (Centralized GPT Invocation Layer)

Responsibilities:
- Centralize all OpenAI calls
- Enforce subscription limits
- Track token usage
- Calculate cost
- Log usage safely
- Return clean structured output

This file acts as an abstraction layer between agents and OpenAI.
"""

import os
from openai import OpenAI
from sqlalchemy import text
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()


class LLMService:
    def __init__(self, db):
        """
        Initialize OpenAI client once.
        """
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o-mini"
        self.db = db

        # Pricing per 1K tokens (update if model changes)
        self.input_price_per_1k = 0.00015
        self.output_price_per_1k = 0.0006

    # ==========================================================
    # PUBLIC METHOD — SINGLE ENTRY POINT FOR ALL GPT CALLS
    # ==========================================================
    def invoke(
        self,
        messages,
        company_id,
        evaluation_id,
        agent_name,
        response_format=None,
        temperature=0.7
    ):
    
        """
        Centralized LLM invocation.

        Returns:
        {
            "content": <response text>,
            "usage": {
                "prompt_tokens": int,
                "completion_tokens": int,
                "total_tokens": int,
                "total_cost": float
            }
        }
        """

        # 1️⃣ Enforce subscription limit BEFORE calling OpenAI
        self._enforce_subscription_limit(company_id)

        # 2️⃣ Call OpenAI
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature
        }

        if response_format:
            kwargs["response_format"] = response_format

        response = self.client.chat.completions.create(**kwargs)

        # 3️⃣ Safely extract usage
        usage_data = getattr(response, "usage", None)

        prompt_tokens = getattr(usage_data, "prompt_tokens", 0) if usage_data else 0
        completion_tokens = getattr(usage_data, "completion_tokens", 0) if usage_data else 0
        total_tokens = getattr(usage_data, "total_tokens", 0) if usage_data else 0

        # 4️⃣ Calculate cost
        input_cost = (prompt_tokens / 1000) * self.input_price_per_1k
        output_cost = (completion_tokens / 1000) * self.output_price_per_1k
        total_cost = round(input_cost + output_cost, 6)

        # 5️⃣ Log usage safely (monitoring must not break workflow)
        try:
            self._log_usage(
                company_id=company_id,
                evaluation_id=evaluation_id,
                agent_name=agent_name,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                total_cost=total_cost
            )
        except Exception as e:
            print(f"⚠️ Usage logging failed (non-blocking): {e}")

        # 6️⃣ Return clean structured output
        return {
            "content": response.choices[0].message.content,
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
                "total_cost": total_cost
            }
        }

    # ==========================================================
    # SUBSCRIPTION LIMIT ENFORCEMENT
    # ==========================================================
    def _enforce_subscription_limit(self, company_id):
        """
        Prevent companies from exceeding workflow limits.
        """

        company = self.db.execute(
            text("""
                SELECT subscription_tier
                FROM companies
                WHERE company_id = :company_id
            """),
            {"company_id": company_id}
        ).fetchone()

        if not company:
            raise HTTPException(status_code=404, detail="Company not found")

        tier = company.subscription_tier

        # Count this month's evaluations
        workflow_count = self.db.execute(
            text("""
                SELECT COUNT(*)
                FROM evaluations
                WHERE company_id = :company_id
                AND created_at >= DATE_TRUNC('month', NOW())
            """),
            {"company_id": company_id}
        ).fetchone()[0]

        if tier == "free" and workflow_count >= 50:
            raise HTTPException(
                status_code=403,
                detail="Free plan limit reached (50 evaluations/month)"
            )

        if tier == "standard" and workflow_count >= 500:
            raise HTTPException(
                status_code=403,
                detail="Standard plan limit reached (500 evaluations/month)"
            )

        # Premium → unlimited

    # ==========================================================
    # SAFE USAGE LOGGING
    # ==========================================================
    def _log_usage(
        self,
        company_id,
        evaluation_id,
        agent_name,
        prompt_tokens,
        completion_tokens,
        total_tokens,
        total_cost
    ):
        """
        Insert usage record into usage_tracking table.
        """

        self.db.execute(
            text("""
                INSERT INTO usage_tracking (
                    company_id,
                    evaluation_id,
                    agent_name,
                    model_name,
                    prompt_tokens,
                    completion_tokens,
                    total_tokens,
                    total_cost
                )
                VALUES (
                    :company_id,
                    :evaluation_id,
                    :agent_name,
                    :model_name,
                    :prompt_tokens,
                    :completion_tokens,
                    :total_tokens,
                    :total_cost
                )
            """),
            {
                "company_id": company_id,
                "evaluation_id": evaluation_id,
                "agent_name": agent_name,
                "model_name": self.model,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
                "total_cost": total_cost
            }
        )

        self.db.commit()