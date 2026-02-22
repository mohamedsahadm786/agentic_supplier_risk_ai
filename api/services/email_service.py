import os
import resend
from dotenv import load_dotenv

load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL", "onboarding@resend.dev")


def send_evaluation_email(to_email: str, subject: str, message: str) -> dict:
    """
    Send evaluation completion email using Resend.
    Returns dict with success status.
    """

    try:
        response = resend.Emails.send({
            "from": f"Supplier Risk System <{FROM_EMAIL}>",
            
            "to": [to_email],
            "subject": subject,
            "html": f"<p>{message}</p>"
        })
        print("RESEND RESPONSE:", response)

        return {
            "success": True,
            "response": response
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }