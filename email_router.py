from fastapi import APIRouter
from pydantic import BaseModel
import smtplib
from email.mime.text import MIMEText

router = APIRouter()

class EmailRequest(BaseModel):
    to: str
    subject: str
    message: str

@router.post("/send-email")
def send_email(data: EmailRequest):
    msg = MIMEText(data.message)
    msg["Subject"] = data.subject
    msg["From"] = "jayworkingstudio@gmail.com"
    msg["To"] = data.to

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login("jayworkingstudio@gmail.com", "mfym ewvu ldzs hqgi")
            server.send_message(msg)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
