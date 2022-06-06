#!/usr/bin/env python3

import json
import logging
import sys

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import re
import config

#
#
#

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

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
            logger.info("Logged in successfully!")
        except NoSuchElementException:
            logger.error('Error logging in.', )
            web.quit()
            quit(1)

    except NoSuchElementException:
        logger.error('Error logging in, could not find fields for username and password or login button.', )
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
        logger.error('Error while performing search')
        web.quit()
        quit(1)


def aptus_fitler_search_result(element, expected_name, expected_url_match):
    try:
        # Get name
        name_elements = element.find_elements(by=By.CSS_SELECTOR, value='td.firstResultColumn')

        if len(name_elements) is not 1:
            logger.error('Unexpected number of name elements in search result row')
            web.quit()
            quit(1)

        # Verify that name is the expected
        actual_name = name_elements[0].get_attribute('innerHTML')
        if actual_name != expected_name:
            return False

        # Get onclick attribute and match against expected
        return expected_url_match in element.get_attribute('onclick')

    except NoSuchElementException:
        logger.error('Error while parsing search box')
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
        logger.error('Could not find customer with name: {}'.format(customer_name))
    elif len(customer_results) != 1:
        logger.error('Found more than one customer with name: {}'.format(customer_name))

    # Open customer
    customer_results[0].click()


#
# Dump
#

def aptus_dump_customer_details_row(tr_element, expected_label, row_type='string'):
    td_elements = tr_element.find_elements(by=By.CSS_SELECTOR, value='td')

    if len(td_elements) != 2:
        logger.error('Error dumping customer details row, expected 2 td elements in tr')
        web.quit()
        quit(1)

    # Label
    label_td = td_elements[0]
    actual_label = label_td.find_element(by=By.CSS_SELECTOR, value='label').get_attribute('for')

    if actual_label != expected_label:
        logger.error(
            'Error dumping customer details row, expected label {}, got label {}'.format(expected_label, actual_label))
        web.quit()
        quit(1)

    # Value
    value_td = td_elements[1]
    value_raw = value_td.get_attribute('innerHTML')
    value_trimmed = value_raw.strip()

    if row_type == 'string':
        return value_trimmed
    elif row_type == 'bool':
        if value_trimmed == 'Ja':
            return True
        elif value_trimmed == 'Nej':
            return False
        else:
            raise ValueError(
                'Unknown value for bool label {}: {}, expected Ja or Nej'.format(expected_label, value_trimmed))
    else:
        raise ValueError('row_type must be string or bool')


def aptus_dump_customer_details():
    # Details table
    details_table_rows = web.find_elements(by=By.CSS_SELECTOR,
                                           value='div.detailsTableDiv > table.detailsTable > tbody > tr')

    if len(details_table_rows) != 6:
        logger.error('Error dumping customer, expected 6 rows in details table')
        web.quit()
        quit(1)

    return {
        'name': aptus_dump_customer_details_row(details_table_rows[0], 'Name'),
        'freeText1': aptus_dump_customer_details_row(details_table_rows[1], 'Fritextf_lt_1'),
        'freeText2': aptus_dump_customer_details_row(details_table_rows[2], 'Fritextf_lt_2'),
        'freeText3': aptus_dump_customer_details_row(details_table_rows[3], 'Fritextf_lt_3'),
        'freeText4': aptus_dump_customer_details_row(details_table_rows[4], 'Fritextf_lt_4'),
        'isCompany': aptus_dump_customer_details_row(details_table_rows[5], 'IsCompany', row_type='bool')
    }


def aptus_dump_key(key_id):
    return {
        'id': key_id
    }


def aptus_dump_customer_keys(customer_id):
    # Open url directly to customer page
    customer_url = '{base}/CustomerKeys/Index/{id}'.format(base=config.APTUS_BASE_URL, id=customer_id)
    web.get(customer_url)

    # Keys table
    table_rows = web.find_elements(by=By.CSS_SELECTOR,
                                   value='div.listTableDiv > table.listTable > tbody > tr')

    onclick_attributes = list(map(lambda row: row.get_attribute('onclick'), table_rows))
    key_onclick_urls = list(filter(lambda a: a is not None and '/CustomerKeys/Details/' in a, onclick_attributes))
    key_ids = list(map(lambda a: re.search(r"document\.location\.href=\'.+/CustomerKeys/Details/(\d+)\'", a).group(1),
                       key_onclick_urls))

    keys = []

    # Loop over key id's
    for key_id in key_ids:
        key = aptus_dump_key(key_id)
        keys.append(key)

    return keys


def aptus_dump_customer(customer_id):
    # Open url directly to customer page
    customer_url = '{base}/Customer/Details/{id}'.format(base=config.APTUS_BASE_URL, id=customer_id)
    web.get(customer_url)

    if web.current_url != customer_url:
        # Customer does not exist if we have been redirected to other page
        logger.info('Customer ID: {} does not exist'.format(customer_id))
        # Return None to signify no data
        return None

    logger.info('Customer ID: {} exist'.format(customer_id))

    # Gather customer data

    customer = {
        'id': customer_id,
        'details': aptus_dump_customer_details(),
        'keys': aptus_dump_customer_keys(customer_id)
    }

    return customer


def aptus_dump_all_customers():
    customers = []

    # Loop over customer id's
    for customer_id in range(0, 5):
        customer = aptus_dump_customer(customer_id)
        if customer is not None:
            customers.append(customer)

    with open('customer_dump.json', 'w', encoding='utf-8') as outfile:
        json_string = json.dumps(customers, indent=2, ensure_ascii=False)
        outfile.write(json_string)


#
#
#


aptus_login()
aptus_dump_all_customers()
