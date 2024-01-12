
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
    # filemode='w',
    format='%(asctime)s %(levelname)s: %(message)s',
    level=logging.ERROR
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
# DieFormel übersetzt die Messwerte (Tabelle aus dem Handbuch) in Temperaturen

sensordict = {
    "Kesselsensor" : "(-7.79670769172508*pow(rt,3)) + (39.9983314997706*pow(rt,2)) + (-109.299890516815*rt) + 163.716704847826",
    "Aussensensor" : "(-2.1331945*pow(rt,3)) + (16.44056044*pow(rt,2)) - (57.79703416*rt) + 104.0119689",
    "Innensensor" : "(-0.05*rt+235.5)",
    "Brauchwassersensor" : "(-7.796707692*pow(rt,3)) + (39.9983315*pow(rt,2)) - (109.2998905*rt) +163.7167048"
}
# Dictinary für die Sensor Dummy Werte wenn V_Mode=True. Es sind Werte die entsprechend umgerechnet werden 
# müssen, damit die Formeln auch ausgetestet werden, Wenn auch mom. nur mit einem Wert. 
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
# TRUE bewirkt das stoppen aller Threads
threadstop : bool = False
# Alle gloalen Variablen, die für die Anzeigeschicht gebraucht werden
# Init der Anzeige Tabelle und der Steuerwerte

# Bei Winter == True haben wir Heizbetrieb
# Wintertemp ist die Temperatur bei der auf Heizbetrieb geschaltet wird
# Winter wird in Abhängigkeit von der Wintertemp automatisch gesetzt. Und von der GUI
# in geschrieben.
# Wintertemp wird nur von der GUI verändert

Winter : bool = True
Wintertemp: float = 17

# Kessel ist die aktuelle Kesseltemperatur, kommt vom Sensor, wird nur gelesen
# KesselSoll ist die KesselSolltemperatur, wird mit der Kurve ermittelt. Kurve wird in der Gui angepasst
# die aktuelle KesselSoll wird nur angezeigt und im Regelkreis gesetzt
# und nur von dort verändert.
# KesselMax ist die Temperatur bei der ein Fehler ausgelöst wird. Fixwert hier im Programm, wird nur gelesen
Kessel : float = 0
KesselSoll : float = 0
KesselMax : float = 90
# Temperaturkonstanten für die Kesselkennlinie
# um die Rangefunktion verwenden zu können ist jeder Wert mit 10 
# multipliziert -30 bis 30Grad, Schrittweite 0,5 Grad (Faktor 10 um normale Schleifen 
# zu verwenden)
AussenMinTemp : int = -30
AussenMaxTemp : int = 30
AussenTempStep : int = 0.5


# Brauchwasser ist die aktuelle Brauchwassertemperatur, kommt vom Sensor, wird nur gelesen
# BrauchwasserSoll ist die Solltemperatur des Brauchwassers, Wird in der GUI eingestellt und nur dort geschrieben
# BrauchwasserError ist die Temperatur bei der ein Fehler ausgelöst wird, Fixwert hier im Programm
Brauchwasser :float = 0
BrauchwasserSoll : float = 55
BrauchwasserError : float = 70

# Pumpe_Brauchwasser_an wird von dem Prozess der Brauchwasser überwachung verändert. GUI zeigt nur an.
Pumpe_Brauchwasser_an : bool = False
# Schaltet die manuelle Brauchwasserbereitung ein. Wird nur in der GUI verändert.
Hand_Dusche : bool = False

# Innen ist die aktuelle Innentemperatur, wird nur vom Sensor verändert, GUI zeigt an
Innen : float = 0
# Aussen ist die aktuelle Aussentemperatur, wird nur vom Sensor verändert, GUI zeigt an
Aussen : float = 0

# Signalisiert ob die Pumpen an / aus. Werden nur vom Regelkreis verändert, GUI zeigt an
Pumpe_oben_an : bool = False
Pumpe_unten_an : bool = False

# Signalisiert ob der Brenner an ist und ob es eie Störung gibt
# Brenner_an zeigt, dass Brenner läuft. Wird nur vom Regelkreis verändert, GUI zeigt an
Brenner_an : bool = False
# Brenner_Störung zeigt eine Brennerstörung wird nur vom Brenner verändert, GUI zeigt an
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
                                BrauchwasserSoll real,   \
                                Innen real,           \
                                Aussen real,           \
                                Pumpe_oben_an text,           \
                                Pumpe_unten_an text,           \
                                Pumpe_Brauchwasser_an text,           \
                                Brenner_an text,           \
                                Brenner_Stoerung text,           \
                                Hand_Dusche text,            \
                                threadstop text  \
                            ); "

# InitWorkDataView SQL, schreibt die erste Zeile mit Basiswerten
init_WorkDataView_sql = f"INSERT OR REPLACE INTO {WorkDataView} (\
                        id, Winter, Wintertemp, Kessel, KesselSoll, Brauchwasser, BrauchwasserSoll, Innen, Aussen,\
                        Pumpe_oben_an, Pumpe_unten_an, Pumpe_Brauchwasser_an, Brenner_an,\
                        Brenner_Stoerung, Hand_Dusche, threadstop ) \
                        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);"

write_Workdataview_value= f"UPDATE {WorkDataView} SET ?=? WHERE id=1;"

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
sql_init_Kesselkennlinie = f"INSERT OR REPLACE INTO {KesselSollTemperatur} (value_x, value_y) VALUES(?,?);"
sql_write_KesselKennlinie_x = f"UPDATE  {KesselSollTemperatur}  SET value_x= ? WHERE id = ? ;;"
sql_write_KesselKennlinie_y = f"UPDATE  {KesselSollTemperatur}  SET value_y= ? WHERE id = ? ;"

# Variablen um die aktuelle Kesselkennlinie für die Anzeige zu speichern
KesselDaten_x=[]
KesselDaten_y=[]

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

