from typing import List
from pydantic import EmailStr
from .index import render_template, create_message, mail








class UserAuthEmail:
  
  @staticmethod
  async def send_verification_email(recipient: List[EmailStr], datadict: dict):
    """Sends verification email using the template."""

    context = datadict
    html_content = render_template("verify_email.html", context)
    message = create_message(recipients=recipient, subject="Welcome to our platform", body=html_content)

    await mail.send_message(message)
    return {"message": "Verification email sent successfully please check your email address and verify your account."}
