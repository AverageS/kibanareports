from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
import requests
import json
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

PHANTOM = 'http://127.0.0.1:8000'
CONFIG_FILE = 'resources/config.json'
TEMPLATE = "resources/report_template.html"
CONFIG = dict()
PDF_FILE = 'report.pdf'


def set_up():
    global CONFIG
    global PHANTOM
    with open(CONFIG_FILE, 'r') as fp:
        CONFIG = json.load(fp)
    PHANTOM = CONFIG['phantom_url']


def generate_report(pics):
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template(TEMPLATE)
    html_out = template.render({'pics': pics})
    HTML(string=html_out).write_pdf(PDF_FILE, stylesheets=[CSS(string=CONFIG['pdf_css'])])


def collect_pic(url):
    pic = requests.get(PHANTOM, params={'url': url}).content.decode()
    return pic


def collect_pics_and_make_report():
    pics = [{'pic': collect_pic(x['url']), 'title': x['title'], 'description': x['description']} for x in CONFIG['pages']]
    generate_report(pics)


def send_report():
    msg = MIMEMultipart()
    msg['Subject'] = CONFIG['email_subject']
    msg['From'] = CONFIG['email_from']
    msg['To'] = CONFIG['email_to']

    part = MIMEBase('application', "octet-stream")
    part.set_payload(open(PDF_FILE, "rb").read())
    encoders.encode_base64(part)

    part.add_header('Content-Disposition', 'attachment; filename="report.pdf"')

    msg.attach(part)

    server = smtplib.SMTP_SSL(CONFIG['smtp_server'])
    server.login(CONFIG['email_from'], CONFIG['email_password'])
    server.sendmail(CONFIG['email_from'], CONFIG['email_to'], msg.as_string())
    server.quit()


if __name__ == '__main__':
    set_up()
    while True:
        logger.info('Started')
        collect_pics_and_make_report()
        send_report()
        logger.info('sent report, going to sleep')
        time.sleep(CONFIG['time_interval'])


