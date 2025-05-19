import mysql.connector
from mysql.connector import Error
from datetime import datetime

def connect_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="ABtmdz247!",
            database="spravce_ukolu"
        )
        return conn
    
    except Error as error:
        print(f"\n❌  Chyba při připojení k databázi: {error}")


def create_table():
    conn = connect_db()
    if conn:
        try:
            # vytvoreni tabulky, pokud neexistuje
            cursor = conn.cursor()
            sql = """
                CREATE TABLE IF NOT EXISTS ukoly (
                    id INT AUTO_INCREMENT PRIMARY KEY, 
                    nazev VARCHAR(50) NOT NULL,
                    popis TEXT NOT NULL,
                    stav ENUM('nezahájeno', 'hotovo', 'probíhá') NOT NULL DEFAULT 'nezahájeno',
                    datum_vytvoreni DATETIME DEFAULT CURRENT_TIMESTAMP 
                );
            """
            cursor.execute(sql)
            conn.commit()
        
        except Error as error:
            print(f"\n❌ Chyba při vytváření tabulky: {error}")
        
        finally:
            cursor.close()
            conn.close()


# Funkce pro pridani noveho ukolu
def pridat_ukol():
    conn = connect_db()
    if not conn:
        return
    
    while True:
        nazev = input("\nZadejte název úkolu: ").strip()
        if not nazev:
            print("\n⚠️  Název úkolu nesmí být prázdný ani obsahovat pouze mezery. Zkuste znovu.\n")
            continue
        
        popis = input("Zadejte popis úkolu: ").strip()
        if not popis:
            print("\n⚠️  Popis úkolu nesmí být prázdný. Zkuste to znovu.")
            continue
            
        try:
            cursor = conn.cursor()
            sql = "INSERT INTO ukoly (nazev, popis, stav, datum_vytvoreni) VALUES (%s, %s, %s, %s)"
            hodnoty = (nazev, popis, 'nezahájeno', datetime.now())
            cursor.execute(sql, hodnoty)
            conn.commit()
            print(f"\n✔️  Úkol byl přidán s ID: {cursor.lastrowid}")
            break
        
        except mysql.connector.Error as error:
            print(f"\n❌  Chyba při přidávání úkolu: {error}")
            break
    
        finally:
            cursor.close()
            conn.close()

# Zobrazeni ukolu
def zobrazit_ukoly():
    conn = connect_db()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        sql = "SELECT id, nazev, popis, stav FROM ukoly WHERE stav IN ('nezahájeno', 'probíhá')"
        cursor.execute(sql)
        ukoly = cursor.fetchall()

        if not ukoly:
            print(f"\n⚠️  Žádné úkoly k zobrazení.")
        else:
            print(f"\n📋  Seznam úkolů:")
            for index, ukol in enumerate(ukoly, 1):
                print(f"{index}. ID: {ukol[0]} | Název: {ukol[1]} | Popis: {ukol[2]} | Stav: {ukol[3]}") 

    except mysql.connector.Error as error:
        print(f"❌  Chyba při zobrazování úkolů: {error}")

    finally:
        cursor.close()
        conn.close()
    

# Pomocna funkce pro vybrani id 
def vybrat_ukol_id(cursor):
    cursor.execute("SELECT id, nazev FROM ukoly")
    ukoly = cursor.fetchall()
    if not ukoly:
        print("\n⚠️  Seznam úkolů je prázdný.")
        return None

    print("\n📋  Seznam úkolů:")
    for index, ukol in enumerate(ukoly, 1):
        print(f"{index}. ID: {ukol[0]} | Název: {ukol[1]}")

    while True:
        volba = input("\nZadejte ID úkolu: ").strip()
        if not volba.isdigit():
            print("\n⚠️  Zadejte číselné ID.")
            continue
        id_ukolu = int(volba)
        cursor.execute("SELECT id FROM ukoly WHERE id = %s", (id_ukolu,))
        if cursor.fetchone():
            return id_ukolu
        else:
            print("\n⚠️  Úkol s tímto ID neexistuje.")


# Funkce, ktera zmeni "probiha", "probihá" a "probíha" na "probíhá"
def normalizuj_stav(stav):
    stav = stav.strip().lower()
    if stav in ["probiha", "probihá", "probíha"]:
        return "probíhá"
    return stav


# Aktualizauje úkol
def aktualizovat_ukol():
    conn = connect_db()
    if not conn:
        return
   
    try:
        cursor = conn.cursor()

        id_ukolu = vybrat_ukol_id(cursor)
        if id_ukolu is None:
            return

        while True:
            novy_stav = input("\nZadejte nový stav ('hotovo' nebo 'probíhá'): ")
            novy_stav = normalizuj_stav(novy_stav)
            if novy_stav in ['hotovo', 'probíhá']:
                break
            else:
                print("\n⚠️  Neplatný stav. Zadejte pouze 'probíhá' nebo 'hotovo'.")
            
        cursor.execute('UPDATE ukoly SET stav = %s WHERE id = %s', (novy_stav, id_ukolu))
        conn.commit()

        print("\n✅  Stav úkolu byl aktualizován.")

    except mysql.connector.Error as error:
        print(f"\n❌  Chyba při aktualizaci úkolu: {error}")
        
    finally:
        cursor.close()
        conn.close()


# Odstranit ukol
def odstranit_ukol():
    conn = connect_db()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        id_ukolu = vybrat_ukol_id(cursor)
        if id_ukolu is None:
            return

        potvrzeni = input(f"\nOpravdu chcete odstranit úkol s ID {id_ukolu}? (a/n): ").strip().lower()
        if potvrzeni == "a":
            cursor.execute("DELETE FROM ukoly WHERE id = %s", (id_ukolu,))
            conn.commit()
            print("\n🗑️  Úkol byl úspěšně odstraněn.")
        else:
            print("ℹ️  Odstranění zrušeno.")
    
    except mysql.connector.Error as error:
        print(f"❌  Chyba při odstraňování úkolu: {error}")

    finally:
        cursor.close()
        conn.close()


# Ukonci profram
def ukoncit_program():
    print("\n👋  Program ukončen.") 


# Hlavni menu aplikace
def hlavni_menu():
    while True:
        print("""
            =================== Správce úkolů - Hlavní menu ===================
            1. Přidat nový úkol
            2. Zobrazit všechny úkoly
            3. Aktualizovat úkol
            4. Odstranit úkol
            5. Konec programu
            ===================================================================
          """)
    
        volba = input("\nVyberte možnost (1-5): ")
        
        if volba == "1":
            pridat_ukol()
        elif volba == "2":
            zobrazit_ukoly()  
        elif volba == "3":
            aktualizovat_ukol()
        elif volba == "4":
            odstranit_ukol()
        elif volba == "5":
            ukoncit_program()
            break 
        else:
            print("\n⚠️  Neplatná volba. Zkuste znovu.")


# Vytvori tabulku ukoly v db a spousti hlavni menu
if __name__ == "__main__":
    create_table()
    hlavni_menu()
    

