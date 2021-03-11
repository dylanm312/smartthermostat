# Raspberry Pi Smart Thermostat
This project uses Flask for the backend, Bootstrap for the frontend, and Chart.JS for the data visualizations.

## Installation Instructions
1. Download and extract the source code to a folder of your choosing
2. Install `virtualenv` and `virtualenvwrapper` (skip to step 3 if you have these already).
    
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
