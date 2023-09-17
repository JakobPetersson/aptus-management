#!/usr/bin/env python3

import argparse
import json
import sys
from pathlib import Path

import aptus
import config


#
#
#

def query_yes_no(question, default="no"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")


#
# Setup args parser
#

arg_parser = argparse.ArgumentParser(description='Aptus Manage')

arg_parser.add_argument(
    '--action',
    type=str,
    action='store',
    help=''
)

arg_parser.add_argument(
    '--file',
    type=str,
    action='store',
    help=''
)

args = arg_parser.parse_args()

if args.action == 'keys':

    if args.file is None:
        print('file argument is missing!')
        quit()

    key_file_path = Path(args.file)

    if not key_file_path.is_file():
        print('Provided files does not exist!')
        quit()

    with open(key_file_path, 'r', encoding='utf-8') as infile:
        keys = json.load(infile)

        if not query_yes_no('Are you sure you want to update {} keys?'.format(len(keys))):
            print('Aborting!')
            quit()

        apt = aptus.Aptus(config.BROWSER,
                          config.APTUS_BASE_URL,
                          config.APTUS_USERNAME,
                          config.APTUS_PASSWORD,
                          config.APTUS_MIN_CUSTOMER_ID,
                          config.APTUS_MAX_CUSTOMER_ID)
        apt.update_keys(keys)
        apt.quit()
else:
    print('Unknown action: {}'.format(args.action))
    quit()
