import sqlite3

# Połączenie z bazą danych
# Jeśli plik `PID_simulation.db` nie istnieje w tym folderze, zmień ścieżkę!
conn = sqlite3.connect("PID_simulation.db")

# Utwórz kursor, który wykonuje zapytania
cursor = conn.cursor()

# Zapytanie SELECT
query = "SELECT * FROM simulation_data;"  # Zmień "nazwa_tabeli" na rzeczywistą nazwę tabeli
cursor.execute(query)

# Pobranie wszystkich wyników
results = cursor.fetchall()

# Wyświetlenie wyników
for row in results:
    print(row)

# Zamknięcie połączenia
conn.close()
