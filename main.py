import requests
from bs4 import BeautifulSoup
import sys
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import json

# Open the JSON file containing the configuration parameters
conf_file = open("conf.json", "r")
# Then load it into a dictionary
conf = json.load(conf_file)
# The price you are willing to pay for the product
target_price = float(conf["target-price"])
# URL of the product on the Unieuro website
url = conf["url"]

# Copied and pasted from the web
def send_email(subject, body, sender, recipients, password):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    smtp_server = smtplib.SMTP_SSL(conf["smtp-server"], conf["smtp-port"])
    smtp_server.login(sender, password)
    smtp_server.sendmail(sender, recipients, msg.as_string())
    smtp_server.quit()

# Load from last_price.txt the previous price found on the web page
previous_price_file = open("last_price.txt", "r")
previous_price = previous_price_file.readline()
if previous_price == "":
    previous_price = 1e6
else:
    previous_price = float(previous_price)
previous_price_file.close()

# Load the HTML page with a GET request
html_page = requests.get(url).text
# Initialize the BeautifulSoup object
soup = BeautifulSoup(html_page, "html.parser")
# Find the right div that has the price in children spans
div_price_right = soup.find("div", class_="pdp-right__price")
span_price_int = div_price_right.find("span", class_="integer")
span_price_dec = div_price_right.find("span", class_="decimal")
# Get the text from both spans to obtain the price in decimal form
price_int = span_price_int.get_text()
price_dec = span_price_dec.get_text().replace(",", ".")
price_final = float(price_int + price_dec)
# For each check, write date and time, plus the current retrieved price (for historical purposes)
log_file = open("connections.log", "a")
log_file.write(str(datetime.now()) + " --> " + str(price_final) + "€\n")
log_file.close()
# If current price is less than the target AND previously it was not
# (otherwise it would have already notified you), then send an e-mail
if price_final <= target_price and previous_price > target_price:
    subject = "Price dropped!"
    body = "Current price for " + url + " --> " + str(price_final) + "€"
    sender = conf["sender"]
    recipients = [conf["sender"]]
    password = conf["password"]
    send_email(subject, body, sender, recipients, password)

# Finally, write the current price to the file, so that it can be retrieved later
previous_price_file = open("last_price.txt", "w")
previous_price_file.write(str(price_final))
previous_price_file.close()
