# aptus-management

Tool for automating tasks with Aptus.

# Prerequisites

## What you need for running on MacOS

* Google Chrome
* Homebrew
* Python 3
* Selenium
* Chromedriver

### Install Google Chrome
Go to [https://www.google.com/chrome/](www.google.com/chrome) and follow the instructions

### Install homebew
Open a [Terminal](#terminal) and enter

`/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`

### Install Python 3
This should be pre installed on all macs, but you never know. Check by opening a [Terminal](#terminal) and enter

`python3 --version``

If you get a response saying something like *Python 3.x.x* skip to [Selenium](#install-selenium)

If you don't have Python 3 installed, open a [Terminal](#terminal) and enter

`brew install python3`

### Install Selenium
Open a [Terminal](#terminal) and enter

`pip3 install selenium`

### Install Chromedriver
Open a [Terminal](#terminal) and enter

`brew install chromedriver`

## What you need for running on Linux

* Google Chrome
* PIP3
* Selenium
* Chromedriver

### Install Google Chrome
Go to [https://www.google.com/chrome/](www.google.com/chrome) and follow the instructions

### Install PIP3
Open a Terminal and enter

`sudo apt-get install python3-pip`

### Install Selenium
Open a Terminal and enter

`pip3 install selenium`

### Install Chromedriver
Open a Terminal and enter

`sudo apt-get install chromium-chromedriver`
or
`sudo apt-get install chromedriver`

If your Linux doesn't have Chomedriver in apt, go to [chromedriver.storage.googleapis.com](https://chromedriver.storage.googleapis.com/index.html) and download a version compatible with your Chrome browser and extract the zip. Then run these commands:

`sudo mv -f ~/Downloads/chromedriver /usr/local/share/`

`sudo chmod +x /usr/local/share/chromedriver`

`sudo ln -s /usr/local/share/chromedriver /usr/local/bin/chromedriver`

`sudo ln -s /usr/local/share/chromedriver /usr/bin/chromedriver`

# Aptus Dump

Dump all authorities and customers.

Creates the following files:
* `authorities_dump.json`
* `customer_dump.json`

```shell
./aptus-dump.py
```

# Aptus Manage

```shell
./aptus-manage.py
```
