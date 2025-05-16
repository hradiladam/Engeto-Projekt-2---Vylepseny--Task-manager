import mysql.connector

# Vytvoreni a smazani testovaci database a tabulky ukoly
def create_test_db_and_table(): 
    # Pripojeni k mysql bez specificke db, protoze tu teprve vyrobime
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password = "ABtmdz247!"
    )
    cursor = conn.cursor()
    
    try:
        cursor.execute("CREATE DATABASE IF NOT EXISTS spravce_ukolu_test") # Vytvoreni testovaci db
        cursor.execute("USE spravce_ukolu_test") # PREPNE DO TESTOVACI DB
        cursor.execute("CREATE TABLE spravce_ukolu_test.ukoly LIKE spravce_ukolu.ukoly") # Vytvoreni testovaci tabulky
    except mysql.connector.Error as error:
        print(f"Vytvoření testovací databáze selhalo: {error}")
        raise

    cursor.close()
    conn.close()
    print("\n✅  Testovací databáze a tabulka byly vytvořeny.")


def drop_test_db():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="ABtmdz247!"
    )
    cursor = conn.cursor()
    cursor.execute("DROP DATABASE IF EXISTS spravce_ukolu_test")
    conn.commit()
    cursor.close()
    conn.close()


if __name__ == "__main__":
    create_test_db_and_table()







