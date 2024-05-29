
venv: venv/touchfile

venv/touchfile: requirements.txt
	test -d venv || python3 -m venv venv
	. venv/bin/activate; python3 -m pip install -Ur requirements.txt
	touch venv/touchfile

.PHONY: clean
clean:
	rm -rf .venv

#
#
#

.PHONY: dump
dump: venv
	. venv/bin/activate; ./aptus-dump.py

.PHONY: dump-agera
dump-agera: venv
	. venv/bin/activate; ./aptus-dump.py agera

.PHONY: dump-authorities
dump-authorities: venv
	. venv/bin/activate; ./aptus-dump.py authorities

.PHONY: dump-customers
dump-customers: venv
	. venv/bin/activate; ./aptus-dump.py customers

.PHONY: dump-bookings
dump-bookings: venv
	. venv/bin/activate; ./aptus-dump.py bookings
