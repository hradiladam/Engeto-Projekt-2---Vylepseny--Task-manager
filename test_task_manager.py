import mysql.connector
from mysql.connector import Error
import pytest
from test_init import create_test_db_and_table, drop_test_db


# Fixture, ktera vytvori db a tabulku pred testy
@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    create_test_db_and_table()
    yield
    drop_test_db()

# Fixture, ktera otevre pripojeni k testovaci databazi
@pytest.fixture(scope="module")
def db_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="ABtmdz247!",
        database="spravce_ukolu_test"  # odělená testovací databáze
    )
    yield conn # Zpřístupní připojení testovací funkci, která jej použije
    conn.close()


# Test vlozeni platneho vstupu
def test_pridat_ukol_pozitivni(db_connection):
    cursor = db_connection.cursor()

    nazev = "Testovací úkol"
    popis = "Popis testovacího úkolu"
    sql = "INSERT INTO ukoly (nazev, popis) VALUES (%s, %s)"

    # Vlozeni ukolu
    cursor.execute(sql, (nazev, popis))
    db_connection.commit()

    # Ověření, že úkol byl přidán
    try:
        cursor.execute("SELECT * FROM ukoly WHERE nazev = %s AND popis = %s", (nazev, popis))
        result = cursor.fetchone()

        assert result is not None
        assert result[1] == nazev
        assert result[2] == popis

        # Smazání testovacího záznamu
        cursor.execute("DELETE FROM ukoly WHERE nazev = %s AND popis = %s", (nazev, popis))
        db_connection.commit()

    # Uzavreni spojeni
    finally:
        cursor.close()


# Test lozeni neplatneho vstupu
def test_pridat_ukol_negativni(db_connection):
    cursor = db_connection.cursor()

    # Vlozeni ukolu bez popisu, coz by melo selhat (popis je NOT NULL sloupec)
    try:
        nazev = "Testovací úkol"
        cursor.execute("INSERT INTO ukoly (nazev) VALUES (%s)", (nazev,))
        db_connection.commit()

        # Pokud se commit podari, test ma selhat
        assert False, "Vložení úkolu bez popisu mělo selhat, ale proběhlo úspěšně"
    
    except Error as sql_error:
        assert isinstance(sql_error, Error)
        assert sql_error.errno == 1364 # 1364 = Sloupec s NOT NULL požadavkem nedostal žádnou hodnotu (a nemá výchozí hodnotu)

    finally:
        cursor.close()


# Test aktualizovani ukolu, vlozeni platych hodnot
def test_aktualizovat_ukol_pozitivni(db_connection):
    cursor = db_connection.cursor()
    
    # Vložíme testovací úkol
    nazev = "Testovací úkol pro update"
    popis = "Popis testovacího úkolu"

    cursor.execute("INSERT INTO ukoly (nazev, popis) VALUES (%s, %s)", (nazev, popis))
    db_connection.commit()

    id_ukolu = cursor.lastrowid # Ulozi id posledniho ukolu po poslednim insertu, takze nemusime pozdeji pouzivat SELECT and .fetchone()

    try:
        # Aktualizujeme stav úkolu na 'hotovo'
        novy_stav = 'hotovo'
        cursor.execute("UPDATE ukoly SET stav = %s WHERE id = %s", (novy_stav, id_ukolu))
        db_connection.commit()

        # Ověříme, že se stav změnil
        cursor.execute("SELECT stav FROM ukoly WHERE id = %s", (id_ukolu,)) 
        zmeneny_stav = cursor.fetchone()[0] # Musim pouzit .fetchone(), jeliko6 lastrowid je mozne pouzit pouze ihned po "INSERT"
        assert novy_stav == zmeneny_stav
    
    finally:
        # Vyčistíme testovací data
        cursor.execute("DELETE FROM ukoly WHERE id = %s", (id_ukolu,))
        db_connection.commit()
        cursor.close()


# Test aktualizovani ukolu, vlozeni neplatnych hodnot
def test_aktualizovat_ukol(db_connection):
    cursor = db_connection.cursor()

    # Vložení testovacího úkolu (stav má default)
    nazev = "Testovací úkol pro NULL stav"
    popis = "Popis testu na NULL hodnotu"
    cursor.execute("INSERT INTO ukoly (nazev, popis) VALUES (%s, %s)", (nazev, popis))
    db_connection.commit()

    id_ukolu = cursor.lastrowid

    try:
        # Pokusíme se nastavit stav na NULL (což je neplatné, pokud sloupec je NOT NULL)
        novy_stav = None
        cursor.execute("UPDATE ukoly SET stav = %s WHERE id = %s", (novy_stav, id_ukolu))  # Explicitní NULL
        db_connection.commit()

        assert False, "Aktualizace stavu na NULL měla selhat (NOT NULL), ale proběhla úspěšně."
    
    except Error as sql_error:
        assert isinstance(sql_error, Error)
        assert sql_error.errno == 1048  # 1048 = Hodnota nezmi byt NULL

    finally:
        cursor.execute("DELETE FROM ukoly WHERE id = %s", (id_ukolu,))
        db_connection.commit()
        cursor.close()


# Test odstraneni ukolu
def test_odstranit_ukol_pozitivni(db_connection):
    cursor = db_connection.cursor()

    # Vlozeni ukolu
    nazev = "Testovací úkol k odstranění"
    popis = "Popis testovacího úkolu, který bude odstraněn"
    cursor.execute("INSERT INTO ukoly (nazev, popis) VALUES (%s, %s)", (nazev, popis))
    db_connection.commit()

    id_ukolu = cursor.lastrowid

    try:
        # 2. Smazani ukolu
        cursor.execute("DELETE FROM ukoly WHERE id = %s", (id_ukolu,))
        db_connection.commit()

        # Overeni smazani
        cursor.execute("SELECT * FROM ukoly WHERE id = %s", (id_ukolu,))
        result = cursor.fetchone()
        assert result is None, "Úkol nebyl odstraněn"

    finally:
        cursor.close()

# Test odstraneneni neexistujiciho ukolu
def test_odstranit_ukol_negativni(db_connection):
    cursor = db_connection.cursor()

    non_existent_id = 999999  # ID, ktere neexistuje

    try:
        # Zkontroluj, že ID neexistuje
        cursor.execute("SELECT id FROM ukoly WHERE id = %s", (non_existent_id,))
        assert cursor.fetchone() is None

        # Pokus o smazani ukolu
        cursor.execute("DELETE FROM ukoly WHERE id = %s", (non_existent_id,))
        db_connection.commit()

        # Pokus o smazání by neměl odstranit žádné řádky
        rows_affected = cursor.rowcount
        assert rows_affected == 0, "Byl odstraněn záznam, který neměl existovat"

    finally:
        cursor.close()
