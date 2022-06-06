#!/usr/bin/env python3

import logging
import sys

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import config

#
#
#

sys.setrecursionlimit(100000)

# Initialize browser driver
web = webdriver.Chrome()

# Implicitly wait maximum 10 seconds for elements
web.implicitly_wait(10)


def aptus_login():
    # Open login page
    web.get(config.APTUS_BASE_URL)

    try:
        # Find login fields
        username_field = web.find_element(by=By.ID, value='Username')
        password_field = web.find_element(by=By.ID, value='Password')
        login_button = web.find_element(by=By.ID, value='btnLogin')

        username_field.send_keys(config.APTUS_USERNAME)
        password_field.send_keys(config.APTUS_PASSWORD)
        login_button.click()

        try:
            # Verify login worked
            web.find_element(by=By.ID, value='namePart')
            logging.info("Logged in successfully!")
        except NoSuchElementException:
            logging.error('Error logging in.', )
            web.quit()
            quit(1)

    except NoSuchElementException:
        logging.error('Error logging in, could not find fields for username and password or login button.', )
        web.quit()
        quit(1)


def aptus_search(search_string):
    # Enter search string
    try:
        search_box = web.find_element(by=By.ID, value='namePart')
        search_box.clear()
        search_box.send_keys(search_string)
        search_box.send_keys(Keys.RETURN)

        # Ensure results show up
        return web.find_element(by=By.CSS_SELECTOR, value='table.searchResultTable')

    except NoSuchElementException:
        logging.error('Error while performing search')
        web.quit()
        quit(1)


def aptus_fitler_search_result(element, expected_name, expected_url_match):
    try:
        # Get name
        name_elements = element.find_elements(by=By.CSS_SELECTOR, value='td.firstResultColumn')

        if len(name_elements) is not 1:
            logging.error('Unexpected number of name elements in search result row')
            web.quit()
            quit(1)

        # Verify that name is the expected
        actual_name = name_elements[0].get_attribute('innerHTML')
        if actual_name != expected_name:
            return False

        # Get onclick attribute and match against expected
        return expected_url_match in element.get_attribute('onclick')

    except NoSuchElementException:
        logging.error('Error while parsing search box')
        web.quit()
        quit(1)

    return False


def aptus_customer_search_and_open(customer_name):
    search_results = aptus_search(customer_name)

    # Ensure results show up
    clickable_results = search_results.find_elements(by=By.CSS_SELECTOR, value='tbody > tr.clickable')

    customer_results = list(
        filter(lambda e: aptus_fitler_search_result(e, customer_name, '/Customer/Details/'), clickable_results))

    if len(customer_results) == 0:
        logging.error('Could not find customer with name: {}'.format(customer_name))
    elif len(customer_results) != 1:
        logging.error('Found more than one customer with name: {}'.format(customer_name))

    # Open customer
    customer_results[0].click()


aptus_login()
