
# hier sind slle globalen Variablen und verwendeten Basiseinstellungen gesammelt

import logging
from time import time


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

# Sensornames ["Kesselsensor", "Aussensensor", "Innensensor", "Brauchwassersensor"]
# Liste damit man alle Temperatur-Sensoren in einer Schleife bearbeiten kann.
# wird in den Sensorklassen befüllt mit den einzelnen Sensor Threads
# Es braucht auch noch einen Brenner Sensor: Brennersensor Der Thread mit dem Brennersensor kann auch in die Liste
SensorList = []


# Liste aller Temperatursensorentabellen
# außer , "Brennersensor"
# 
TemperaturSensorList = ["Kesselsensor", "Aussensensor", "Innensensor", "Brauchwassersensor"]


# Sensor Dictionary um jede Sensorklasse mit der richtigen Formel zu versorgen, sonst muss der 
# Code für jede Class kopiert werden.
# DieFormel übersetzt die Messwerte (Tabelle aus dem Handbuch) in Temperaturen

sensordict = {
    "Kesselsensor" : "(-7.79670769172508*pow(rt,3)) + (39.9983314997706*pow(rt,2)) + (-109.299890516815*rt) + 163.716704847826",
    "Aussensensor" : "(-2.1331945*pow(rt,3)) + (16.44056044*pow(rt,2)) - (57.79703416*rt) + 104.0119689",
    "Innensensor" : "(-0.05*rt+235.5)",
    "Brauchwassersensor" : "(-7.796707692*pow(rt,3)) + (39.9983315*pow(rt,2)) - (109.2998905*rt) +163.7167048"
}

# Dictionary für die Sensor Dummy Werte wenn V_Mode=True. Es sind Werte die entsprechend umgerechnet werden 
# müssen, damit die Formeln auch ausgetestet werden, Wenn auch mom. nur mit einem Wert. 
rawvaluedict = {
    "Kesselsensor" : 2.44,
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
# Heizen: soll geheizt werden
# Nachtabsenkung: Ist die Nachabsenkung an?
Kesselsensor="Kesselsensor"
Kessel : float = 0
KesselSoll : float = 0
KesselMax : float = 90
Heizen : int= False
Nachtabsenkung : int =True

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
sql_write_KesselKennlinie_x = f"UPDATE  {KesselSollTemperatur}  SET value_x= ? WHERE id = ? ;"
sql_write_KesselKennlinie_y = f"UPDATE  {KesselSollTemperatur}  SET value_y= ? WHERE id = ? ;"

# Variablen um die aktuelle Kesselkennlinie für die Anzeige zu speichern
KesselDaten_x=[]
KesselDaten_y=[]



# Temperaturkonstanten für die Kesselkennlinie
# um die Rangefunktion verwenden zu können ist jeder Wert mit 10 
# multipliziert -30 bis 30Grad, Schrittweite 0,5 Grad (Faktor 10 um normale Schleifen 
# zu verwenden)
Aussensensor="Aussensensor"
AussenMinTemp : int = -30
AussenMaxTemp : int = 30
AussenTempStep : int = 0.5
# Aussen ist die aktuelle Aussentemperatur, wird nur vom Sensor verändert, GUI zeigt an
Aussen : float = 0


# Brauchwasser ist die aktuelle Brauchwassertemperatur, kommt vom Sensor, wird nur gelesen
# BrauchwasserSoll ist die Solltemperatur des Brauchwassers, Wird in der GUI eingestellt und nur dort geschrieben
# BrauchwasserError ist die Temperatur bei der ein Fehler ausgelöst wird, Fixwert hier im Programm
# BrauchwasserAus ist für das generelle ausschalten des Brauchwasser
Brauchwassersensor="Brauchwassersensor"
Brauchwasser : float = 0
BrauchwasserSoll : float = 55
BrauchwasserError : float = 70
BrauchwasserAus : bool = False
Brauchwasserbereiten :bool = False

# Pumpe_Brauchwasser_an wird von dem Prozess der Brauchwasser überwachung verändert. GUI zeigt nur an.
Pumpe_Brauchwasser_an : bool = False
# Schaltet die manuelle Brauchwasserbereitung ein. Wird nur in der GUI verändert.
Hand_Dusche : bool = False

# Innen ist die aktuelle Innentemperatur, wird nur vom Sensor verändert, GUI zeigt an
Innensensor="Innensensor"
Innen : float = 0

# Signalisiert ob die Pumpen an / aus. Werden nur vom Regelkreis verändert, GUI zeigt an
Pumpe_oben_an : bool = False
Pumpe_unten_an : bool = False



# die Tabelle der Anzeigeschicht heisst:----------
WorkDataView = "WorkDataView"

# SQL Statement für die Tabelle der Anxzeigeschicht
# changetime ist der Zeitpunkt der letzten Änderung in ns
# ViewChange ist der Zeitpunkt an dem die letzte Änderung an irgendeiner Stelle im View
# vorgenommen wurde
sql_create_view_table_p1 = "CREATE TABLE IF NOT EXISTS " 
sql_create_view_table_p2 = " (id integer PRIMARY KEY AUTOINCREMENT NOT NULL,  \
                                ViewChanged int, \
                                Winter int,              \
                                Winter_changetime int,              \
                                Wintertemp real,           \
                                Wintertemp_changetime int,           \
                                Kessel real,         \
                                Kessel_changetime int,         \
                                KesselSoll real,   \
                                KesselSoll_changetime int,   \
                                Heizen int, \
                                Heizen_changetime int, \
                                Nachtabsenkung int, \
                                Nachtabsenkung_changetime int, \
                                Brauchwasser real,           \
                                Brauchwasser_changetime int,           \
                                BrauchwasserSoll real,   \
                                BrauchwasserSoll_changetime int,   \
                                BrauchwasserAus int,   \
                                BrauchwasserAus_changetime int,  \
                                Brauchwasserbereiten int,  \
                                Brauchwasserbereiten_changetime int, \
                                Innen real,           \
                                Innen_changetime int,           \
                                Aussen real,           \
                                Aussen_changetime int,           \
                                Pumpe_oben_an int,           \
                                Pumpe_oben_an_changetime int,           \
                                Pumpe_unten_an int,           \
                                Pumpe_unten_an_changetime int,           \
                                Pumpe_Brauchwasser_an int,           \
                                Pumpe_Brauchwasser_an_changetime int,           \
                                Brenner_an int,           \
                                Brenner_an_changetime int,           \
                                Brenner_Stoerung int,           \
                                Brenner_Stoerung_changetime int,           \
                                Hand_Dusche int,            \
                                Hand_Dusche_changetime int,            \
                                threadstop int  \
                            ); "

# InitWorkDataView SQL, schreibt die erste Zeile mit Basiswerten
init_WorkDataView_sql = f"INSERT OR REPLACE INTO {WorkDataView} (\
                            id, Viewchanged, \
                            Winter, Winter_changetime,\
                            Wintertemp, Wintertemp_changetime,\
                            Kessel, Kessel_changetime, \
                            KesselSoll, KesselSoll_changetime,\
                            Heizen, Heizen_changetime, \
                            Nachtabsenkung, Nachtabsenkung_changetime, \
                            Brauchwasser, Brauchwasser_changetime, \
                            BrauchwasserSoll, BrauchwasserSoll_changetime,\
                            BrauchwasserAus, BrauchwasserAus_changetime,  \
                            Brauchwasserbereiten, Brauchwasserbereiten_changetime, \
                            Innen, Innen_changetime, \
                            Aussen, Aussen_changetime, \
                            Pumpe_oben_an, Pumpe_oben_an_changetime,\
                            Pumpe_unten_an, Pumpe_unten_an_changetime,\
                            Pumpe_Brauchwasser_an, Pumpe_Brauchwasser_an_changetime,\
                            Brenner_an, Brenner_an_changetime,\
                            Brenner_Stoerung, Brenner_Stoerung_changetime,\
                            Hand_Dusche, Hand_Dusche_changetime,\
                            threadstop ) \
                        VALUES(:id, :Viewchanged, \
                            :Winter, :Winter_changetime, \
                            :Wintertemp, :Wintertemp_changetime,\
                            :Kessel, :Kessel_changetime,\
                            :KesselSoll,:KesselSoll_changetime,\
                            :Heizen,:Heizen_changetime,\
                            :Nachtabsenkung, :Nachtabsenkung_changetime, \
                            :Brauchwasser, :Brauchwasser_changetime, \
                            :BrauchwasserSoll, :BrauchwasserSoll_changetime,\
                            :BrauchwasserAus, :BrauchwasserAus_changetime,  \
                            :Brauchwasserbereiten, :Brauchwasserbereiten_changetime, \
                            :Innen, :Innen_changetime, \
                            :Aussen, :Aussen_changetime, \
                            :Pumpe_oben_an, :Pumpe_oben_an_changetime,\
                            :Pumpe_unten_an, :Pumpe_unten_an_changetime,\
                            :Pumpe_Brauchwasser_an, :Pumpe_Brauchwasser_an_changetime,\
                            :Brenner_an, :Brenner_an_changetime,\
                            :Brenner_Stoerung, :Brenner_Stoerung_changetime,\
                            :Hand_Dusche, :Hand_Dusche_changetime,\
                            :threadstop);"

write_WorkDataView_value= f"UPDATE {WorkDataView} SET ?=? WHERE id=1;"
read_WorkDataView_complete= f"SELECT * from {WorkDataView} WHERE id =1 ;"



# Loginfo -> noch unklar
# löscht Fehlerstatus -> noch unklar



# Statements um die Sensortabelle für alle Temperatursensoren zu erzeugen
sql_create_sensor_table_p1 = "CREATE TABLE IF NOT EXISTS " 
sql_create_sensor_table_p2 = " (id integer PRIMARY KEY AUTOINCREMENT NOT NULL,  \
                                value real,              \
                                begin_date int,         \
                                end_date int,           \
                                error int            \
                            ); "
                



# die Tabelle für die Zeitsteuerung heisst:----------
ZeitSteuerung="ZeitSteuerung"
sql_zeitsteuerung_p1=sql_create_view_table_p1
sql_zeitsteuerung_p2=" (line_id integer,      \
                        type text,           \
                        tage text,           \
                        von text,            \
                        bis text,             \
                        active int,           \
                        changetime int,       \
                        );"
sql_readzeitsteuerung=f"SELECT line_id, type, tage, von, bis, active, changetime FROM {ZeitSteuerung};"
sql_writezeitsteuerung=f"INSERT OR REPLACE INTO {ZeitSteuerung} (line_id, type, tage, von, bis, active, changetime)  VALUES (:line_id,:type,:tage,:von,:bis,:active,:changetime);"
sql_deletezeitsteuerung=f"DELETE from {ZeitSteuerung};"

# als Programm brauchen wir 
# Montag-Sonntag Nachtabsenkung 22:00-7:00,inaktiv, keine Zeit
# Brauchwasser Mo-Fr 6:00-9.00,inaktiv, keine Zeit
# Brauchwasser Sa,So 6:00-9:00,inaktiv, keine Zeit
# Brauchwasser Sa,So 16:00-19:00,inaktiv, keine Zeit
# Heizbetrieb Mo-So 00:00-24:00,inaktiv, keine Zeit
changetime=time.time_ns()
Standardprogramm = [ (1,'Nachtabsenk.','Mo-So','22:00','7:00',0,{changetime}), \
                     (2,'Brauchw','Mo-Fr','6:00','9:00',0,{changetime}), \
                     (3,'Brauchw','Sa-So','6:00','9:00',0,{changetime}), \
                     (4,'Brauchw','Sa-So','16:00','19:00',0,{changetime}), \
                     (5,'Heizen','Mo-So','00:00','23:59',0,{changetime})   ]



# Signalisiert ob der Brenner an ist und ob es eie Störung gibt
# Brenner_an zeigt, dass Brenner läuft. Wird nur vom Regelkreis verändert, GUI zeigt an
Brenner_an : bool = False
# Brenner_Störung zeigt eine Brennerstörung wird nur vom Brenner verändert, GUI zeigt an
Brenner_Stoerung : bool = False

# Die Varianblen für die Brennersensortabelle ----------
Brennersensor="Brennersensor"
sql_brennersensor_p1=sql_create_view_table_p1
sql_brennersensor_p2=" (id integer PRIMARY KEY AUTOINCREMENT NOT NULL,  \
                                brenner_an int,           \
                                brenner_stoerung int,  \
                                von text,            \
                                bis text             \
                        );"
sql_readbrennersensor=f"SELECT von FROM {Brennersensor} WHERE von >= ? AND brenner_an='True';"
sql_writebrennersensorbetrieb=f"INSERT INTO {Brennersensor} brenner_an=?, von=?, bis=?;"
sql_writebrennersensorstoerung=f"INSERT INTO {Brennersensor} brenner_stoerung=?, von=?, bis=?;"