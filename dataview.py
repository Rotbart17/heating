#!/usr/bin/env python3
# in diesem Modul wird die Datenaustauschstruktur definiert
# sie versteckt die Datenbankzugriffe in einer Klasse
# so zumindest die Idee!

import settings
from dataclasses import dataclass, field
import logging
from dbinit import checktable, connect_db
import threading
import time
import sqlite3
from dataview_sensor import SensorView, sens
from dataview_kessel import KesselView
from dataview_zeitst import ZeitView
# from multiprocessing.queues import Queue as MPQueue
from typing import Any


# Muster für logging
# logging.debug('debug')
# logging.info('info')
# logging.warning('warning')
# logging.error('error')
# logging.critical('critical')

logging.basicConfig(
    filename='gui.log',
    filemode='w',
    format='%(asctime)s %(levelname)s: %(message)s',
    level=logging.ERROR
)

def str2bool(value):
    return {"True": True, "true": True}.get(value, False)

class ViewField:
    '''Zugriff auf ein Feld der Tabelle WorkDataView über die Variable _<name> der Datenklasse.
    Beim Setzen werden der Wert und der Zeitstempel zusätzlich in die DB geschrieben.'''

    def __init__(self, name:str) -> None:
        self.name = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, f"_{self.name}")

    def __set__(self, obj, value) -> None:
        setattr(obj, f"_{self.name}", value)
        timestamp = obj._writeitem(value, self.name, f"{self.name}_changetime")
        setattr(obj, f"_{self.name}_changetime", timestamp)


##### Start der Idee mit der Idee der Dataclass
@dataclass
class maindata(SensorView, KesselView, ZeitView):
    # Erkenntnis zu dataclass: wenn man einen Defaultvalue für eine Variable vergibt muss man das für alle
    # folgenden Variablen auch machen. Damit nehme ich nun die Werte, die ich in settings.py vergeben habe.
    # Wenn ich die Variablen verwende, dann wird alles ungültig, wenn ich die anderen teile auch für die Datenklasse umbaue.
    # Wenn ich nur die Werte verwende, habe ich sie an mehreren Orten :-( 
    # Fast alle hier gesetzten Werte werden werden beim ersten Lesen aus der DB überschrieben. Damit ist es sowieso egal.
    # Es bleibt aber nicht schön.
    # Wenn ich die Dataclass für alles verwende, dann kann ich die globalen Variablen reduzieren.

    start_polling : bool = True

    # damit man den thread stoppen kann
    threadstop : bool = False

    #Wartezeit in Sec bevor die nächste Abfrage des WorkdataView durchgeführt wird
    _sleeptime : int = 5

    # wenn Daten geschrieben werden mit dem Lesen warten, damit die Variable nicht
    # überschrieben wird, primitiv, aber hoffentlich ausreichend
    _datawrite: bool = False

    # Defaults werden in settings.py festgelegt ind in dbinit.py als Tabelle angelegt 
    # und von den Werten gesetzt

    # diser Wert wird beim Füllen der Variablen aus der Datenbank zuerst gesetzt
    # er dient als indikator ob sich in der DB etwas geändert hat und ob deswegen alle Variablen neu geladen werden müssen
    # falls er neu gesetzt wird bekommt er den Zeitwert von ViewChanged.
    # Wenn ein Prozess einen Wert in der Tabelle Wordataview ändert, wird der Wert auf den Zeit wert des 
    # veränderten Felds gesetzt
    _lastruntime :int = 0

    # Bei Winter == True haben wir Heizbetrieb
    # Wintertemp ist die Temperatur bei der auf Heizbetrieb geschaltet wird
    _Winter : bool = False
    _Wintertemp: float = 17
    _WintertempInnen: float = 20

    # Kessel ist die aktuelle Kesseltemperatur
    # KesselSoll ist die KesselSolltemperatur
    # KesselMax ist die Temperatur bei der ein Fehler ausgelöst wird
    # Heizen: soll geheizt werden
    # Nachabsenkung: soll die Temperatur Nachts abgesenkt werden?
    # KesselDaten_x und y ist die KesselSollkennlinie
    # die x und y Listen sind die Sensordaten nach x und y gesplittet. 
    # Die Grafikfunktion braucht diese Trennung
    _Kessel : float = 0
    _KesselSoll : float = 0
    _KesselMax : float = 90
    _Heizen : bool = False
    _Nachtabsenkung: bool = False
    _KesselDaten_x : list = field(default_factory=list)
    _KesselDaten_y : list = field(default_factory=list)
    #_KesselIstDaten_x : list = field(default_factory=list)
    #_KesselIstDaten_y : list = field(default_factory=list)


    # Brauchwasser ist die aktuelle Brauchwassertemperatur
    # BrauchwasserSoll ist die Solltemperatur des Brauchwassers
    # BrauchwasserError ist die Temperatur bei der ein Fehler ausgelöst wird
    # BrauchwasserAus ist Wahr wenn kein Brauchwasser erzeugt werden soll.
    _Brauchwasser : float = 0
    #_BrauchwasserDaten_x : list = field(default_factory=list)
    #_BrauchwasserDaten_y : list = field(default_factory=list)
    _BrauchwasserSoll : float = 55
    _BrauchwasserError : float = 70
    _BrauchwasserAus : bool = False
    _Brauchwasserbereiten : bool =False
    _Pumpe_Brauchwasser_an : bool =False
    _Hand_Dusche : bool = False

    # Legionellenschutz: wenn True soll das Brauchwasser auf LegionellenschutzSoll erhitzt werden,
    # unabhängig von BrauchwasserSoll. Wird von der Zeitsteuerung gesetzt.
    _Legionellenschutz : bool = False

    # Innen ist die aktuelle Innentemperatur
    _Innen : float = 0
    #_InnenDaten_x : list = field(default_factory=list)
    #_InnenDaten_y : list = field(default_factory=list)
    
    # Innen ist die aktuelle Aussentemperatur
    _Aussen : float = 0 
    #_AussenDaten_x : list = field(default_factory=list)
    #_AussenDaten_y : list = field(default_factory=list)

    # Signalisiert ob die Pumpen an /  aus sind
    _Pumpe_oben_an : bool = False
    _Pumpe_unten_an : bool = False

    # Signalisiert ob der Brenner an ist und ob es eie Störung gibt
    _Brenner_an : bool =False
    _Brenner_Stoerung : bool = False

    _VIEW_FIELDS = (
        "Winter",
        "Wintertemp",
        "WintertempInnen",
        "Kessel",
        "KesselSoll",
        "Heizen",
        "Nachtabsenkung",
        "Brauchwasser",
        "BrauchwasserSoll",
        "BrauchwasserAus",
        "Brauchwasserbereiten",
        "Legionellenschutz",
        "Innen",
        "Aussen",
        "Pumpe_oben_an",
        "Pumpe_unten_an",
        "Pumpe_Brauchwasser_an",
        "Brenner_an",
        "Brenner_Stoerung",
        "Hand_Dusche",
    )

    # Setzt für jeder Attribut die Changezeit, wenn sie neuer ist als die bekannte.
    # Force ist für die Initialisierung gesetzt
    def _update_view_field(self, results, name, force=False):
        value = results[name]
        changetime_name = f"{name}_changetime"
        changetime = results[changetime_name]

        attr = f"_{name}"
        changetime_attr = f"_{changetime_name}"

        if force or getattr(self, changetime_attr, 0) < changetime:
            setattr(self, attr, value)
            setattr(self, changetime_attr, changetime)

    # lädt die Daten aus der Datenbank aus der Tabelle WorkDataView 
    # in die klasseninternen Variablen
    def _viewloader(self, initialrun):
        try:
            with connect_db() as db:
                db.row_factory = sqlite3.Row
                results = db.execute(settings.read_WorkDataView_complete).fetchone()

            self._lastruntime = results["ViewChanged"]
            for field in self._VIEW_FIELDS:
                self._update_view_field(results, field, force=initialrun)

            self.threadstop = results["threadstop"]
        except sqlite3.Error as e:
            logging.error(f"Error {e} ist aufgetreten")
            raise

    # hier wird regelmäßig die DB abgefragt, damit immer frische Werte vorhanden sind
    # aber wenn gerade geschrieben wird, dann wird eine 1/50 sec gewartet. Vielleicht noch ein wenig viel.
    # schreiben hat Vorrang vor dem Lesen,
    # ein Argument muss man mitgeben...-> dummy
    def _dataviewpolling(self,dummy):
        while (self.threadstop ==False):
            if self._datawrite==False:
                
                try:
                    self._viewloader(False)
                except sqlite3.Error:
                    # Fehler ist schon geloggt, im nächsten Zyklus erneut versuchen
                    pass
                logging.debug('WorkdataView Pollen')
                self._sleep_until_stop(self._sleeptime)
            else:
                self._sleep_until_stop((self._sleeptime)/100)

    
    # hier müssen die aktuellen Werte aus der DB eingelesen werden.
    # da die GUI immer nach dem DB Modul gestartet wird, müssen 
    # hier Werte vorhanden sein. Sind sie es nicht, ist das ein fatler
    # Fehler
    def __post_init__(self):
    
        if checktable(settings.WorkDataView)==False:
            logging.error(f'Die Tabelle {settings.WorkDataView} existiert nicht. Programm wird beendet')
            raise RuntimeError(f'Die Tabelle {settings.WorkDataView} existiert nicht.')
        # jetzt die Daten zum ersten Mal aus der DB laden
        # Laden der historischen=letzten Werte der Sensoren (Aussen, Innen,Kessel, Brauchwasser)
        # die Defaults werden dabei überschrieben.
        self._viewloader(True)
        
        # Laden der initialen Kesselkennlinie
        self._kesseldataload()

        # Laden der initialen SensorWerte
        self._sensordataload()

        # Zeitsteuerung laden
        self._zeitsteuerungload()

        if self.start_polling == False:
            return
    
        # starten des Threads für das periodische Update der Dataview-Werte oder Initialisierung
        # ZZ brauche noch einen Ort an dem ich den Thread wieder einfange!
        # vielleicht beim löschen der Klasse?
        dummy=0    

        global dv_poll
        self.dv_poll = threading.Thread(target=self._dataviewpolling, name="Thread-GUI-DataView", args=(dummy,))
        logging.info('Starte DB-Abfrage dataview Thread!')
        self.dv_poll.start()
        logging.debug('DB-Abfrage Thread dataview gestartet!')

        self._start_sensor_thread()
    

    # scheibt jeden Wert einzeln in die DB zusammen mit den Zeitstempeln
    def _writeitem(self,value,name,namect):
        db=connect_db()
        try:
            self._datawrite=True
            cursor=db.cursor()
            timestamp=time.time_ns()
            # den neuen Wert und den Time Stamp zwei Mal schreiben damit klar ist, dass sich was geändert hat.
            sql= f"UPDATE {settings.WorkDataView} SET {name}={value},{namect}={timestamp}, \
                 ViewChanged={timestamp} WHERE id=1"
            cursor.execute(sql)
            db.commit()
            cursor.close()
            self._datawrite=False
            db.close()
            return(timestamp)
        except sqlite3.Error as e:
            logging.error(f"Der Fehler {e} ist beim Schreiben von {name}:{value} aufgetreten")
            db.close()
            raise

    def stop_polling(self) -> None:
        logging.debug('datav Klasse löschen,  Polling DB stop')
        self.threadstop = True

        for poll_thread in (getattr(self, 'dv_poll', None), getattr(self, 'sensor_poll', None)):
            if poll_thread is None or poll_thread.ident is None:
                continue
            if poll_thread is threading.current_thread():
                continue
            poll_thread.join(timeout=2)
            if poll_thread.is_alive():
                logging.warning(f"Thread {poll_thread.name} konnte nicht innerhalb des Timeouts beendet werden.")

    # Thread schliessen wenn Objekt gelöscht wird
    def __del__(self):
        self.stop_polling()
        logging.info("datav Klasse gelöscht, Polling gestoppt.")

    # Für jede Variable der WorkDataView-Tabelle gibt es ein ViewField. Ein Setzen schreibt den neuen Wert auch in die DB.
    vWinter = ViewField("Winter")
    vKessel = ViewField("Kessel")
    vKesselSoll = ViewField("KesselSoll")
    vBrauchwasser = ViewField("Brauchwasser")
    vInnen = ViewField("Innen")
    vAussen = ViewField("Aussen")
    vPumpe_oben_an = ViewField("Pumpe_oben_an")
    vPumpe_unten_an = ViewField("Pumpe_unten_an")
    vPumpe_Brauchwasser_an = ViewField("Pumpe_Brauchwasser_an")
    vBrenner_Stoerung = ViewField("Brenner_Stoerung")
    vWintertemp = ViewField("Wintertemp")
    vWintertempInnen = ViewField("WintertempInnen")
    vHeizen = ViewField("Heizen")
    vNachtabsenkung = ViewField("Nachtabsenkung")
    vBrauchwasserSoll = ViewField("BrauchwasserSoll")
    vBrauchwasserAus = ViewField("BrauchwasserAus")
    vBrauchwasserbereiten = ViewField("Brauchwasserbereiten")
    vLegionellenschutz = ViewField("Legionellenschutz")
    vBrenner_an = ViewField("Brenner_an")
    vHand_Dusche = ViewField("Hand_Dusche")

    @property
    def vKesselDaten_x(self):
        return self._KesselDaten_x
    
    @property
    def vKesselDaten_y(self):
        return self._KesselDaten_y
    
    @vKesselDaten_y.setter
    def vKesselDaten_y(self,value):
        self._writeKesselDaten_y(value)
