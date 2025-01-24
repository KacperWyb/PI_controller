import numpy as np
from math import sqrt
from bokeh.io import curdoc, show
from bokeh.layouts import layout, column, row, gridplot
from bokeh.models import CustomJS, ColumnDataSource, Slider, Button
from bokeh.plotting import figure
import csv

# Slider do aktualizacji parametrów
slider_T_zadane = Slider(
    title="Zadana temperatura [°C]", start=100, end=200, value=200, step=10)
slider_ki = Slider(
    title="Wzmocnienie całkujące [s]", start=5, end=100, value=10, step=5)
slider_kp = Slider(title="Wzmocnienie proporcjonalne", start=0.0001,
                   end=0.01, value=0.0006, step=0.0005, format='0[.]0000')
sliders_list = [slider_T_zadane, slider_ki, slider_kp]


def update_temperature_PI(T, T_docelowa, k, T_otoczenia, m, c, delta_t, skumulowany_uchyb, T_grzalka, Kp_local, Ki_local):
    """
    Oblicza nową temperaturę piekarnika po jednym kroku czasowym za pomocą regulatora PI.

    Args:
        T (float): Aktualna temperatura piekarnika (°C).
        T_docelowa (float): Docelowa temperatura (°C).
        k (float): Współczynnik strat cieplnych (kW/°C).
        T_otoczenia (float): Temperatura otoczenia (°C).
        m (float): Masa powietrza w piekarniku (kg).
        c (float): Pojemność cieplna powietrza (kJ/(kg·°C)).
        delta_t (float): Krok czasowy (s).
        skumulowany_uchyb (float): Skumulowany błąd (°C·s).
        T_grzalka (float): Aktualna temperatura grzałki (°C).

    Returns:
        float: Nowa temperatura piekarnika (°C).
        float: Zaktualizowany skumulowany błąd.
        float: Nowa temperatura grzałki (°C).
    """
    # Obliczanie błędu
    error = T_docelowa - T

    # Aktualizacja skumulowanego błędu
    skumulowany_uchyb += error * delta_t

    # Wyznaczenie mocy grzałki na podstawie regulatora PI
    P = Kp_local * (error + ((delta_t / Ki_local) * skumulowany_uchyb))
    # Ograniczenie mocy grzałki do zakresu [0, 2.0 kW]
    P = max(0, min(P, P_max))

    # Obliczanie dostarczonej mocy do grzałki - sygnał sterujący
    Q_dostarczone = P * delta_t
    # Energia utracona poprzez nie perfekcyjną izolację piekarnika (kJ)
    Q_utracone = k * (T - T_otoczenia) * delta_t
    T_utracone = (Q_utracone / (m * c))   # Zmiana energii na temperaturę (°C)

    # Obliczanie temperatury grzałki
    # grzałka ochładza się w zależności od tego jaka jest różnica temperatury pomiędzy temperaturą piekarnika a temperaturą grzałki
    T_grzalka += (P * delta_t) - \
        ((grzalka_cooling_rate * (T_grzalka - T) * delta_t) / (m*c))
    # Temperatura grzałki nie może spaść poniżej otoczenia
    T_grzalka = max(T, T_grzalka)

    # Temperatura dostarczona przez grzałkę
    delta_T = 0.15 * (T_grzalka - T) - T_utracone

    return T + delta_T, skumulowany_uchyb, T_grzalka, T_utracone, P


# Parametry fizyczne piekarnika
k = 0.006  # Współczynnik strat cieplnych (kW/°C)
T_otoczenia = 20  # Temperatura otoczenia (°C)
V = 50  # Objętość piekarnika (litry)
rho = 1.2  # Gęstość skumulowany_uchybpowietrza (kg/m³)
c = 1.2  # Pojemność cieplna powietrza (kJ/(kg·°C))
m = V/1000 * rho  # Masa powietrza w piekarniku (kg)
P_max = 2  # Górny zakres mocy grzałki (kW)
# m * c ==> energia potrzebna do zmiany temperatury powietrza o jeden stopień celcjusza

# Parametry grzałki
T_grzalka = 20  # Początkowa temperatura grzałki (°C)
grzalka_cooling_rate = 0.0012  # Współczynnik chłodzenia grzałki (°C/s)

# Listy do przechowywania danych do wykresu
time = []
temperatura_piekarnik = []
temperatura_grzalka = []
temperatura_strata = []
wartosc_sterujaca = []

# Inicjacja wykresu
# Parametry regulatora PI
Kp = 0.0005  # Wzmocnienie proporcjonalne
Ki = 10  # Wzmocnienie całkujące
skumulowany_uchyb = 0  # Skumulowany błąd

# Parametry symulacji
T = T_otoczenia  # Początkowa temperatura piekarnika (°C)
T_docelowa = 200  # Docelowa temperatura (°C)
delta_t = 1  # Krok czasowy (s)
sim_time = 2000  # Czas symulacji (s)
total_time = 0  # Czas trwania symulacji (s)


# Symulacja
while total_time < sim_time:
    T, skumulowany_uchyb, T_grzalka, T_utracone, P = update_temperature_PI(
        T, T_docelowa, k, T_otoczenia, m, c, delta_t, skumulowany_uchyb, T_grzalka, Kp, Ki)
    total_time += delta_t
    time.append(total_time)
    temperatura_piekarnik.append(T)
    temperatura_grzalka.append(T_grzalka)
    temperatura_strata.append(T_utracone)
    wartosc_sterujaca.append(P)


# ustawienia wykresu
p = figure(title="Symulacja nagrzewania piekarnika o objętości 50 l\n"
                 "Moc grzałki 2 Kw \n"
                 "Współczynnik strat cieplnych piekarnika 0.006 kW/°C\n"
                 "Współczynnik strat cieplnych grzałki 0012 kW/°C\n"
                 "Temperatura otoczenia 20 °C\n"
                 "Docelowa temperatura 200 °C",
           x_axis_label="czas [min]", y_axis_label="Temperatura wewnątrz piekarnika [°C]")
p.title.text_font_size = "20px"
source = ColumnDataSource(data=dict(x=time, y=temperatura_piekarnik))
p.line(source=source)
row = row([p])

p_1 = figure(title="Zależność temperatury grzałki wewnątrz piekarnika od czasu",
             x_axis_label="czas [s]", y_axis_label="Temperatura grzałki [°C]")
p_1.title.text_font_size = "20px"
source_1 = ColumnDataSource(data=dict(x=time, y=temperatura_grzalka))
p_1.line(source=source_1)

p_2 = figure(title="Zależność sygnału sterującego od czasu",
             x_axis_label="czas [min]", y_axis_label="Moc [Kw]")
p_2.title.text_font_size = "20px"
source_2 = ColumnDataSource(data=dict(x=time, y=wartosc_sterujaca))
p_2.line(source=source_2)

p_3 = figure(title="Utrata temperatury na przestrzeni czasu",
             x_axis_label="czas [min]", y_axis_label="Temperatura utracona [°C]")
p_3.title.text_font_size = "20px"
source_3 = ColumnDataSource(data=dict(x=time, y=temperatura_strata))
p_3.line(source=source_3)


def chart_update(attr, old, new):
    global time, temperatura_piekarnik, temperatura_grzalka, temperatura_strata, wartosc_sterujaca, T_grzalka

    # Parametry regulatora PI
    Kp = slider_kp.value  # Wzmocnienie proporcjonalne
    Ki = slider_ki.value  # Wzmocnienie całkujące
    skumulowany_uchyb = 0  # Skumulowany błąd

    time = []
    temperatura_piekarnik = []
    temperatura_grzalka = []
    temperatura_strata = []
    wartosc_sterujaca = []

    # Parametry symulacji
    T = T_otoczenia  # Początkowa temperatura piekarnika (°C)
    T_grzalka = T_otoczenia
    T_docelowa = slider_T_zadane.value  # Docelowa temperatura (°C)
    delta_t = 1  # Krok czasowy (s)
    sim_time = 2000  # Czas symulacji (s)v

    for i in range(0, sim_time):
        T, skumulowany_uchyb, T_grzalka, T_utracone, P = update_temperature_PI(
            T, T_docelowa, k, T_otoczenia, m, c, delta_t, skumulowany_uchyb, T_grzalka, Kp, Ki)
        time.append(i)
        temperatura_piekarnik.append(T)
        temperatura_grzalka.append(T_grzalka)
        temperatura_strata.append(T_utracone)
        wartosc_sterujaca.append(P)
        print(
            f"Czas: {i}s, Temperatura: {T:.2f}°C, Temperatura grzałki: {T_grzalka:.2f}°C")

    # Aktualizacja danych na wykresach
    source.data = dict(x=time, y=temperatura_piekarnik)
    source_1.data = dict(x=time, y=temperatura_grzalka)
    source_2.data = dict(x=time, y=wartosc_sterujaca)
    source_3.data = dict(x=time, y=temperatura_strata)


for slider in sliders_list:
    slider.on_change('value', chart_update)

page = layout([slider_T_zadane, column(
    slider_ki, slider_kp, p, p_1, p_2, p_3)])

curdoc().add_root(page)
