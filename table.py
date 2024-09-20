
# Hier wird die Basisklasse für alle Tabellen definiert. Sie wird dann an weitere Klassen vererbt
# Tables
#       Sensoren(Aussen Innen Brauchwasser Kessel) -> OK
#       KesselSoll -> OK
#       Brennersensor -> OK
#       Zeitsteuerung -> OK
#       Workdataview -> OK
#       
# Die Tables Class soll, Tabellen Anlegen, löschen, prüfen ob sie Inhalt haben 
# Sie hat als Pararmeter den Tabellennamen, die beiden SQL Teile zur Anlage der Tabelle

import logging
import settings
import sqlite3
from sqlite3 import Error
import time




class Tables:

    def __init__(self, tablename,sql_p1,sql_p2) -> None:
        self.tablename=tablename
        self.sql_p1=sql_p1
        self.sql_p2=sql_p2
        # Tabelle Anlegen

    # Tabelle anlegen wenn sie noch nicht existiert
    def _create_table(self):

        try:
            conn = sqlite3.connect(settings.DBPATH)
            logging.info('DB-Verbindung geöffnet')
            
        except Error as e:
            logging.error('Es konnte keine Verbindung zu Datenbank erstellt werden. Programm wird beendet')
            exit(1)
        try:
            c = conn.cursor()
            create_table_sql = self.sql_p1 + self.tablename + self.sql_p2
            c.execute(create_table_sql)
            conn.commit()
            conn.close()
            logging.info('Tabelle: ' + self.tablename +' erstellt')
        except Error as e:
            logging.error('Es konnte kein Cursor in der Datenbank erstellt werden um die Tabellen zu erzeugen. Programm wird beendet!')
            exit(1)
        return

        
    # Tabelle mit Inhalt löschen
    def _drop_table(self):
        
        try:
            conn = sqlite3.connect(settings.DBPATH)
            logging.info('DB-Verbindung geöffnet')
            cursor= conn.cursor()
            cursor.execute("DROP TABLE ",self.tablename)
            conn.commit()
            conn.close()
            logging.info('Tabelle '+self.tablename+' gelöscht.')
        except Error as e:
            logging.error('Tabelle '+self.tablename+' konte nicht gelöscht werden.')
            exit(1)
        finally:
            return(True)


    # Tabelleninhalt löschen
    def _empty_table(self):
        try:
            conn = sqlite3.connect(settings.DBPATH)
            logging.info('DB-Verbindung geöffnet')
            cursor= conn.cursor()
            cursor.execute("DELETE FROM ",self.tablename)
            conn.commit()
            conn.close()
        except Error as e:
            logging.error('Daten in '+self.tablename+' konten nicht gelöscht werden.')
            exit(1)
        finally:
            logging.info('Daten in '+self.tablename+' gelöscht.')
            return(True)

    # Tabelle initialisieren
    def _init_table(self,init_sql, data):
        try:
            conn = sqlite3.connect(settings.DBPATH)
            logging.info('DB-Verbindung geöffnet')
            
        except Error as e:
            logging.error('Es konnte keine Verbindung zur Datenbank erstellt werden. Programm wird beendet')
            exit(1)
        try:
            c = conn.cursor()
            c.execute(init_sql,data)
            conn.commit()
            conn.close()
            logging.info('Tabelle initialisiert')
        except Error as e:
            logging.error('Es konnte das SQL nicht ausgeführt werden:'+ init_sql + 'Daten:'+ str(data)+ ' Programm wird beendet!')
            exit(1)
        return  


    # Prüft ob Daten in der Tabelle sind
    # False= keine Daten drin
    # True = Daten in der Tabelle
    def _checktable(self)->bool:
        
        t=0
        try:
            conn = sqlite3.connect(settings.DBPATH)
            logging.info('DB-Verbindung geöffnet')
            
        except Error as e:
            logging.error('Es konnte keine Verbindung zur Datenbank erstellt werden. Programm wird beendet')
            exit(1)
        try:
            c = conn.cursor()
            # prüfen ob Tabelle existiert
            t= c.execute(f"SELECT EXISTS(SELECT name FROM sqlite_master WHERE type='table' AND name = '{self.tablename}');").fetchone()[0]
            # prüfen ob Tabelle einen Inhalt hat
            if t==1:
                t=c.execute(f"SELECT COUNT(*) FROM {self.tablename}").fetchone()[0]
            conn.close()
            logging.info('Tabelle '+self.tablename+' enthält :'+str(t)+' Datensätze')
            if t>0 :
                erg=True
            else:
                erg=False
        except Error as e:
            logging.info('Es konnte die Tabelle '+ self.tablename +' nicht abgefragt werden!')
                
        return (erg)




# legt die Tabelle an wenn nötig, füllt sie wenn nötig
class KesselSollTemperatur(Tables):

    def __init__(self, tablename,sql_p1,sql_p2):
        super().__init__(tablename,sql_p1,sql_p2)
        self._create_table()
        if self._checktable()==False:
            self._init_Kesselvalues()

    def _init_Kesselvalues(self):
        # k wird als Variable in der Formel settings.KesselKennlinie verwendet
        k=0
        # alles mal 10, damit man range() mit int verwenden kann.
        # die Kennlinie geht von -30 bis 30 Grad Schritt 0.5
        for i in range(int(settings.AussenMinTemp*10),int(settings.AussenMaxTemp*10),int(settings.AussenTempStep*10)):
            x= float(i/10)
            y=round(eval(settings.KesselKennlinie),1)
            # die Daten müssen nun in die Datenbank
            data=(x,y)
            sql = settings.sql_init_Kesselkennlinie
            self._init_table(sql,data)
        

# Zeitsteurungstabelle anlegen, und mit einem Defaultprogramm füllen
# wenn die Tabelle nicht leer ist
class Zeitsteuerung(Tables):
    def __init__(self, tablename,sql_p1,sql_p2):
        super().__init__(tablename,sql_p1,sql_p2)
        # Zeitsteuertabelle (Brauchwasser, Heizen, Nachtabsenkung, von, bis) ggf. erzeugen
        # kein checktable notwendig, da das der SQL befehl selbst erledigt, 
        # wird nur wegen der Initialisierung bnötigt.
        self._create_table()
        # hier muss jetzt noch ein Init hin, damit in der Tabelle ein Grundprogramm drin ist 
        if self._checktable()==False:
            for i in settings.Standardprogramm:
                self._init_table(settings.sql_writezeitsteuerung,i)

# Brennerberiebs Logging Table anlegen
# Tabelle für die Zustände des Brennersensors
class Brennersensor(Tables):
    def __init__(self, tablename,sql_p1,sql_p2):
        super().__init__(tablename,sql_p1,sql_p2)   
        self._create_table()


class WorkdataView(Tables):
    def __init__(self, tablename,sql_p1,sql_p2):
        super().__init__(tablename,sql_p1,sql_p2) 
        self._create_table()
        if self._checktable()==False:
            
            # so nun mal ein paar Init-datenschreiben und wenn noch nicht da die erste 
            # und einzige Zeile dieser Tabelle erzeugen
            # init_WorkDataView_sql = "INSERT or REPLACE INTO .... 
            # und zusätzlich noch zu jedem Wert die Zeit.

            t=time.time_ns()
            data=(1, t, \
                settings.Winter, t, \
                settings.Wintertemp, t,\
                settings.Kessel, t, \
                settings.KesselSoll, t,\
                settings.Brauchwasser, t,\
                settings.BrauchwasserSoll,t,\
                settings.BrauchwasserAus,t, \
                settings.Innen,  t,\
                settings.Aussen, t,\
                settings.Pumpe_oben_an, t,\
                settings.Pumpe_unten_an, t,\
                settings.Pumpe_Brauchwasser_an, t,\
                settings.Brenner_an, t,\
                settings.Brenner_Stoerung, t,\
                settings.Hand_Dusche, t,\
                settings.threadstop )
            # so, die Tabelle existiert. Initdaten sind reingeschrieben.
            self._init_table(settings.init_WorkDataView_sql,data)

