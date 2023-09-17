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

```shell
python3 --version
```

If you get a response saying something like *Python 3.x.x* skip to [Selenium](#install-selenium)

If you don't have Python 3 installed, open a [Terminal](#terminal) and enter

```shell
brew install python3
```

### Install Selenium
Open a [Terminal](#terminal) and enter

```shell
pip3 install selenium
```

### Browsers

Configure the browser in the `config.py` file.

#### Chrome

Chrome requires installing `chromedriver`.

```shell
brew install chromedriver
```

How to fix chromedriver quarantine after update:

```shell
xattr -dr com.apple.quarantine $(readlink -f $(which chromedriver))
```

#### Safari

**NOT WORKING FULLY**

Safari requires enabling the built-in driver.

```shell
sudo safaridriver --enable
```

#### Firefox

Firefox does not require any installation other than the browser.

```shell
brew install geckodriver
```

# Aptus Dump

Dump all authorities and customers.

Creates the following files:
* `./dumps/<YYYY-MM-DD-HHMM>/authorities_dump.json`
* `./dumps/<YYYY-MM-DD-HHMM>/customer_dump.json`

```shell
./aptus-dump.py
```

# Aptus Manage

```shell
./aptus-manage.py
```
