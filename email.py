import smtplib, ssl ,email
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
def send(plaka ,dosya_yolu = "./",dosya = "simple.png"):
    subject = "Telefon algılandı"
    body = plaka + " plakalı araçta telefon kullanıldığı tespit edildi. Fotoğraf ektedir."
    sender_email = "*************"  # Enter your address
    receiver_email = "**********"  # Enter receiver address
    password = "*************" #app password / password
    message = MIMEMultipart()
    
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["Bcc"] = receiver_email


    message.attach(MIMEText(body, "plain"))
    filename = dosya_yolu + dosya
    with open(filename, "rb") as attachment:
   
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    encoders.encode_base64(part)

    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )

    message.attach(part)
    text = message.as_string()

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)
    context = ssl.create_default_context()
if __name__ == '__main__' :
    send("22 AA 0000","./","simple.png")