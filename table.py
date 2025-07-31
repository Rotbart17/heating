
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

    def __init__(self, tablename: str, sql_columns: str) -> None:
        """Initialisiert die Tabellen-Basisklasse."""
        self.tablename=tablename
        self.sql_columns = sql_columns

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
            create_table_sql = f"CREATE TABLE IF NOT EXISTS {self.tablename} {self.sql_columns}"
            c.execute(create_table_sql)
            conn.commit()
            conn.close()
            logging.info(f'Tabelle: {self.tablename} erstellt')
        except Error as e:
            logging.error(f'Beim erzeugen von: {self.tablename} + ist Fehler {e} aufgetreten. Programm wird beendet!')
            exit(1)
        return

        

    def _drop_table(self):
        ''' Tabelle löschen'''
        try:
            # SQL-Identifier wie Tabellennamen können nicht durch Platzhalter (?) ersetzt werden.
            # Sie müssen sicher in den SQL-String eingefügt werden.
            # Da der Tabellenname intern verwaltet wird, ist die Verwendung eines f-Strings hier unbedenklich.
            sql = f"DROP TABLE IF EXISTS {self.tablename}"
            with sqlite3.connect(settings.DBPATH) as conn:
                logging.info(f"DB-Verbindung für DROP TABLE '{self.tablename}' geöffnet")
                cursor = conn.cursor()
                cursor.execute(sql)
            logging.info(f"Tabelle '{self.tablename}' erfolgreich gelöscht.")
            return True
        except Error as e:
            logging.error(f"Fehler beim Löschen der Tabelle '{self.tablename}': {e}")
            # Die ursprüngliche Exception wird weitergeleitet, um dem aufrufenden Code die Fehlerbehandlung zu ermöglichen.
            raise


  
    def _empty_table(self):
        ''' Tabelle leeren'''
        try:
            with sqlite3.connect(settings.DBPATH) as conn:
                logging.info('DB-Verbindung geöffnet')
                cursor = conn.cursor()
                sql = f"DELETE FROM {self.tablename}"
                cursor.execute(sql)
            logging.info(f'Daten in {self.tablename} gelöscht.')
            return True
        except Error as e:
            logging.error(f'Daten in {self.tablename} konnten nicht gelöscht werden.')
            raise Exception from e

   
    def _init_table(self,init_sql, data):
        ''' Tabelle initialisieren'''

        try:
            conn = sqlite3.connect(settings.DBPATH)
            logging.info('DB-Verbindung geöffnet')
            
        except Error as e:
            logging.error(f'Es konnte keine Verbindung zur Datenbank {settings.DBPATH} erstellt werden. Programm wird beendet')
            exit(1)
        try:
            c = conn.cursor()
            c.execute(init_sql,data)
            conn.commit()
            conn.close()
            logging.info('Tabelle initialisiert')
        except Error as e:
            logging.error(f'Es konnte das SQL nicht ausgeführt werden:{init_sql} Daten: {str(data)} Fehler:{str(e)}')
            exit(1)
        return  



    def _checktable(self)->bool:
        '''    Prüft ob Daten in der Tabelle sind
               False= keine Daten drin
               True = Daten in der Tabelle'''
        
        t=0
        erg=False
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
            logging.info(f'Tabelle {self.tablename} enthält :{str(t)} Datensätze')
            if t>0 :
                erg=True
            else:
                erg=False
        except Error as e:
            logging.info(f'Es konnte die Tabelle {self.tablename} nicht abgefragt werden!')
                
        return (erg)


class KesselSollTemperatur(Tables):
    '''legt die KesselSolTemperatur Tabelle an wenn nötig, füllt sie wenn nötig'''
    def __init__(self, tablename: str, sql_columns: str):
        super().__init__(tablename, sql_columns)
        self._create_table()
        if self._checktable()==False:
            self._init_Kesselvalues()

    def _init_Kesselvalues(self):
        ''' k wird als Variable in der Formel settings.KesselKennlinie verwendet
         alles mal 10, damit man range() mit int verwenden kann.
         die Kennlinie geht von -30 bis 30 Grad Schritt 0.5'''
        for i in range(int(settings.AussenMinTemp*10),int(settings.AussenMaxTemp*10),int(settings.AussenTempStep*10)):
            x= float(i/10)
            y=round(eval(settings.KesselKennlinie),1)
            # die Daten müssen nun in die Datenbank
            data=(x,y)
            sql = settings.sql_init_Kesselkennlinie
            self._init_table(sql,data)
        


class Zeitsteuerung(Tables):
    '''Zeitsteurungstabelle anlegen, und mit einem Defaultprogramm füllen
       wenn die Tabelle nicht leer ist'''
       
    def __init__(self, tablename: str, sql_columns: str):
        super().__init__(tablename, sql_columns)
        # Zeitsteuertabelle (Brauchwasser, Heizen, Nachtabsenkung, von, bis) ggf. erzeugen
        # kein checktable notwendig, da das der SQL befehl selbst erledigt, 
        # wird nur wegen der Initialisierung bnötigt.
        self._create_table()
        # hier muss jetzt noch ein Init hin, damit in der Tabelle ein Grundprogramm drin ist 
        if self._checktable()==False:
            for i in settings.Standardprogramm:
                self._init_table(settings.sql_writezeitsteuerung,i)


class Brennersensor(Tables):
    '''Brennerberiebs Logging Tabelle anlegen
        Tabelle für die Zustände des Brennersensors'''
    def __init__(self, tablename: str, sql_columns: str):
        super().__init__(tablename, sql_columns)
        self._create_table()


class WorkdataView(Tables):
    '''WorkdataView Tabelle und Default Inhalt anlegen'''
    def __init__(self, tablename: str, sql_columns: str):
        super().__init__(tablename, sql_columns)
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
                settings.Heizen, t, \
                settings.Nachtabsenkung, t, \
                settings.Brauchwasser, t,\
                settings.BrauchwasserSoll,t,\
                settings.BrauchwasserAus,t, \
                settings.Brauchwasserbereiten, t, \
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
