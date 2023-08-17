
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
FastApiDBPath= "sqlite:///heizung.db"
FastApiAPPName = "Heizung"

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


# Schaltet die virtuellen Sensoren / Daten ein um alles ohne Sensoren testen 
# zu können False = Echte Daten, True = Fakedaten
V_Mode = False

# Liste aller Threads, vielleicht kann man die ja noch brauchen
ThreadList = [] 

# Alle gloalen Variablen, die für die Anzeigeschicht gebraucht werden
# Init der Anzeige Tabelle und der Steuerwerte

# Bei Winter == True haben wir Heizbetrieb
# Wintertemp ist die Temperatur bei der auf Heizbetrieb geschaltet wird
Winter : bool = True
Wintertemp: float =17

# Kessel ist die aktuelle Kesseltemperatur
# KesselSoll ist die KesselSolltemperatur
# KesselError ist die Temperatur bei der ein Fehler ausgelöst wird
Kessel : float = 0
KesselSoll : float = 0
KesselError : float = 90
x : float = 0 
y : float = 0

# Brauchwasser ist die aktuelle Brauchwassertemperatur
# BrauchwasserSoll ist die Solltemperatur des Brauchwassers
# BrauchwasserError ist die Temperatur bei der ein Fehler ausgelöst wird
Brauchwasser :float = 0
BrauchwasserSoll : float = 55
BrauchwasserError : float = 70
Pumpe_Brauchwasser_an : bool = False
Hand_Dusche : bool = False

# Innen ist die aktuelle Innentemperatur
Innen : float = 0
# Innen ist die aktuelle Aussentemperatur
Aussen : float = 0

# Signalisiert ob die Pumpen an /  aus sind
Pumpe_oben_an : bool = False
Pumpe_unten_an : bool = False

# Signalisiert ob der Brenner an ist und ob es eie Störung gibt
Brenner_an : bool = False
Brenner_Stoerung : bool = False



# die Tabelle der Anzeigeschicht heisst:----------
WorkDataView = "WorkDataView"

# SQL Statement für die Tabelle der Anxzeigeschicht
sql_create_view_table_p1 = "CREATE TABLE IF NOT EXISTS " 
sql_create_view_table_p2 = " (id integer PRIMARY KEY AUTOINCREMENT NOT NULL,  \
                                Winter text,              \
                                Wintertemp real,           \
                                Kessel real,         \
                                KesselSoll real,   \
                                Brauchwasser real,           \
                                Innen real,           \
                                Aussen real,           \
                                Pumpe_oben_an text,           \
                                Pumpe_unten_an text,           \
                                Pumpe_Brauchwasser_an text,           \
                                Brenner_an text,           \
                                Brenner_Stoerung text,           \
                                Hand_Dusche text            \
                            ); "

# InitWorkDataView SQL, schreibt die erste Zeile mit Basiswerten
init_WorkDataView_sql = f"INSERT or REPLACE INTO ? (\
                        id, Winter, Wintertemp, Kessel, KesselSoll, Brauchwasser, Innen, Aussen,   \
                        Pumpe_oben_an, Pumpe_unten_an, Pumpe_Brauchwasser_an, Brenner_an, \
                        Brenner_Stoerung, Hand_Dusche ) \
                        values( 1, ?,?,?,?,?,?,?,?,?,?,?,?,?);"


# Loginfo -> noch unklar
# löscht Fehlerstatus -> noch unklar


# die Tabelle der Kesseltemperatur Kennlinien Werte heisst:----------
KesselSollTemperatur="KesselSollTemperatur"
    
sql_kennlinie_p1="CREATE TABLE IF NOT EXISTS " 
sql_kennlinie_p2=" (id integer PRIMARY KEY AUTOINCREMENT NOT NULL,  \
                    value_x real,              \
                    value_y real           \
                    );"

# die Kennlinie für KesselSollTemperatur ist:
# Y=-1.2 x+56 + k
# Default für k=0:
# + 10 Grad => 44Grad
#    0 Grad => 56Grad
# - 10 Grad => 68Grad
# initial mit K=0 befüllen. Die Anpassungen erfolgen über die 
# GUI für jeden einzelnen Wert. Die Auswertung erfolgt mit eval(...)
KesselKennlinie="((-1.2)*x)+56 + k"
sql_init_Kesselkennlinie = "INSERT OR REPLACE INTO ? (value_x, value_y) VALUES(?,?);"

tankdataset_x=[]
tankdataset_y=[]

# die Tabelle für die Zeitsteuerung heisst:----------
ZeitSteuerung="ZeitSteuerung"
sql_zeitsteuerung_p1=sql_create_view_table_p1
sql_zeitsteuerung_p2=" (id integer PRIMARY KEY AUTOINCREMENT NOT NULL,  \
                                line_id integer,      \
                                type text,           \
                                tage text,           \
                                von text,            \
                                bis text             \
                        );"

