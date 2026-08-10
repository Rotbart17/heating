#!/usr/bin/env python3
"""Übergeordnete Beschreibung der Regelkreise
Alle Aktionen dürfen nur statt finden, wenn 
alle Werte innerhalb der Toleranzen sind.
- Kesseltemperatur 2 < t < KesselMax
- Brauchwasser Temperatur 2 < t < BrauchwasserError
- Sensoren Werte müssen sich in erlaubten Bereichen befinden
- 	Brennerstatus Brenner_Stoerung (kann nur indirekt ermittelt werden)
- 	Aussentemperatur AussenMinTemp < t < AussenMaxTemp
- 	Innentemperatur 2 < t < 30
Wenn nicht muss ein Fehler ausgegeben werden und das Programm 
darf keine Aktion zulassen bis die Werte wieder in dem Normbereich 
sind.

Die verschiedenen Modi (Brauchwasser, Heizung, Nachtabs., Legionellen, Gefrierschutz) müssen in der Anzeige sichtbar sein
Solange die Werte OK sind, minimal minütlich prüfen:
- Prüfen ob Gefrierschutz (2<t<8) notwendig ist -> aktivieren
- Prüfen ob Legionellenschutz notwendig ist -> aktivieren
- Prüfen ob Brauchwasser bereitet werden soll 
		Brauchwasser nicht generell aus?
   BrauchwasserZeitraum AND Brauchwassertemperatur zu niedrig
						-> Brauchwasserbereitung aktivieren
- Prüfen ob der Heizbetrieb notwendig ist 
						-> Heizwasserbereitung aktivieren
						Prüfen ob Brauchwasser erwärmt werden muss -> Bruchwasserbereitung 
						aktivieren und zurückkehren
zum Schleifenanfang"""


