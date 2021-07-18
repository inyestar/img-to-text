# coding=utf-8
# reference: https://stackoverflow.com/questions/3894923/extract-content-from-a-file-with-mime-multipart

import os
import email
import mimetypes
import smtplib
from email.mime.text import MIMEText


# get message from file
def get_msg(msg_path):
    msg = None
    if os.path.isfile(msg_path):
        with open(msg_path) as f:
            msg = email.message_from_file(f)
    return msg


# get image from message
def extract_img(msg):
    img_list = list()
    for idx, multipart in enumerate(msg.walk()):
        if multipart.get_content_maintype() == 'image':
            filename = multipart.get_filename()
            if not filename:
                ext = mimetypes.guess_extension(multipart.get_content_maintype)
                filename = 'image-%02d%s' % (idx, ext or '.tiff')
            img_list.append((filename, multipart))
    return img_list


# extract image from multipart and save
def save_img(img_list):
    save_list = list()
    for i in img_list:
        # i = (filename, multipart)
        save_path = os.path.join(os.environ['TMP_DIR'], i[0])
        with open(save_path, 'wb') as f:
            f.write(i[1].get_payload(decode=True))
        if os.path.isfile(save_path):
            save_list.append(save_path)
    return save_list


# get stored image file path
def get_img(mail_path):
    msg = get_msg(mail_path)
    if not msg:
        return None
    img_list = extract_img(msg)
    if len(img_list) == 0:
        return None
    return save_img(img_list)


# reassemble message with text from api
def reassemble(text_list, mail_path):
    msg = get_msg(mail_path)
    if msg:
        for text in text_list:
            msg.attach(MIMEText(text, 'plain'))
        with open(mail_path, 'w') as f:
            f.write(msg.as_string())


# send message
def send(mail_path):
    msg = get_msg(mail_path)
    if msg:
        # ['Return-Path', 'X-Original-To', 'Delivered-To', 'Received', 'Subject']
        # ['Return-Path', 'X-Original-To', 'Delivered-To', 'Received', 'MIME-Version', 'Date', 'Subject', 'From', 'To', 'Content-Type', 'Message-ID']
        with smtplib.SMTP(os.environ['SMTP_SERVER'], os.environ['SMTP_PORT']) as server:
            try:
                code = server.sendmail(msg['Return-Path'], msg['Delivered-To'], msg.as_bytes())
                print('[INFO] %s sent code=%s' % (mail_path, str(code)))
            except Exception as error:
                if type(error) is smtplib.SMTPDataError and error.args[0] == 550:
                    return True
                print('[ERROR] %s at msg.send' % str(error))
                return False
            finally:
                server.quit()
    return True


# delete message
def delete(mail_path):
    if os.path.isfile(mail_path):
        os.remove(mail_path)
        print('[INFO] %s got deleted' % mail_path)