import mimetypes
import os.path
import smtplib
from email.message import EmailMessage

def send_email(
    receiver: str,
    filepath: str,
):

    # Email content
    subject = "TIMIND - PAYSLIP - AUGUST 2025"
    body = "Please check the attached file below."
    sender_email = "hr@timind.co"
    password = "Timind*2025"  # Use App Password if using Gmail with 2FA

    # Create email
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver

    # Guess MIME type
    mime_type, _ = mimetypes.guess_type(filepath)
    mime_type = mime_type or "application/octet-stream"
    maintype, subtype = mime_type.split('/', 1)

    with open(filepath, 'rb') as file:
        msg.add_attachment(file.read(),
                           maintype=maintype,
                           subtype=subtype,
                           filename=os.path.basename(filepath))

    # Send email via Gmail SMTP server
    try:
        with smtplib.SMTP_SSL('mail.timind.co', 465) as smtp:
            smtp.login(sender_email, password)
            smtp.send_message(msg)
            print("Email sent successfully!")
    except Exception as e:
        print(f"Error: {e}")