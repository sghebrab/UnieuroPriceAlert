# Unieuro Price Alert

## Overview

Tired of having to sistematically refresh Unieuro's products pages to know if the price for a specific product is acceptable for you?
Then welcome to **Unieuro Price Alert**, a short, simple Python script that automatically alerts you when a product's price drops under a chosen threshold.
With the latest modifications, you can track the price of more than one product at each run and be informed not only if the price goes under your specified threshold,
but also if it hits an historical minimum, which could be also interesting for you.

## How to

1. Clone the repository to a chosen folder. In the following instructions, it is assumed that the directory will be `/home/$USER/PythonProjects/UnieuroPriceAlert/`;
2. Move inside the newly created directory (`cd /home/$USER/PythonProjects/UnieuroPriceAlert/`)
3. Create a virtual environment named venv (`python3 -m venv venv`) and activate it (`. venv/bin/activate`);
4. Install the required libraries containted in requirements.txt (`python3 -m pip install -r requirements.txt`);
5. Deactivate the virtual environment (`deactivate`);
6. Create a file named `connections.log` inside the working directory (it will keep track of any retrieved price);
7. Copy the `conf.json.sample` file into a new file named `conf.json`;
8. Populate the `conf.json` file with the correct values;
9. Make `run.sh` executable (`chmod +x run.sh`) and edit it so that the first instruction is a `cd` to the working directory;
10. Create a cron job that executes the run.sh script as frequently as you need (e.g. `*/5 * * * * env USER=$LOGNAME /bin/bash /home/$LOGNAME/Documents/PythonProjects/UnieuroPriceAlert/run.sh > /dev/null 2>&1`)
11. Optionally, create a cron job that deletes the content of `connections.log` (daily, for example).

## Results

After creating the cron job, if everything is set up correctly, the script will retrieve the current price for the specified product at specified time intervals.

If the current price is under the threshold specified by the user in the `conf.json` file or if it hits a new historical minimum, then an e-mail will be sent by the user to itself. 
The content of the e-mail will be the URL of the product along with the current price. You won't be notified again unless the price goes again above threshold and then below it.
