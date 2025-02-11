import numpy as np
from math import sqrt
from bokeh.io import curdoc, show
from bokeh.layouts import layout, column, row, gridplot
from bokeh.models import CustomJS, ColumnDataSource, Slider, Button, CustomJS
from bokeh.plotting import figure
from simpful import *
from fuzzy_2 import create_fuzzy_pi, simulate_oven
import csv

""" OPIS
Grzałka nagrzewa powietrze wewnątrz piekarnika (Konwekcja) oraz ścianki piekarnika (Promieniowanie).
Dlatego mierzymy 2 razy utratę ciepła:
- straty cieplne piekarnika (nieszczelność, nie perfekcyjna izolacja) 
- schładzanie się gorącej grzałki (oddawanie ciepła cząstkowego do powietrza) (pomijamy w tym kroku promieniowanie)
Ogrzewanie piekarnika obliczamy również na dwa sposoby:
- Temperatura wytworzona przez grzałkę (powietrze przy grzałce)

WZORY
Q = m * cp * Δ𝑇
Δ𝑇 = Q / (m*C)
Q : ilość energii potrzebnej do podgrzania powietrza [J]
m : masa powietrza w piekarniku [kg]
cp : ciepło właściwe powietrza ≈1005 J/(kg·°C)
Δ𝑇 : przyrost temperatury [°C]

1 Wat = 1 dżul na sekundę
2.5kW  w ciągu 1 sekundy = 2500 Dżuli

Gęstość Powietrza = 1.2 [kg/m^3]
Pojemność Piekarnika = 60 [l]
Masa Powietrza w piekarniku 1200g / 10000 * 60 = 7.2 [gr]
Ciepło właściwe powietrza: c = 1.005 [kJ / kg * °C]
Pojemność cieplna : pc = m * c [kJ / °C]
 """

# Slider do aktualizacji parametrów
slider_T_zadane = Slider(
    title="Zadana temperatura [°C]", start=100, end=200, value=200, step=10)
slider_Ti = Slider(
    title="Wzmocnienie całkujące [s]", start=1, end=10, value=1, step=0.5)
slider_kp = Slider(title="Wzmocnienie proporcjonalne", start=0.0001,
                   end=0.002, value=0.001, step=0.0001, format='0[.]0000')
sliders_list = [slider_T_zadane, slider_Ti, slider_kp]


def update_temperature_PI(T, T_docelowa, k, T_otoczenia, cp, delta_t, skumulowany_uchyb, Kp_local, Ti_local):
    # Oblicza nową temperaturę piekarnika po jednym kroku czasowym za pomocą regulatora PI.
    # Obliczanie błędu
    uchyb = T_docelowa - T

    # Aktualizacja skumulowanego błędu
    skumulowany_uchyb += uchyb * delta_t

    # Wyznaczenie mocy grzałki na podstawie regulatora PI
    Q = max(0, min(Kp_local * (uchyb + ((delta_t / Ti_local) * skumulowany_uchyb)), 1))

    # Ograniczenie mocy grzałki do zakresu [0, 2 kW]
    P = 0.95 * Q * P_max

    # Obliczanie dostarczonej mocy do grzałki - sygnał sterujący [kW * s = kJ] [Kilo Dżul]
    Q_dostarczone = P * delta_t
    # Energia utracona poprzez nie perfekcyjną izolację piekarnika [kW * s = kJ] [Kilo Dżul]
    Q_utracone = k * (T - T_otoczenia) * delta_t

    # Temperatura dostarczona przez grzałkę [kJ / kJ / °C = kJ * °C / kJ = °C] [°C]
    delta_T = (Q_dostarczone - Q_utracone) / cp

    return T + delta_T, skumulowany_uchyb, Q_utracone, P


# Parametry fizyczne piekarnika
k = 0.006  # Współczynnik strat cieplnych (kW/°C)
T_otoczenia = 20  # Temperatura otoczenia (°C)
V = 50  # Objętość piekarnika (litry)
rho = 1.2  # Gęstość powietrza (kg/m³)
m = V/1000 * rho  # Masa powietrza w piekarniku (kg)
c = 1.005  # ciepło właściwe (kJ/(kg·°C))
cp = c * m  # pojemność cieplna [kJ/°C]
P_max = 2  # Górny zakres mocy grzałki (kW)


# Listy do przechowywania danych do wykresu
time = []
temperatura_piekarnik = []
temperatura_strata = []
wartosc_sterujaca = []

# Inicjacja wykresu
# Parametry regulatora PI
Kp = 0.0005  # Wzmocnienie proporcjonalne
Ti = 10  # Wzmocnienie całkujące
skumulowany_uchyb = 0  # Skumulowany uchyb

# Parametry symulacji
T = T_otoczenia  # Początkowa temperatura piekarnika (°C)
T_docelowa = 200  # Docelowa temperatura (°C)
delta_t = 1  # Krok czasowy (s)
sim_time = 200  # Czas symulacji (s)
total_time = 0  # Czas trwania symulacji (s)


# Symulacja zwypły PI
while total_time < sim_time:
    T, skumulowany_uchyb, T_utracone, P = update_temperature_PI(
        T, T_docelowa, k, T_otoczenia, cp, delta_t, skumulowany_uchyb, Kp, Ti)
    total_time += delta_t
    time.append(total_time)
    temperatura_piekarnik.append(T)
    temperatura_strata.append(T_utracone)
    wartosc_sterujaca.append(P)

# wywołanie symulacji PI rozmyty
FS = create_fuzzy_pi()
times_fuzzy, temperatures_fuzzy, power_fuzzy = simulate_oven(
    FS, T_docelowa, T_otoczenia, P_max, k, cp, delta_t, sim_time)

# ustawienia wykresu
p = figure(title="Symulacja nagrzewania piekarnika o objętości 50 l\n"
                 "Moc grzałki 2 Kw \n"
                 "Współczynnik strat cieplnych piekarnika 0.006 kW/°C\n"
                 "Temperatura otoczenia 20 °C\n"
                 f"Docelowa temperatura {T_otoczenia} °C",
           x_axis_label="czas [s]", y_axis_label="Temperatura wewnątrz piekarnika [°C]")
p.title.text_font_size = "20px"
source = ColumnDataSource(data=dict(x=time, y=temperatura_piekarnik))
p.line(source=source)


p_1 = figure(title="Zależność straty energii od czasu",
             x_axis_label="czas [s]", y_axis_label="Utracona energia [kJ]")
p_1.title.text_font_size = "20px"
source_2 = ColumnDataSource(data=dict(x=time, y=temperatura_strata))
p_1.line(source=source_2)

p_2 = figure(title="Zależność sygnału sterującego od czasu",
             x_axis_label="czas [s]", y_axis_label="Moc [kW]")
p_2.title.text_font_size = "20px"
source_3 = ColumnDataSource(data=dict(x=time, y=wartosc_sterujaca))
p_2.line(source=source_3)

p_4 = figure(title="Nagrzewanie piekarnika z wykorzystaniem Fuzzy PI",
             x_axis_label="czas [s]", y_axis_label="Temperatura wewnątrz piekarnika [°C]")
p_4.title.text_font_size = "20px"
source_4 = ColumnDataSource(data=dict(x=times_fuzzy, y=temperatures_fuzzy))
p_4.line(source=source_4)

p_5 = figure(title="Zależność sygnału sterującego od czasu",
             x_axis_label="czas [s]", y_axis_label="Moc [kW]")
p_5.title.text_font_size = "20px"
source_5 = ColumnDataSource(data=dict(x=times_fuzzy, y=power_fuzzy))
p_5.line(source=source_5)


def chart_update():
    global time, temperatura_piekarnik, temperatura_grzalka, temperatura_strata, wartosc_sterujaca, T_grzalka

    # Parametry regulatora PI
    Kp = slider_kp.value  # Wzmocnienie proporcjonalne
    Ti = slider_Ti.value  # Wzmocnienie całkujące
    skumulowany_uchyb = 0  # Skumulowany uchyb

    time = []
    temperatura_piekarnik = []
    temperatura_grzalka = []
    temperatura_strata = []
    wartosc_sterujaca = []
    times_fuzzy = []
    temperatures_fuzzy = []
    power_fuzzy = []

    # Parametry symulacji
    T = T_otoczenia  # Początkowa temperatura piekarnika (°C)
    T_docelowa = slider_T_zadane.value  # Docelowa temperatura (°C)
    delta_t = 1  # Krok czasowy (s)
    sim_time = 400  # Czas symulacji (s)v

    # Symulacja zwykły PI
    for i in range(0, sim_time):
        T, skumulowany_uchyb, T_utracone, P = update_temperature_PI(
            T, T_docelowa, k, T_otoczenia, cp, delta_t, skumulowany_uchyb, Kp, Ti)
        time.append(i)
        temperatura_piekarnik.append(T)
        temperatura_strata.append(T_utracone)
        wartosc_sterujaca.append(P)
        print(
            f"Czas: {i}s, Temperatura: {T:.2f}°C")

    # Symulacja PI Rozmyty
    FS = create_fuzzy_pi()
    times_fuzzy, temperatures_fuzzy, power_fuzzy = simulate_oven(
        FS, T_docelowa, T_otoczenia, P_max, k, cp, delta_t, sim_time)

    # Aktualizacja danych na wykresach
    source.data = dict(x=time, y=temperatura_piekarnik)
    source_2.data = dict(x=time, y=temperatura_strata)
    source_3.data = dict(x=time, y=wartosc_sterujaca)
    source_4.data = dict(x=times_fuzzy, y=temperatures_fuzzy)
    source_5.data = dict(x=times_fuzzy, y=power_fuzzy)


button = Button(label="Wygeneruj grafy",
                button_type="danger")

button.on_click(chart_update)


page = layout([row(button, slider_T_zadane, slider_Ti, slider_kp),
              row(column(p), column(p_1), column(p_2)),
              row(column(p_4), column(p_5))])


curdoc().add_root(page)
