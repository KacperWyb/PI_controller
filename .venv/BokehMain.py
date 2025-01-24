from math import sqrt
from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Slider
from bokeh.plotting import figure
import sqlite3

# Tworzenie lub łączenie z bazą danych SQLite
conn = sqlite3.connect("PID_simulation.db")
cursor = conn.cursor()

# Tworzenie tabeli, jeśli nie istnieje
cursor.execute("""
CREATE TABLE IF NOT EXISTS simulation_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    czas REAL,
    wysokosc_wody REAL,
    wartosc_sterujaca REAL
)
""")
conn.commit()

# PARAMETRY REGULATORA
t_i = 20  # stała całkowania
t_d = 5  # czas wyprzedzenia
kp = 0.008  # wzmocnienie regulatora

# PARAMETRY ZBIORNIKA
A = 2  # przekrój poprzeczny zbiornika
h_min = 0  # minimalna wysokość wody w zbiorniku
h_max = 10  # maksymalna wysokość wody w zbiorniku
B = 0.035  # współczynnik wypływu m/s
q_min = 0  # minimalna przepustowość dopływu w litrach / s
q_max = 50  # maksymalna przepustowość dopływu w litrach / s

# PARAMETRY SYMULACJI
t_p = 0.2  # okres próbkowania
czas_symulacji = 15  # w minutach
t_Sim = czas_symulacji * 60  # czas symulacji w sekundach
N = int(t_Sim / t_p)  # liczba próbek (2 próbki na sekundę)
h_zadane = 3

# Dane początkowe
T = [0]
H = [0]  # wysokość wody w zbiorniku
e = [0.0]  # Lista z wartościami uchybu
u = [0]  # wartość sterująca
u_min = 0
u_max = 10

# Funkcja do zapisywania danych do bazy SQLite
def save_to_db(T, H, u):
    cursor.execute("DELETE FROM simulation_data")  # Wyczyść tabelę przed zapisem
    for t, h, ctrl in zip(T, H, u):
        cursor.execute("INSERT INTO simulation_data (czas, wysokosc_wody, wartosc_sterujaca) VALUES (?, ?, ?)", (t, h, ctrl))
    conn.commit()

# Funkcja do odczytu danych z bazy SQLite
def load_from_db():
    cursor.execute("SELECT czas, wysokosc_wody FROM simulation_data")
    rows = cursor.fetchall()
    return [row[0] for row in rows], [row[1] for row in rows]

# Symulacja wstępna
for i in range(0, N):
    T.append(i * t_p / 60)
    e.append(h_zadane - H[i])
    u_temp = kp * (e[i] + t_p / t_i * sum(e) + (t_d / t_p) * (e[-1] - e[-2]))
    u.append(min(u_max, max(u_min, u_temp)))
    q_d = (((u[-1] - u_min) / (u_max - u_min)) * (q_max - q_min) + q_min)
    H.append(min(h_max, max(h_min, t_p * (q_d - B * sqrt(H[-1])) / A + H[-1])))

# Zapis danych do bazy
save_to_db(T, H, u)

# Ustawienia wykresu
p = figure(title="Symulacja napełniania zbiornika",
           x_axis_label="czas [min]", y_axis_label="wysokość wody w zbiorniku [m]")

# Dane do wykresu
T_plot, H_plot = load_from_db()
source = ColumnDataSource(data=dict(x=T_plot, y=H_plot))
p.line('x', 'y', source=source)

# Slider do aktualizacji parametrów
slider_h_zadane = Slider(title="Zadany poziom napełnienia zbiornika [%]", start=10, end=70, value=30, step=1)
slider_t_i = Slider(title="Czas zdwojenia [s]", start=5, end=100, value=20, step=0.5)
slider_t_d = Slider(title="Czas wyprzedzania [s]", start=1, end=100, value=5, step=1)
slider_kp = Slider(title="Wzmocnienie regulatora", start=0.0001, end=0.02, value=0.008, step=0.0001, format='0[.]0000')

sliders_list = [slider_h_zadane, slider_t_i, slider_t_d, slider_kp]

# Funkcja do aktualizacji danych
def data_update(attr, old, new):
    global T, H, u
    new_h_zadane = slider_h_zadane.value / 10

    t_i = slider_t_i.value
    t_d = slider_t_d.value
    kp = slider_kp.value

    T = [0]
    H = [0]
    e = [0.0]
    u = [0]

    for i in range(0, N):
        T.append(i * t_p / 60)
        e.append(new_h_zadane - H[i])
        u_temp = kp * (e[i] + t_p / t_i * sum(e) + (t_d / t_p) * (e[-1] - e[-2]))
        u.append(min(u_max, max(u_min, u_temp)))
        q_d = (((u[-1] - u_min) / (u_max - u_min)) * (q_max - q_min) + q_min)
        H.append(min(h_max, max(h_min, t_p * (q_d - B * sqrt(H[-1])) / A + H[-1])))

    # Zapis do bazy
    save_to_db(T, H, u)

    # Odczyt z bazy i aktualizacja źródła danych
    T_plot, H_plot = load_from_db()
    source.data = dict(x=T_plot, y=H_plot)

for slider in sliders_list:
    slider.on_change('value', data_update)

# Układ layout
layout = row([column(slider_h_zadane, slider_t_i, slider_t_d, slider_kp), p])
curdoc().add_root(layout)
