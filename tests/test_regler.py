import math
import sys
import multiprocessing
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ausgabe import Ausgabe, Brennerueberwachung, Brennerzyklus
from control import Modus, ist_winter, kennlinie_soll
from regler import Regler


class FakeDatav:
    '''Ersatz für maindata ohne Datenbank'''
    def __init__(self):
        self.vWinter = True
        self.vWintertemp = 17.0
        self.vWintertempInnen = 20.0
        self.vKessel = self.vKesselSoll = self.vBrauchwasser = self.vInnen = self.vAussen = 0
        self.vPumpe_oben_an = self.vPumpe_unten_an = self.vPumpe_Brauchwasser_an = False
        self.vBrenner_an = self.vBrenner_Stoerung = False
        self.vHeizen = True
        self.vNachtabsenkung = self.vBrauchwasserAus = self.vBrauchwasserbereiten = False
        self.vLegionellenschutz = self.vHand_Dusche = False
        self.vBrauchwasserSoll = 50.0
        self.vKesselDaten_x = [-30.0, 0.0, 30.0]
        self.vKesselDaten_y = [92.0, 56.0, 20.0]

    def _viewloader(self, initial):
        pass

    def _kesseldataload(self):
        pass


class Uhr:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


class BrennerzyklusTest(unittest.TestCase):
    def test_mindestlaufzeit_und_pause(self):
        z = Brennerzyklus(jetzt=0)
        self.assertFalse(z.freigabe(True, 100))   # Pause nach Start
        self.assertTrue(z.freigabe(True, 300))
        self.assertTrue(z.freigabe(False, 400))   # läuft noch keine 5 Minuten
        self.assertFalse(z.freigabe(False, 600))
        self.assertFalse(z.freigabe(True, 800))   # Totzeit
        self.assertTrue(z.freigabe(True, 900))

    def test_notaus_ist_sofort(self):
        z = Brennerzyklus(jetzt=0)
        z.freigabe(True, 300)
        self.assertFalse(z.freigabe(True, 301, notaus=True))
        self.assertFalse(z.freigabe(True, 302))   # Totzeit gilt auch nach Notaus


class BrennerueberwachungTest(unittest.TestCase):
    def test_anstieg_ist_ok(self):
        u = Brennerueberwachung()
        self.assertFalse(u.stoerung(True, 30, 0))
        self.assertFalse(u.stoerung(True, 35, 100))
        self.assertFalse(u.stoerung(True, 40, 180))
        self.assertFalse(u.stoerung(True, 30, 400))    # nur einmal pro Lauf geprüft

    def test_kein_anstieg_ist_stoerung(self):
        u = Brennerueberwachung()
        u.stoerung(True, 30, 0)
        self.assertFalse(u.stoerung(True, 30, 179))
        self.assertTrue(u.stoerung(True, 30.2, 180))

    def test_neuer_lauf_wird_neu_geprueft(self):
        u = Brennerueberwachung()
        u.stoerung(True, 30, 0)
        u.stoerung(True, 40, 180)
        u.stoerung(False, 40, 200)
        u.stoerung(True, 40, 500)
        self.assertTrue(u.stoerung(True, 40, 700))


class ControlHelfer(unittest.TestCase):
    def test_kennlinie(self):
        x, y = [-10.0, 0.0, 10.0], [68.0, 56.0, 44.0]
        self.assertEqual(kennlinie_soll(x, y, 0), 56)
        self.assertEqual(kennlinie_soll(x, y, 5), 50)
        self.assertEqual(kennlinie_soll(x, y, -20), 68)
        self.assertEqual(kennlinie_soll(x, y, 20), 44)
        with self.assertRaises(ValueError):
            kennlinie_soll([], [], 0)

    def test_winter(self):
        self.assertTrue(ist_winter(5, 18, 17, 20, False))
        self.assertFalse(ist_winter(18, 18, 17, 20, False))
        self.assertTrue(ist_winter(17.5, 18, 17, 20, True))   # Hysterese
        self.assertFalse(ist_winter(5, 22, 17, 20, False))


class ReglerTest(unittest.TestCase):
    def setUp(self):
        self.d = FakeDatav()
        self.uhr = Uhr()
        self.werte = {"Kesselsensor": 30.0, "Brauchwassersensor": 50.0,
                      "Aussensensor": 0.0, "Innensensor": 18.0}
        self.lauf = []
        self.ausgabe = Ausgabe()
        self.regler = Regler(multiprocessing.Event(), self.d, self.ausgabe,  # type: ignore[arg-type]
                             sensorquelle=lambda n: self.werte[n],
                             protokoll=lambda von, bis: self.lauf.append((von, bis)),
                             uhr=self.uhr)

    def schritt(self, t):
        self.uhr.t = t
        self.regler.schritt()

    def test_start_pause_dann_heizen(self):
        self.schritt(10)
        self.assertEqual(self.regler.modus, Modus.HEIZEN)
        self.assertTrue(self.ausgabe.pumpe_oben)
        self.assertFalse(self.ausgabe.brenner)      # noch Pause nach dem Start
        self.schritt(300)
        self.assertTrue(self.ausgabe.brenner)
        self.assertTrue(self.d.vBrenner_an)
        self.assertEqual(self.d.vKesselSoll, 56)

    def test_pumpen_laufen_mit_bis_mindestlaufzeit_vorbei(self):
        self.schritt(300)
        self.werte["Kesselsensor"] = 60.0           # Brenner will aus
        self.schritt(310)
        self.assertTrue(self.ausgabe.brenner)       # Mindestlaufzeit
        self.d.vHeizen = False                      # Entscheidung wäre AUS ohne Pumpen
        self.schritt(320)
        self.assertTrue(self.ausgabe.brenner)
        self.assertTrue(self.ausgabe.pumpe_oben and self.ausgabe.pumpe_unten)
        self.schritt(700)
        self.assertFalse(self.ausgabe.brenner)
        self.assertFalse(self.ausgabe.pumpe_oben)
        self.assertEqual(len(self.lauf), 1)

    def test_sensorausfall_schaltet_alles_aus(self):
        self.schritt(300)
        self.assertTrue(self.ausgabe.brenner)
        self.werte["Kesselsensor"] = math.nan
        self.schritt(305)
        self.assertEqual(self.regler.modus, Modus.FEHLER)
        self.assertFalse(self.ausgabe.brenner or self.ausgabe.pumpe_oben or self.ausgabe.pumpe_unten)
        self.assertFalse(self.d.vBrenner_an)
        self.assertEqual(len(self.lauf), 1)

    def test_brennerstoerung_nach_drei_minuten(self):
        self.schritt(300)                           # Brenner an, Kessel bleibt bei 30 Grad
        self.assertTrue(self.ausgabe.brenner)
        self.schritt(400)
        self.assertTrue(self.ausgabe.brenner)
        self.schritt(590)
        self.assertEqual(self.regler.modus, Modus.FEHLER)
        self.assertTrue(self.d.vBrenner_Stoerung)
        self.assertFalse(self.ausgabe.brenner or self.ausgabe.pumpe_oben)
        self.schritt(900)                           # bleibt aus, bis zum Neustart
        self.assertEqual(self.regler.modus, Modus.FEHLER)

    def test_neustart_quittiert_stoerung(self):
        self.d.vBrenner_Stoerung = True
        self.regler.stop_event.set()
        self.regler.run()
        self.assertFalse(self.d.vBrenner_Stoerung)

    def test_sicherer_zustand_beim_stoppen(self):
        self.schritt(300)
        self.regler.stop_event.set()
        self.regler.run()
        self.assertFalse(self.ausgabe.brenner or self.ausgabe.pumpe_oben)
        self.assertFalse(self.d.vBrenner_an)


if __name__ == "__main__":
    unittest.main()
