import sqlite3

# Połączenie z bazą danych
conn = sqlite3.connect("PID_simulation.db")

# Utwórz kursor, który wykonuje zapytania
cursor = conn.cursor()

# Zapytanie SELECT
query = "SELECT * FROM simulation_data;"
cursor.execute(query)

# Pobranie wszystkich wyników
results = cursor.fetchall()

# Wyświetlenie wyników
for row in results:
    print(row)

# Zamknięcie połączenia
conn.close()
