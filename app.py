from tkinter import *
import sqlite3
from tkinter import simpledialog

# Yhdistetään tietokantaan
conn = sqlite3.connect("tehtavalista.db")
cursor = conn.cursor()

# Luodaan tehtävien ja käyttäjien taulut, jos niitä ei vielä ole
cursor.execute('''CREATE TABLE IF NOT EXISTS tehtavat (id INTEGER PRIMARY KEY, kayttaja_id INTEGER, tehtava_teksti TEXT)''')
conn.commit()
cursor.execute('''CREATE TABLE IF NOT EXISTS kayttajat (id INTEGER PRIMARY KEY, kayttajanimi TEXT, salasana TEXT, on_admin INTEGER)''')
conn.commit()
kayttajan_tehtavat = []

# Avataan pääsovellus
def avaa_paasovellus(kayttaja_id, on_admin):
    def painallus():
        global kayttajan_tehtavat
        tehtava_teksti = e.get()
        painallus_teksti = Label(tehtavakehys, text=tehtava_teksti)
        painallus_teksti.grid(row=len(kayttajan_tehtavat), column=0, columnspan=2, sticky="w", padx=10, pady=5)

        # Tallennetaan käyttäjän syöte ja käyttäjän ID tietokantaan
        cursor.execute("INSERT INTO tehtavat (kayttaja_id, tehtava_teksti) VALUES (?, ?)", (kayttaja_id, tehtava_teksti))
        conn.commit()

        # Tyhjennetään syötekenttä tehtävän lisäämisen jälkeen
        e.delete(0, END)

        # Päivitetään tehtävälista
        hae_tehtavat(kayttaja_id, on_admin)

    def hae_tehtavat(kayttaja_id, on_admin):
        # Haetaan tehtävät tietokannasta
        if on_admin:
            cursor.execute("SELECT id, tehtava_teksti, kayttaja_id FROM tehtavat")
            kayttaja_id = "admin"  # Asetetaan käyttäjä_id "adminiksi" ylläpitäjille
        else:
            cursor.execute("SELECT id, tehtava_teksti, kayttaja_id FROM tehtavat WHERE kayttaja_id=?", (kayttaja_id,))

        kayttajan_tehtavat = cursor.fetchall()

        # Tyhjennetään tehtäväkehys ennen uudelleentäyttöä
        for widget in tehtavakehys.winfo_children():
            widget.destroy()

        # Näytetään haetut tehtävät ja lisätään niihin Muokkaa ja Poista -napit luojalle tai ylläpitäjälle
        for i, (tehtava_id, tehtava_teksti, tehtava_luojan_id) in enumerate(kayttajan_tehtavat):
            tehtava_label = Label(tehtavakehys, text=tehtava_teksti)
            tehtava_label.grid(row=i, column=0, columnspan=2, sticky="w", padx=10, pady=5)

            if kayttaja_id == tehtava_luojan_id or kayttaja_id == "admin":
                muokkaa_nappi = Button(tehtavakehys, text="Muokkaa", command=lambda tehtava_id=tehtava_id, tehtava_teksti=tehtava_teksti: muokkaa_tehtava(kayttaja_id, tehtava_id, tehtava_teksti))
                muokkaa_nappi.grid(row=i, column=2, padx=5)

                poista_nappi = Button(tehtavakehys, text="Poista", command=lambda tehtava_id=tehtava_id: poista_tehtava(kayttaja_id, tehtava_id))
                poista_nappi.grid(row=i, column=3, padx=5)

    def muokkaa_tehtava(kayttaja_id, tehtava_id, vanha_teksti):
        # Tarkistetaan, onko käyttäjä tehtävän luoja tai ylläpitäjä
        cursor.execute("SELECT kayttaja_id FROM tehtavat WHERE id=?", (tehtava_id,))
        tehtava_luoja_id = cursor.fetchone()[0]

        if kayttaja_id == tehtava_luoja_id or kayttaja_id == "admin":
            uusi_teksti = simpledialog.askstring("Muokkaa tehtävää", "Muokkaa tehtävää:", initialvalue=vanha_teksti)
            if uusi_teksti:
                cursor.execute("UPDATE tehtavat SET tehtava_teksti=? WHERE id=?", (uusi_teksti, tehtava_id))
                conn.commit()
                hae_tehtavat(kayttaja_id, on_admin)
        else:
            # Näytetään virheviesti käyttäjille, jotka eivät ole tehtävän luoja tai ylläpitäjiä
            virhe_label.config(text="Sinulla ei ole oikeuksia muokata tätä tehtävää.")

    def poista_tehtava(kayttaja_id, tehtava_id):
        # Tarkistetaan, onko käyttäjä tehtävän luoja tai ylläpitäjä
        cursor.execute("SELECT kayttaja_id FROM tehtavat WHERE id=?", (tehtava_id,))
        tehtava_luoja_id = cursor.fetchone()[0]

        if kayttaja_id == tehtava_luoja_id or kayttaja_id == "admin":
            cursor.execute("DELETE FROM tehtavat WHERE id=?", (tehtava_id,))
            conn.commit()
            hae_tehtavat(kayttaja_id, on_admin)
        else:
            # Näytetään virheviesti käyttäjille, jotka eivät ole tehtävän luoja tai ylläpitäjiä
            virhe_label.config(text="Sinulla ei ole oikeuksia poistaa tätä tehtävää.")

    root = Tk()
    root.title("Tehtävälista Sovellus")
    root.geometry("500x500")  # Asetetaan ikkunan koko 500x500 pikseliin

    e = Entry(root)
    e.grid(row=0, column=0, padx=10, pady=10)

    lisaa_nappi = Button(root, text="Lisää Tehtävä", width=10, command=painallus)
    lisaa_nappi.grid(row=0, column=1, padx=5)

    tehtavakehys = Frame(root)
    tehtavakehys.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

    hae_tehtavat(kayttaja_id, on_admin)

    root.mainloop()

# Tarkistetaan käyttäjätunnukset
def tarkista_tunnukset():
    kayttajanimi = kayttajanimi_syote.get()
    salasana = salasana_syote.get()

    cursor.execute("SELECT id, on_admin FROM kayttajat WHERE kayttajanimi=? AND salasana=?", (kayttajanimi, salasana))
    kayttaja_tiedot = cursor.fetchone()

    if kayttaja_tiedot:
        kayttaja_id, on_admin = kayttaja_tiedot
        on_admin_bool = bool(on_admin)  # Muutetaan kokonaisluku boolean-arvoksi

        # Jos käyttäjä on tunnistettu, avataan pääsovellus hänen käyttäjä-ID:llään
        kirjautumisikkuna.destroy()
        avaa_paasovellus(kayttaja_id, on_admin_bool)  # Siirretään käyttäjä-ID ja on_admin_bool pääsovellukselle
    else:
        # Jos tunnistaminen epäonnistuu, näytetään virheviesti
        virhe_label.config(text="Virheellinen käyttäjätunnus tai salasana")

# Avataan rekisteröitymissivu
def avaa_rekisterointi_sivu():
    def rekisteroi_kayttaja():
        uusi_kayttajanimi = uusi_kayttajanimi_syote.get()
        uusi_salasana = uusi_salasana_syote.get()

        # Tarkistetaan, onko käyttäjänimi jo käytössä
        cursor.execute("SELECT * FROM kayttajat WHERE kayttajanimi=?", (uusi_kayttajanimi,))
        olemassaoleva_kayttaja = cursor.fetchone()

        if olemassaoleva_kayttaja:
            virhe_label_rekisterointi.config(text="Käyttäjänimi on jo käytössä.")
        else:
            # Määritetään, pitäisikö uudesta käyttäjästä tulla ylläpitäjä
            if not cursor.execute("SELECT * FROM kayttajat").fetchall():
                on_admin = 1  # Asetetaan on_admin 1:ksi ensimmäiselle käyttäjälle
            else:
                on_admin = 0  # Asetetaan on_admin 0:ksi muille käyttäjille

            # Jos käyttäjänimi ei ole käytössä, lisätään se tietokantaan
            cursor.execute("INSERT INTO kayttajat (kayttajanimi, salasana, on_admin) VALUES (?, ?, ?)", (uusi_kayttajanimi, uusi_salasana, on_admin))
            conn.commit()

            # Kirjaudutaan juuri rekisteröitynyt käyttäjä sisään
            cursor.execute("SELECT id FROM kayttajat WHERE kayttajanimi=? AND salasana=?", (uusi_kayttajanimi, uusi_salasana))
            kayttaja_id = cursor.fetchone()

            if kayttaja_id:
                rekisterointi_ikkuna.destroy()
                avaa_paasovellus(kayttaja_id[0], bool(on_admin))  # Siirretään käyttäjä-ID ja on_admin pääsovellukselle

    rekisterointi_ikkuna = Tk()
    rekisterointi_ikkuna.title("Rekisteröidy")
    rekisterointi_ikkuna.geometry("500x500")  # Asetetaan ikkunan koko 500x500 pikseliin

    uusi_kayttajanimi_label = Label(rekisterointi_ikkuna, text="Uusi käyttäjänimi:")
    uusi_kayttajanimi_label.grid(row=0, column=0, padx=10, pady=10)

    uusi_kayttajanimi_syote = Entry(rekisterointi_ikkuna)
    uusi_kayttajanimi_syote.grid(row=0, column=1, padx=10, pady=10)

    uusi_salasana_label = Label(rekisterointi_ikkuna, text="Uusi salasana:")
    uusi_salasana_label.grid(row=1, column=0, padx=10, pady=10)

    uusi_salasana_syote = Entry(rekisterointi_ikkuna, show="*")  # Salasanasyöte näyttää '*' jokaista merkkiä kohti
    uusi_salasana_syote.grid(row=1, column=1, padx=10, pady=10)

    rekisteroi_nappi = Button(rekisterointi_ikkuna, text="Rekisteröidy", command=rekisteroi_kayttaja)
    rekisteroi_nappi.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

    virhe_label_rekisterointi = Label(rekisterointi_ikkuna, text="", fg="red")
    virhe_label_rekisterointi.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

    kirjautumisikkuna.destroy()  # Suljetaan kirjautumisikkuna rekisteröinnin jälkeen

    rekisterointi_ikkuna.mainloop()

# Luodaan kirjautumisikkuna
kirjautumisikkuna = Tk()
kirjautumisikkuna.title("Kirjaudu")
kirjautumisikkuna.geometry("500x500")  # Asetetaan ikkunan koko 500x500 pikseliin

kayttajanimi_label = Label(kirjautumisikkuna, text="Käyttäjänimi:")
kayttajanimi_label.grid(row=0, column=0, padx=10, pady=10)

kayttajanimi_syote = Entry(kirjautumisikkuna)
kayttajanimi_syote.grid(row=0, column=1, padx=10, pady=10)

salasana_label = Label(kirjautumisikkuna, text="Salasana:")
salasana_label.grid(row=1, column=0, padx=10, pady=10)

salasana_syote = Entry(kirjautumisikkuna, show="*")  # Salasanasyöte näyttää '*' jokaista merkkiä kohti
salasana_syote.grid(row=1, column=1, padx=10, pady=10)

kirjaudu_nappi = Button(kirjautumisikkuna, text="Kirjaudu", command=tarkista_tunnukset)
kirjaudu_nappi.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

rekisteroi_nappi = Button(kirjautumisikkuna, text="Rekisteröidy", command=avaa_rekisterointi_sivu)
rekisteroi_nappi.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

virhe_label = Label(kirjautumisikkuna, text="", fg="red")
virhe_label.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

kirjautumisikkuna.mainloop()