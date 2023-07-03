
# hier sind slle globalen Variablen und verwendeten Basiseinstellungen gesammelt

import logging

# Muster für logging
# logging.debug('debug')
# logging.info('info')
# logging.warning('warning')
# logging.error('error')
# logging.critical('critical')

logging.basicConfig(
    filename='heizung.log',
    filemode='w',
    format='%(asctime)s %(levelname)s: %(message)s',
    level=logging.DEBUG
)


# Konstanten

# Pfad zu Datenbank
DBPATH = "/home/ernst/Devel/heating/heizung.db"

# Sensornames ["Kesselsensor", "Aussensensor", "Innensensor", "Brauchwassersensor", "Brennersensor"]
# Liste damit man alle Sensoren in einer Schleife bearbeiten kann.
# wird in den Sensorklassen befüllt
SensorList = []

# Liste aller Sensortabellen
SENSORTABLELIST = ["Kesselsensor", "Aussensensor", "Innensensor", "Brauchwassersensor", "Brennersensor"]


# Sensor Dictionary um jede Sensorklasse mit der richtigen Formel zu versorgen, sonst muss der 
# Code für jede Class kopiert werden.
sensordict = {
    "Kesselsensor" : "(-7.79670769172508*pow(rt,3)) + (39.9983314997706*pow(rt,2)) + (-109.299890516815*rt) + 163.716704847826",
    "Aussensensor" : "(-2.1331945*pow(rt,3)) + (16.44056044*pow(rt,2)) - (57.79703416*rt) + 104.0119689",
    "Innensensor" : "",
    "Brauchwassersensor" : "(-7.796707692*pow(rt,3)) + (39.9983315*pow(rt,2)) - (109.2998905*rt) +163.7167048"
}
# Dictinary für die Sensor Dummy Werte wenn V_Mode=True
rawvaluedict = {
    "Kesselsensor" : 2.38,
    "Aussensensor" : 3.57,
    "Innensensor" : 4350,
    "Brauchwassersensor" : 2.38
}

# Arbeitstabellenname
tablename=None

# Liste aller Tabellen die man sonst so braucht
TableList = []

# Schaltet die virtuellen Sensoren / Daten ein um alles ohne Sensoren testen 
# zu können False = Echte Daten, True = Fakedaten
V_Mode = False

# Liste aller Threads, vielleicht kann man die ja noch brauchen
ThreadList = [] 

# Alle gloalen Variablen, die für die Anzeigeschicht gebraucht werden
# 
Winter_j_n : bool
Kessel : float
Bauchwasser : float
Innen : float
Punmpe_oben_an : bool
Pumpe_unten_an : bool
Pumpe_Bauchwasser_an : bool
Brenner_an : bool
Brenner_Stoerung : bool
Hand_Dusche : bool

# Init der globalen Variablen
def init_vars():
    Winter_j_n = True
    Kessel = 0
    Bauchwasser = 0
    Innen = 0
    Punmpe_oben_an = False
    Pumpe_unten_an = False
    Pumpe_Bauchwasser_an = False
    Brenner_an = False
    Brenner_Stoerung = False
    Hand_Dusche = False
