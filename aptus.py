import json
import logging
import re
from datetime import datetime
from pathlib import Path

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By


class Aptus:
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.username = username
        self.password = password

        # Initialize browser driver
        self.web = webdriver.Chrome()

        # Implicitly wait maximum 10 seconds for elements
        self.web.implicitly_wait(10)

        self.logger = logging.getLogger(__name__)

    def _build_url(self, path: str) -> str:
        return '{base}/{path}'.format(base=self.base_url, path=path)

    def _abort(self):
        self.web.quit()
        raise Exception('Aborted Aptus due to error')

    def open_path(self, path: str) -> str:
        login_attempts = 1

        while login_attempts >= 0:
            # Open url
            self.web.get(self._build_url(path))

            # Get current url after potential redirects etc.
            current_url = self.web.current_url

            login_redirect_url = self._build_url('Account/Login')

            if not current_url.startswith(login_redirect_url):
                # If not redirected to login page
                return current_url

            login_attempts -= 1
            print('- Redirected to login page')

            try:
                # Enter username
                username_field = self.web.find_element(by=By.ID, value='Username')
                username_field.send_keys(self.username)

                # Enter password
                password_field = self.web.find_element(by=By.ID, value='Password')
                password_field.send_keys(self.password)

                # Click login button
                login_button = self.web.find_element(by=By.ID, value='btnLogin')
                login_button.click()
            except NoSuchElementException:
                self.logger.error('Error logging in, could not find fields for username and password or login button.')
                self._abort()

            # Get current url after potential redirects etc. again
            current_url = self.web.current_url

            if not current_url.startswith(login_redirect_url):
                # If not redirected to login page again
                print('- Logged in')

                # Open url again after login since some pages are not reditected to correctly
                self.web.get(self._build_url(path))

                # Get current url after potential redirects etc.
                current_url = self.web.current_url

                return current_url

    def dump_all_authorities(self, dump_dir: Path):
        # Open url to authority index page
        self.open_path('Authority/Index')

        # Authority table
        tr_elements = self.web.find_elements(by=By.CSS_SELECTOR,
                                             value='div.listTableDiv > table.listTable > tbody > tr')

        row_datas = list(map(lambda tr_element: {
            'tr': tr_element,
            'onclick': tr_element.get_attribute('onclick')
        }, tr_elements))

        row_datas = list(
            filter(lambda row: row.get('onclick') is not None and '/Authority/Details/' in row.get('onclick'),
                   row_datas))

        row_datas = list(
            map(lambda row: {
                'id': re.search(r"document\.location\.href=\'.+/Authority/Details/(\d+)\'", row.get('onclick')).group(
                    1),
                'name': row.get('tr').find_element(by=By.CSS_SELECTOR, value='td').get_attribute('innerHTML').strip()
            }, row_datas))

        print('Authorities: {}'.format(len(row_datas)))

        authorities = []

        # Loop over authority id's
        for authority_data in row_datas:
            authorities.append(self.dump_authority(authority_data.get('id'), authority_data.get('name')))

        authorities_dump_file_path = dump_dir.joinpath("authorities_dump.json")

        with authorities_dump_file_path.open(mode='w', encoding='utf-8') as outfile:
            json_string = json.dumps(authorities, indent=2, ensure_ascii=False)
            outfile.write(json_string)

    def dump_authority(self, authority_id, authority_name):
        # Open authority details page
        self.open_path('Authority/Details/{id}'.format(id=authority_id))

        # Permissions table
        td_elements = self.web.find_elements(by=By.CSS_SELECTOR,
                                             value='div.listTableDiv > div > table.listTable > tbody > tr > td')

        timezones = list(map(lambda td_element: td_element.get_attribute('innerHTML').strip(), td_elements))

        print('Authority {}, {}, {} timezones'.format(authority_id, authority_name, len(timezones)))

        return {
            'id': authority_id,
            'name': authority_name,
            'timezones': timezones
        }

    def dump_all_customers(self, dump_dir: Path):
        customers = []

        # Loop over customer id's
        for customer_id in range(0, 600):
            customer = self.dump_customer(customer_id)
            if customer is not None:
                customers.append(customer)

        customer_dump_file_path = dump_dir.joinpath('customer_dump.json')

        with customer_dump_file_path.open(mode='w', encoding='utf-8') as outfile:
            json_string = json.dumps(customers, indent=2, ensure_ascii=False)
            outfile.write(json_string)

    def dump_customer(self, customer_id):
        # Open url to customer details page
        customer_details_path = 'Customer/Details/{id}'.format(id=customer_id)
        current_url = self.open_path(customer_details_path)

        if not current_url.endswith(customer_details_path):
            # Customer does not exist if we have been redirected to other page
            print('Customer ID: {} does not exist'.format(customer_id))
            # Return None to signify no data
            return None

        print('Customer ID: {}'.format(customer_id))

        # Gather customer data

        customer = {
            'id': customer_id,
            'details': self.dump_customer_details(),
            'keys': self.dump_customer_keys(customer_id),
            'contracts': self.dump_customer_contracts(customer_id),
            'entryPhone': self.dump_customer_entry_phone(customer_id),
            'notes': self.dump_customer_notes(customer_id)
        }

        return customer

    def dump_customer_details(self):
        # Details table
        details_table_rows = self.web.find_elements(by=By.CSS_SELECTOR,
                                                    value='div.detailsTableDiv > table.detailsTable > tbody > tr')

        if len(details_table_rows) != 6:
            self.logger.error('Error dumping customer, expected 6 rows in details table')
            self._abort()

        return {
            'name': self.dump_customer_details_row(details_table_rows[0], 'Name', 'string'),
            'freeText1': self.dump_customer_details_row(details_table_rows[1], 'Fritextf_lt_1', 'string'),
            'freeText2': self.dump_customer_details_row(details_table_rows[2], 'Fritextf_lt_2', 'string'),
            'freeText3': self.dump_customer_details_row(details_table_rows[3], 'Fritextf_lt_3', 'string'),
            'freeText4': self.dump_customer_details_row(details_table_rows[4], 'Fritextf_lt_4', 'string'),
            'isCompany': self.dump_customer_details_row(details_table_rows[5], 'IsCompany', 'bool')
        }

    def dump_customer_details_row(self, tr_element, expected_label, input_type):
        td_elements = tr_element.find_elements(by=By.CSS_SELECTOR, value='td')

        if len(td_elements) != 2:
            self.logger.error('Error dumping customer details row, expected 2 td elements in tr')
            self._abort()

        # Label
        label_td = td_elements[0]
        actual_label = label_td.find_element(by=By.CSS_SELECTOR, value='label').get_attribute('for')

        if actual_label != expected_label:
            self.logger.error(
                'Error dumping customer details row, expected label {}, got label {}'.format(expected_label,
                                                                                             actual_label))
            self._abort()

        # Value
        return self.convert_parse_string(td_elements[1], input_type)

    def dump_customer_keys(self, customer_id):
        # Open url to customer keys page
        self.open_path('CustomerKeys/Index/{id}'.format(id=customer_id))

        # Keys table
        table_rows = self.web.find_elements(by=By.CSS_SELECTOR,
                                            value='div.listTableDiv > table.listTable > tbody > tr')

        onclick_attributes = list(map(lambda row: row.get_attribute('onclick'), table_rows))
        key_onclick_urls = list(filter(lambda a: a is not None and '/CustomerKeys/Details/' in a, onclick_attributes))
        key_ids = list(
            map(lambda a: re.search(r"document\.location\.href=\'.+/CustomerKeys/Details/(\d+)\'", a).group(1),
                key_onclick_urls))

        keys = []

        print('Keys: {}'.format(len(key_ids)))

        # Loop over key id's
        for key_id in key_ids:
            keys.append(self.dump_key(key_id))

        return keys

    def dump_key(self, key_id):
        # Open url to key details page
        self.open_path('CustomerKeys/Details/{id}'.format(id=key_id))

        # Details table
        details_table_rows = self.web.find_elements(by=By.CSS_SELECTOR,
                                                    value='div.detailsTableDiv > table.detailsTable > tbody > tr')

        if len(details_table_rows) != 10:
            self.logger.error('Error dumping key, expected 10 rows in details table')
            self._abort()

        print('Key ID: {}'.format(key_id))

        # Permissions table
        permissions_table_rows = self.web.find_elements(by=By.CSS_SELECTOR,
                                                        value='div.listTableDiv > table.listTable > tbody > tr')

        # Remove table header
        permissions_table_rows.pop(0)

        permissions = []

        # Loop over key id's
        for permission_row in permissions_table_rows:
            columns = permission_row.find_elements(by=By.CSS_SELECTOR, value='td')

            if len(columns) != 4:
                self.logger.error('Error dumping key permission, expected 4 columns in permissions table')
                self._abort()

            permissions.append({
                'permission': self.convert_parse_string(columns[0], 'string'),
                'start': self.convert_parse_string(columns[1], 'string'),
                'stop': self.convert_parse_string(columns[2], 'string'),
                'blocked': self.convert_parse_string(columns[3], 'bool')
            })

        return {
            'id': key_id,
            'name': self.dump_customer_details_row(details_table_rows[0], 'Name', 'string'),
            'cardLabel': self.dump_customer_details_row(details_table_rows[1], 'CardLabel', 'string'),
            'card': self.dump_customer_details_row(details_table_rows[2], 'Card', 'string'),
            'code': self.dump_customer_details_row(details_table_rows[3], 'Code', 'string'),
            'start': self.dump_customer_details_row(details_table_rows[4], 'Start', 'string'),
            'stop': self.dump_customer_details_row(details_table_rows[5], 'Stop', 'string'),
            'createdTime': self.dump_customer_details_row(details_table_rows[6], 'CreatedTime', 'string'),
            'blocked': self.dump_customer_details_row(details_table_rows[7], 'Blocked', 'bool'),
            'limitedLogging': self.dump_customer_details_row(details_table_rows[8], 'LimitedLogging', 'bool'),
            'freeText1': self.dump_customer_details_row(details_table_rows[9], 'Fritextf_lt_1', 'string'),
            'permissions': permissions
        }

    def dump_customer_contracts(self, customer_id):
        # Open url to customer contracts index page
        self.open_path('CustomerContract/Index/{id}'.format(id=customer_id))

        # Contracts table
        table_rows = self.web.find_elements(by=By.CSS_SELECTOR,
                                            value='div.listTableDiv > table.listTable > tbody > tr')

        onclick_attributes = list(map(lambda row: row.get_attribute('onclick'), table_rows))
        key_onclick_urls = list(
            filter(lambda a: a is not None and '/CustomerContract/Details/' in a, onclick_attributes))
        contract_ids = list(
            map(lambda a: re.search(r"document\.location\.href=\'.+/CustomerContract/Details/(\d+)\'", a).group(1),
                key_onclick_urls))

        contracts = []

        print('Contracts: {}'.format(len(contract_ids)))

        # Loop over key id's
        for contract_id in contract_ids:
            contracts.append(self.dump_contract(contract_id))

        return contracts

    def dump_contract(self, contract_id):
        # Open url to customer contract details page
        self.open_path('CustomerContract/Details/{id}'.format(id=contract_id))

        # Details table
        details_table_rows = self.web.find_elements(by=By.CSS_SELECTOR,
                                                    value='div.detailsTableDiv > table.detailsTable > tbody > tr')

        if len(details_table_rows) != 8:
            self.logger.error('Error dumping contract, expected 8 rows in details table')
            self._abort()

        print('Contract ID: {}'.format(contract_id))

        return {
            'id': contract_id,
            'startDate': self.dump_customer_details_row(details_table_rows[0], 'StartDate', 'string'),
            'endDate': self.dump_customer_details_row(details_table_rows[1], 'EndDate', 'string'),
            'objectName': self.dump_customer_details_row(details_table_rows[2], 'ObjectName', 'string'),
            'entryPhoneCallCode': self.dump_customer_details_row(details_table_rows[3], 'EntryPhoneCallCode',
                                                                 'string'),
            'floor': self.dump_customer_details_row(details_table_rows[4], 'Floor', 'string'),
            'floorText': self.dump_customer_details_row(details_table_rows[5], 'FloorText', 'string'),
            'apartmentNo': self.dump_customer_details_row(details_table_rows[6], 'ApartmentNo', 'string'),
            'addressName': self.dump_customer_details_row(details_table_rows[7], 'AddressName', 'string')
        }

    def dump_customer_entry_phone(self, customer_id):
        # Open url directly to entry phone index page
        customer_entry_phone_index_path = 'CustomerEntryPhone/Index/{id}'.format(id=customer_id)
        current_url = self.open_path(customer_entry_phone_index_path)

        if current_url.endswith(customer_entry_phone_index_path):
            # Customer does not have entry phone if we are still at the index page
            print('Does not have entry phone')
            # Return None to signify no data
            return None

        # Get entry phone id
        entry_phone_id = re.search(r".+/CustomerEntryPhone/Details/(\d+)", current_url).group(1)

        print('Entry phone ID: {}'.format(entry_phone_id))

        # Entry phone names table
        entry_phone_name_rows = self.web.find_elements(by=By.CSS_SELECTOR,
                                                       value='div.listTableDiv > table.listTable > tbody > tr')

        # Remove table header
        entry_phone_name_rows.pop(0)

        entry_phone_names = []

        # Loop over entry phone names
        for entry_phone_name_row in entry_phone_name_rows:
            columns = entry_phone_name_row.find_elements(by=By.CSS_SELECTOR, value='td')

            if len(columns) != 5:
                self.logger.error('Error dumping entry phone name, expected 4 columns in list table')
                self._abort()

            entry_phone_names.append({
                'firstName': self.convert_parse_string(columns[0], 'string'),
                'surname': self.convert_parse_string(columns[1], 'string'),
                'phoneNumber': self.convert_parse_string(columns[2], 'string'),
                'callCode': self.convert_parse_string(columns[3], 'string'),
                'show': self.convert_parse_string(columns[4], 'bool')
            })

        # Details table
        details_table_rows = self.web.find_elements(by=By.CSS_SELECTOR,
                                                    value='div.detailsTableDiv > table.detailsTable > tbody > tr')

        if len(details_table_rows) != 8:
            self.logger.error('Error dumping entry phone, expected 8 rows in details table')
            self._abort()

        return {
            'id': entry_phone_id,
            'objectName': self.dump_customer_details_row(details_table_rows[0], 'ObjectName', 'string'),
            'phoneNumber': self.dump_customer_details_row(details_table_rows[1], 'PhoneNumber', 'string'),
            'firstName1': self.dump_customer_details_row(details_table_rows[2], 'FirstName1', 'string'),
            'surname1': self.dump_customer_details_row(details_table_rows[3], 'Surname1', 'string'),
            'firstName2': self.dump_customer_details_row(details_table_rows[4], 'FirstName2', 'string'),
            'surname2': self.dump_customer_details_row(details_table_rows[5], 'Surname2', 'string'),
            'showInEntryPhoneDisplay': self.dump_customer_details_row(details_table_rows[6], 'ShowInEntryPhoneDisplay',
                                                                      'bool'),
            'apartmentPhonePresent': self.dump_customer_details_row(details_table_rows[7], 'ApartmentPhonePresent',
                                                                    'bool'),
            'entryPhoneNames': entry_phone_names
        }

    def dump_customer_notes(self, customer_id):
        # Open url to customer note index page
        self.open_path('CustomerNote/Index/{id}'.format(id=customer_id))

        # Notes list
        notes_table_rows = self.web.find_elements(by=By.CSS_SELECTOR,
                                                  value='div.listTableDiv > table.listTable > tbody > tr')

        # Remove table header
        notes_table_rows.pop(0)

        notes = []

        print('Notes: {}'.format(len(notes_table_rows)))

        # Loop over note table rows
        for permission_row in notes_table_rows:
            columns = permission_row.find_elements(by=By.CSS_SELECTOR, value='td')

            if len(columns) != 4:
                self.logger.error('Error dumping customer note, expected 4 columns in customer note table')
                self._abort()

            notes.append({
                'note': self.convert_parse_string(columns[0], 'string'),
                'createdTime': self.convert_parse_string(columns[1], 'string'),
                'operator': self.convert_parse_string(columns[2], 'string')
            })

        return notes

    def get_details_table_row_forName(self, name):
        # Details table
        details_table_rows = self.web.find_elements(by=By.CSS_SELECTOR,
                                                    value='div.detailsTableDiv > table.detailsTable > tbody > tr')

        # Filter out tr element
        filtered_rows = list(
            filter(lambda row: row.find_element(by=By.CSS_SELECTOR, value='td > label').get_attribute('for') == name,
                   details_table_rows))

        if len(filtered_rows) != 1:
            raise Exception('Could not find expected field in details table')

        return filtered_rows[0]

    def update_key(self, key_data: dict):
        key_id = key_data.get('id')
        # Open url to key edit page
        self.open_path('CustomerKeys/Edit/{id}'.format(id=key_id))

        print('Updating key: {}'.format(key_id))

        has_changed = False

        # Update code
        code_key = 'code'
        if code_key in key_data:
            code_tr = self.get_details_table_row_forName('Code')
            code_input = code_tr.find_element(by=By.CSS_SELECTOR, value='input')

            # Update code
            old_code = code_input.get_attribute('value')
            new_code = key_data.get(code_key)

            if new_code != old_code:
                has_changed = True
                code_input.clear()
                code_input.send_keys(new_code)
                print('Updating code from: {} to: {}'.format(old_code, new_code))

        # Save
        if has_changed:
            save_button = self.web.find_element(by=By.ID, value='theSubmitButton')
            save_button.click()

            # Wait for OK
            self.web.find_element(by=By.CSS_SELECTOR, value='div.message > div.messageOk')
            print('Saved successfully!')
        else:
            print('No changes!')

    def update_keys(self, key_datas: list):
        for key_data in key_datas:
            self.update_key(key_data)

    def quit(self):
        self.web.quit()

    @staticmethod
    def convert_parse_string(td_element, input_type):
        value_raw = td_element.get_attribute('innerHTML')
        value_trimmed = value_raw.strip()

        if input_type == 'string':
            return value_trimmed
        elif input_type == 'bool':
            if value_trimmed == 'Ja':
                return True
            elif value_trimmed == 'Nej':
                return False
            else:
                raise ValueError(
                    'Unknown value for bool label: {}, expected Ja or Nej'.format(value_trimmed))
        else:
            raise ValueError('row_type must be string or bool')

    #
    #
    #

    @staticmethod
    def create_dump_dir() -> Path:
        # Get current working directory
        work_dir_path = Path.cwd()

        # Create dump directory name and path
        dump_date = datetime.now()
        dump_dirname = dump_date.strftime("%Y-%m-%d-%H%M")
        dump_dir_path = work_dir_path.joinpath("dumps").joinpath(dump_dirname)

        # Create dumps directory if not existing
        if not dump_dir_path.exists():
            dump_dir_path.mkdir(parents=True)

        # Verify creation
        if not dump_dir_path.is_dir():
            raise Exception('Error creating dump directory')

        return dump_dir_path

    def dump_all(self):
        dump_dir = self.create_dump_dir()
        self.dump_all_authorities(dump_dir)
        self.dump_all_customers(dump_dir)
