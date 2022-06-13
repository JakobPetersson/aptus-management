#!/usr/bin/env python3

import aptus
import config

#
# Dump
#

apt = aptus.Aptus(config.APTUS_BASE_URL, config.APTUS_USERNAME, config.APTUS_PASSWORD)
apt.dump_all_authorities()
apt.dump_all_customers()
apt.quit()
