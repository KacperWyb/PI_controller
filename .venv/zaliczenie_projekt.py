# zaprojektowac dowolna implementacje regulatora PID
# np dla regulowania temperatury wewnatrz piekarnika
# dane z bazy sqlite
# silnik obliczeniowy
# klasyczny regulator i rozmyty regulator
# interfejs interaktywny
# najlepiej pokazac zmiany dla klasycznego / rozmytego na raz obok zeby mogl porownac / zobaczyc roznice

import sqlite3
import tkinter as tk
from tkinter import ttk  # bokeh najlepiej
import time
import random

# Tworzymy bazę danych
def init_db():
    conn = sqlite3.connect("temperature_data.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS temperature_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            setpoint REAL,
            measured_temp REAL,
            control_signal REAL
        )
    """)
    conn.commit()
    conn.close()

# Zapisz dane do bazy
def save_to_db(setpoint, measured_temp, control_signal):
    conn = sqlite3.connect("temperature_data.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO temperature_history (setpoint, measured_temp, control_signal) VALUES (?, ?, ?)",
                   (setpoint, measured_temp, control_signal))
    conn.commit()
    conn.close()

# Klasa dla regulatora PID
class PID:
    def __init__(self, kp, ki, kd, setpoint=0):
        self.kp = kp  # Wzmocnienie proporcjonalne
        self.ki = ki  # Wzmocnienie całkujące
        self.kd = kd  # Wzmocnienie różniczkujące
        self.setpoint = setpoint  # Wartość zadana
        self.integral = 0  # Całka
        self.previous_error = 0  # Poprzedni błąd

    def compute(self, measured_value, dt):
        # Obliczenie uchybu
        error = self.setpoint - measured_value
        self.integral += error * dt
        derivative = (error - self.previous_error) / dt

        # Obliczenie sygnału sterującego
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        self.previous_error = error

        return output

# Klasa symulatora temperatury
class TemperatureSimulator:
    def __init__(self):
        self.temperature = 20  # Początkowa temperatura

    def update(self, control_signal):
        # Symulacja ogrzewania lub chłodzenia w zależności od sygnału sterującego
        self.temperature += control_signal * 0.1
        self.temperature += random.uniform(-0.1, 0.1)  # Szum pomiarowy
        return self.temperature

# Funkcja uruchamiająca symulację
def run_simulation():
    setpoint = float(entry_setpoint.get())
    pid.setpoint = setpoint
    fuzzy.setpoint = setpoint
    controller_type = selected_controller.get()
    simulator = TemperatureSimulator()

    # Zainicjalizuj control_signal przed pętlą
    control_signal = 0

    # Pętla symulacji
    for _ in range(100):
        measured_temp = simulator.update(control_signal)

        # Wybierz regulator
        if controller_type == "PID":
            control_signal = pid.compute(measured_temp, dt=1)
        else:
            control_signal = fuzzy.compute(measured_temp)

        # Upewnij się, że sygnał sterujący jest większy od 0
        control_signal = max(control_signal, 0)

        # Zapisz dane do bazy i GUI
        save_to_db(setpoint, measured_temp, control_signal)
        text_output.insert(tk.END, f"Temp: {measured_temp:.2f}, Sygnał sterujący: {control_signal:.2f}\n")
        text_output.see(tk.END)
        window.update()
        time.sleep(0.1)


# Inicjalizacja bazy danych
init_db()

# Inicjalizacja okna GUI
window = tk.Tk()
window.title("Symulacja regulatora PID")

# Wybór wartości zadanej
tk.Label(window, text="Wartość zadana (°C):").pack()
entry_setpoint = tk.Entry(window)
entry_setpoint.pack()

# Wybór typu regulatora
selected_controller = tk.StringVar(value="PID")
tk.Label(window, text="Wybierz regulator:").pack()
ttk.Radiobutton(window, text="PID", variable=selected_controller, value="PID").pack()
ttk.Radiobutton(window, text="Rozmyty", variable=selected_controller, value="Rozmyty").pack()

# Przycisk uruchamiający symulację
btn_run = tk.Button(window, text="Uruchom symulację", command=run_simulation)
btn_run.pack()

# Wyświetlanie wyników
text_output = tk.Text(window, height=10, width=50)
text_output.pack()

# Inicjalizacja regulatorów PID i rozmytego (przykładowa klasa dla regulatora rozmytego)
class FuzzyController:
    def __init__(self):
        self.setpoint = 0

    def compute(self, measured_value):
        # Implementacja logiki rozmytej (wymaga zaimplementowania)
        return 0  # Zwracany sygnał sterujący

# Inicjalizacja regulatorów PID i rozmytego
pid = PID(kp=1.0, ki=0.1, kd=0.05)
fuzzy = FuzzyController()

# Rozpoczęcie pętli głównej aplikacji
window.mainloop()
