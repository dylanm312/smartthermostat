[![Pylint](https://github.com/dylanm312/smartthermostat/actions/workflows/pylint.yml/badge.svg)](https://github.com/dylanm312/smartthermostat/actions/workflows/pylint.yml)

# Raspberry Pi Smart Thermostat
This project uses Flask for the backend, Bootstrap for the frontend, and Chart.JS for the data visualizations.

## Required Hardware
* [Electronics-Salon Relay Board](https://smile.amazon.com/gp/product/B07CZL2SKN/ref=ppx_yo_dt_b_asin_title_o04_s00?ie=UTF8&psc=1)
* [Lechacal RPICT3T1 Current and Temperature Sensor](http://lechacal.com/wiki/index.php?title=RPICT3T1) -- we are only using the temperature portion
* [Raspberry Pi](https://smile.amazon.com/Raspberry-Pi-MS-004-00000024-Model-Board/dp/B01LPLPBS8/ref=sr_1_14?dchild=1&keywords=raspberry+pi&qid=1615513274&s=electronics&sr=1-14) -- I used a 3B+ but other versions will likely work too.

## Installation Instructions
1. Assemble the hardware however you like. I used standoffs to stack the three components, but you could use a breadboard as well.
2. Download and extract the source code to a folder of your choosing
3. Install `virtualenv` and `virtualenvwrapper` (skip to step 4 if you have these already).
    
    ```bash
    pip3 install virtualenv virtualenvwrapper
    ```
    
    You will also need to make some changes to your `~/.bashrc` file for virtualenvwrapper to work properly, [see here](https://virtualenvwrapper.readthedocs.io/en/latest/install.html#basic-installation).
3. Create a virtual environment for the project and switch into it
    
    ```bash
    mkvirtualenv smarttthermostat
    workon smartthermostat
    ```
    
4. Install the Python dependencies

    ```bash
    pip3 install -r requirements.txt
    ```
    
5. Launch the app

    ```bash
    python3 main.py
    ```
    
6. Open the web interface to see your thermostat at work! By default, the web server runs on port 5000.
