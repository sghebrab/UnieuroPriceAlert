import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import json

# Open the JSON file containing the configuration parameters
conf_file = open("conf.json", "r")
# Then load it into a dictionary
conf = json.load(conf_file)
conf_file.close()

sender = conf["sender"]
recipients = [conf["sender"]]
password = conf["password"]

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

connections_log = open("connections.log", "a")
# For each product to track in the JSON file
for product in conf["products"]:
    # Try loading the HTML page
    try:
        html_response = requests.get(product["url"], timeout=2)
    # If anything goes wrong with the same product for 3 times in a row, send an alert e-mail
    except requests.RequestException:
        if "subsequent_errors" not in product:
            product["subsequent_errors"] = 0
        product["subsequent_errors"] += 1
        if product["subsequent_errors"] == 3:
            send_email("Connection Error", "Error while fetching the page of " + product["friendly-name"], conf["sender"], [conf["sender"]], conf["password"])
            product["subsequent_errors"] = 0
        connections_log.write(str(datetime.now()) + " --> Unexpected error looking for " + product["friendly-name"] + "\n")
        continue
    # Reset the counter for subsequent errors, since the page was correctly loaded
    product["subsequent_errors"] = 0
    # Load the HTML page with a GET request
    html_page = html_response.text
    # Initialize the BeautifulSoup object
    soup = BeautifulSoup(html_page, "html.parser")
    # Find the availability of the product
    availability = soup.find("div", class_="available")
    # The second element is either on/off if the product is available or if it is not
    availability = availability.get_attribute_list("class")[1]
    if "availability" not in product:
        product["availability"] = availability
    # Find the right div that has the price in children spans
    div_price_right = soup.find("div", class_="pdp-right__price")
    # If the HTML page does not contain the aforementioned div, skip the rest of the iteration as the price cannot be found
    if div_price_right is None:
        send_email("Price error", "Unable to find the price in the HTML for product " + product["friendly-name"], conf["sender"], [conf["sender"]], conf["password"])
        connections_log.write(str(datetime.now()) + " --> Unable to find price for " + product["friendly-name"] + "\n")
        continue
    span_price_int = div_price_right.find("span", class_="integer")
    span_price_dec = div_price_right.find("span", class_="decimal")
    # Get the text from both spans to obtain the price in decimal form
    price_int = span_price_int.get_text().replace(".", "")
    price_dec = span_price_dec.get_text().replace(",", ".")
    price_final = float(price_int + price_dec)
    # Log current time and price for each product, just for information purposes
    connections_log.write(str(datetime.now()) + " --> " + product["friendly-name"] + " --> " + str(price_final) + "€\n")
    # If current price is lower than the threshold AND before this time it was not
    # (otherwise it would have already notified you), then send an e-mail
    if price_final <= product["target-price"] and product["latest-price"] > product["target-price"] and availability == "on":
        subject = "💸 Price under threshold! 💸"
        body = "Current price for " + product["friendly-name"] + " --> " + str(price_final) + "€\n"
        body += "Link --> " + product["url"]
        send_email(subject, body, sender, recipients, password)
        # If the current price is also the historical minimum, replace the latter with the newest value
        if price_final < product["lowest-price"]:
            product["lowest-price"] = price_final
    # If current price is not under threshold, but it is the lowest seen, notify the user to let him know
    # that current price is an historical minimum (maybe he's willing to pay that amount...)
    elif price_final <= product["lowest-price"] and availability == "on" and product["availability"] == "off":
        subject = "📉 All time low! 📉"
        body = "Current price for " + product["friendly-name"] + " --> " + str(price_final) + "€\n"
        body += "Previous historical minimum --> " + str(product["lowest-price"]) + "€\n"
        body += "Link --> " + product["url"]
        send_email(subject, body, sender, recipients, password)
        product["lowest-price"] = price_final
    # If the product was not available before and now is back in stock, send an email.
    elif product["availability"] == "off" and availability == "on":
        subject = "ℹ️  Product back in stock ℹ️"
        body = "Product " + product["friendly-name"] + " is back in stock.\n"
        body += "Current price --> " + str(price_final) + "€\n"
        body += "Link --> " + product["url"]
        send_email(subject, body, sender, recipients, password)
    # Finally, replace the latest price with the newly measured one
    product["latest-price"] = price_final
    product["availability"] = availability
connections_log.close()
# Dump the dictionary to the conf.json file
conf_file = open("conf.json", "w")
json.dump(conf, conf_file, indent=4)
conf_file.close()
