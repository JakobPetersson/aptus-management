#!/usr/bin/env python3
import sys

import aptus
import config

#
# Dump
#

apt = aptus.Aptus(config.BROWSER,
                  config.APTUS_BASE_URL,
                  config.APTUS_USERNAME,
                  config.APTUS_PASSWORD,
                  config.APTUS_MIN_CUSTOMER_ID,
                  config.APTUS_MAX_CUSTOMER_ID)

# Defined what parts to dump
parts_to_dump = sys.argv[1:]
if len(parts_to_dump) == 0:
    # Set defaults
    parts_to_dump = ['agera', 'authorities', 'customers', 'bookings']

apt.dump_all(parts_to_dump)
apt.quit()
