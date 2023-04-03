#!/usr/bin/env python3

import aptus
import config

#
# Dump
#

apt = aptus.Aptus(config.APTUS_BASE_URL,
                  config.APTUS_USERNAME,
                  config.APTUS_PASSWORD,
                  config.APTUS_MIN_CUSTOMER_ID,
                  config.APTUS_MAX_CUSTOMER_ID)
apt.dump_all()
apt.quit()
