# Create View from Qubole Table
When creating a view file in Looker, and when using a Qubole table, you cannot choose the "Create View From Table" option. You have to write a View file manually.
This script allows a user to input a table they wish to create a view from, and it will generate a View file.


## To run:
1. Run `pip3 install -r requirements.txt` to install necessary Python libraries
    > If you do not have pip3, run `brew install pip3`

    > If you do not have Homebrew installed, double check if you're a developer

2. Run `python3 converter.py -t <TABLE_NAME>` to generate the View file
    > Example: `python3 converter.py -t egdp_prod_demand_solutions.booking_commission_eps_taap_report_v1`

    > If chromedriver is giving you issues, follow the steps in the [Fixing Chromedriver](#fixing-chromedriver) section
3. The resulting file will be sent to an `output.txt` file in this directory. You can manually copy/paste this into Looker

### Fixing Chromedriver
1. [Download](https://chromedriver.chromium.org/downloads) the correct chromedriver based on which version of Chrome you use
2. Delete the old chromedriver and move the Chromedriver executable you just donwloaded to this directory. Make sure to name it "chromedriver"
3. Run `chmod 755 chromedriver` to change permissions on your chromedriver

If you run into a message that says "macOS cannot verify that this app is free from malware", go to:
System Preferences --> Security and Privacy --> General, and click on the "Open Anyway" box for Chromedriver.
