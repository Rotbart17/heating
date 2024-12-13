#!/usr/bin/env python3
# dieses Modul setzt die Werte für den Regelkreis die sich durch die Programmsteuerung ändern
# Eigenen Thread eröffnen
# Schleife
# Programmsteuerungsdaten lesen
# Werte für den Vergleich adaptieren
# Werte vergleichen und DatenWerte setzen / löschen
# Werte: Brauchwasser an / aus, Heizung an / aus, Nachtabsenkung an / aus
# Schlafen
import time
import logging
import threading
import settings
from table import Tables
import random
from dataview import maindata
