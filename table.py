
# Hier wird die Basisklasse für alle Tabellen definiert. Sie wird dann an weitere Kalssen vererbt
# Tables
#       Sensoren(Aussen Innen Brauchwasser Kessel) -> OK
#       KesselSoll -> OK
#       Zeitsteuerung
#       Workdataview <- Das ist schwierig, da das jetzt schon eine Datenklasse ist.
#       Brennersensor
# Die Tables Class soll, Tabellen Anlegen, löschen, prüfen ob sie Inhalt haben 
# Sie hat als Pararmeter den Tabellennamen, die beiden Teile zur Anlage der Tabelle

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
    def _checktable(self):
        
        t=0
        try:
            conn = sqlite3.connect(settings.DBPATH)
            logging.info('DB-Verbindung geöffnet')
            
        except Error as e:
            logging.error('Es konnte keine Verbindung zur Datenbank erstellt werden. Programm wird beendet')
            exit(1)
        try:
            c = conn.cursor()
            # t=c.execute(f"SELECT COUNT(*) FROM {tablename}").fetchone()[0]
            t= c.execute(f"SELECT EXISTS(SELECT name FROM sqlite_master WHERE type='table' AND name = '{self.tablename}');").fetchone()[0]
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
        if self._checktable(self.tablename)==False:
            self._create_table(self.tablename,sql_p1,sql_p2)
            self._init_Kesselvalues(self.tablename)

    def _init_Kesselvalues(self,name):
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
class Zeitsteuerung(Tables):
    def __init__(self, tablename,sql_p1,sql_p2):
        super().__init__(tablename,sql_p1,sql_p2)
        # Zeitsteuertabelle (Brauchwasser, Heizen , Nachtabsenkung, von, bis) ggf. erzeugen
        # kein checktable notwendig, da das der SQL befehl selbst erledigt, 
        # wird nur wegen der Initialisierung bnötigt.
        self._create_table(self.tablename,sql_p1,sql_p2)
        # hier muss jetzt noch ein Init hin, damit in der Tabelle ein Grundprogramm drin ist      
        for i in settings.Standardprogramm:
            self._init_table(settings.sql_writezeitsteuerung,settings.Standardprogramm[i])

# Brennerberiebs Logging Table anlegen
class Brennersensor(Tables):
    def __init__(self, tablename,sql_p1,sql_p2):
        super().__init__(tablename,sql_p1,sql_p2)   
        self._create_table(self.tablename, settings.sql_brennersensor_p1,settings.sql_brennersensor_p2)
