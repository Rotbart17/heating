import sys
import unittest
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from control import Eingang, Grenzen, Modus, decide

NORMAL = Eingang(kessel=40, kessel_soll=50, brauchwasser=50, brauchwasser_soll=50,
                 aussen=5, innen=20, winter=True, heizen=False, nachtabsenkung=False,
                 brauchwasser_aus=False, brauchwasser_bereiten=False, hand_dusche=False,
                 legionellenschutz=False, brenner_stoerung=False)


def e(**kw) -> Eingang:
    return replace(NORMAL, **kw)


class DecideTest(unittest.TestCase):
    def test_nichts_zu_tun(self):
        self.assertEqual(decide(NORMAL).modus, Modus.AUS)

    def test_fehler_schaltet_alles_aus(self):
        for kw in ({"kessel": 95}, {"brauchwasser": 75}, {"aussen": 40}, {"innen": 35},
                   {"brenner_stoerung": True}):
            with self.subTest(kw):
                d = decide(e(heizen=True, **kw))
                self.assertEqual(d.modus, Modus.FEHLER)
                self.assertTrue(d.fehler)
                self.assertFalse(d.brenner or d.pumpe_oben or d.pumpe_unten or d.pumpe_brauchwasser)

    def test_heizen_nur_im_winter(self):
        self.assertEqual(decide(e(heizen=True, winter=False)).modus, Modus.AUS)
        d = decide(e(heizen=True))
        self.assertEqual(d.modus, Modus.HEIZEN)
        self.assertTrue(d.pumpe_oben and d.pumpe_unten and d.brenner)

    def test_heizen_hysterese(self):
        # Soll 50, Hysterese 2: an unter 48, aus ab 52
        self.assertFalse(decide(e(heizen=True, kessel=49)).brenner)
        self.assertTrue(decide(e(heizen=True, kessel=49, brenner_an=True)).brenner)
        self.assertFalse(decide(e(heizen=True, kessel=52, brenner_an=True)).brenner)
        # Pumpen laufen auch bei aus-Brenner weiter
        self.assertTrue(decide(e(heizen=True, kessel=52, brenner_an=True)).pumpe_oben)

    def test_nachtabsenkung(self):
        self.assertTrue(decide(e(heizen=True, kessel=45)).brenner)
        self.assertFalse(decide(e(heizen=True, kessel=45, nachtabsenkung=True)).brenner)

    def test_brauchwasser_hat_vorrang_vor_heizen(self):
        d = decide(e(heizen=True, brauchwasser_bereiten=True, brauchwasser=40))
        self.assertEqual(d.modus, Modus.BRAUCHWASSER)
        self.assertTrue(d.pumpe_brauchwasser)
        self.assertFalse(d.pumpe_oben or d.pumpe_unten)

    def test_brauchwasser_hysterese(self):
        # Start erst unter soll - 5, dann weiter bis soll
        self.assertEqual(decide(e(brauchwasser_bereiten=True, brauchwasser=47)).modus, Modus.AUS)
        d = decide(e(brauchwasser_bereiten=True, brauchwasser=47, modus=Modus.BRAUCHWASSER))
        self.assertEqual(d.modus, Modus.BRAUCHWASSER)
        self.assertEqual(decide(e(brauchwasser_bereiten=True, brauchwasser=50,
                                  modus=Modus.BRAUCHWASSER)).modus, Modus.AUS)

    def test_hand_dusche(self):
        self.assertEqual(decide(e(hand_dusche=True, brauchwasser=40)).modus, Modus.BRAUCHWASSER)

    def test_brauchwasser_aus(self):
        d = decide(e(hand_dusche=True, brauchwasser_bereiten=True, legionellenschutz=True,
                     brauchwasser=40, brauchwasser_aus=True))
        self.assertEqual(d.modus, Modus.AUS)

    def test_legionellenschutz_heizt_auf_65(self):
        d = decide(e(legionellenschutz=True, brauchwasser=58, brauchwasser_soll=50))
        self.assertEqual(d.modus, Modus.LEGIONELLENSCHUTZ)
        self.assertTrue(d.brenner)
        self.assertEqual(decide(e(legionellenschutz=True, brauchwasser=66,
                                  modus=Modus.LEGIONELLENSCHUTZ)).modus, Modus.AUS)

    def test_gefrierschutz_hat_vorrang(self):
        d = decide(e(aussen=1, kessel=8, innen=4, heizen=True, brauchwasser_bereiten=True,
                     brauchwasser=40))
        self.assertEqual(d.modus, Modus.GEFRIERSCHUTZ)
        self.assertTrue(d.pumpe_oben and d.pumpe_unten)
        self.assertFalse(d.brenner)  # Kessel noch nicht unter 5 Grad

    def test_gefrierschutz_brenner_unter_5_grad(self):
        self.assertTrue(decide(e(aussen=1, kessel=4, innen=4)).brenner)

    def test_gefrierschutz_hysterese(self):
        # aktiv bleibt er bis 2 Grad über den Startwerten
        self.assertEqual(decide(e(aussen=4, kessel=11, innen=4)).modus, Modus.AUS)
        self.assertEqual(decide(e(aussen=4, kessel=11, innen=4, modus=Modus.GEFRIERSCHUTZ)).modus,
                         Modus.GEFRIERSCHUTZ)


if __name__ == "__main__":
    unittest.main()
