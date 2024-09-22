from email.message import EmailMessage
import ssl
import smtplib

email_sender ='deefweatheralert@gmail.com'
email_password ='qkri fcgt igoc pmio'
email_recevier = 'naemfares@gmail.com'

subject = 'Weather info'
body = """
this is from my app3
my app is weather info app
"""

em = EmailMessage()
em['From'] = email_sender
em['To'] = email_recevier
em['Subject'] = subject
em.set_content(body)

context = ssl.create_default_context()

with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
    smtp.login(email_sender, email_password)
    smtp.sendmail(email_sender, email_recevier, em.as_string())