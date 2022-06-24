import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from secrets import mail_address, mail_password, recipients
from main import OctopusConsumption
from datetime import datetime, timedelta


def mail_sender(text, mail_subject):
    mail_content = text

    # The mail addresses and password

    sender_address = mail_address
    sender_pass = mail_password
    receiver_address = recipients
    # Setup the MIME
    message = MIMEMultipart()
    message['From'] = mail_address
    message['To'] = recipients
    message['Subject'] = mail_subject  # The subject line
    # The body and the attachments for the mail
    message.attach(MIMEText(mail_content, 'html'))
    # Create SMTP session for sending the mail
    session = smtplib.SMTP('smtp.gmail.com', 587)  # use gmail with port
    session.starttls()  # enable security
    session.login(sender_address, sender_pass)  # login with mail_id and password
    text = message.as_string()
    session.send_message(message)
    #session.sendmail(sender_address, receiver_address, text)
    session.quit()


yesterday = (datetime.today() - timedelta(1)).strftime('%A %d of %B')
subject = "Your rolling energy consumption as of " + yesterday
message = (OctopusConsumption().rolling_consumption())

mail_sender(message, mail_subject=subject)
