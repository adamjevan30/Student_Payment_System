import smtplib
from email.mime.text import MIMEText

EMAIL_ADDRESS = "jevanadammulato@gmail.com"
EMAIL_PASSWORD = "ajxv esxr vddl npoq"

def send_email(to_email, subject, message):

    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

        server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())

        server.quit()

        print("Email sent to", to_email)

    except Exception as e:
        print("Error sending email:", e)