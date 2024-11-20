from math import sqrt
from bokeh.io import curdoc, show
from bokeh.layouts import layout, column, row, gridplot
from bokeh.models import ColumnDataSource, Slider, PreText, Annotation, Label, LayoutDOM
from bokeh.plotting import figure
import csv

# PARAMETRY REGULATORA
t_i = 5  # stała całkowania / czas zdwojenia
kp = 0.02  # wzmocnienie regulatora


# PARAMETRY ZBIORNIKA
A = 1.5  # przekrój poprzeczny zbiornika
h_min = 0  # minimalna wysokość wody w zbiorniku
h_max = 5  # maksymalna wysokość wody w zbiorniku
B = 0.035  # współczynnik wypływu m/s
q_min = 0   # minimalna przepustowość dopływu w litrach / s
q_max = 50  # maksymalna przepustowość dopływu w litrach / s


# PARAMETRY SYMULACJI
t_p = 0.1  # okres próbkowania
czas_symulacji = 5  # w minutach
t_Sim = czas_symulacji * 60  # czas symulacji w sekundach
N = int(t_Sim / t_p)  # liczba próbek (dwie próbki na sekundę)
h_zadane = 3

# DANE
T = [0]     # próbki
H = [0]     # wysokość wody w zbiorniku
e = [0.0]  # Lista z wartościami uchybu
u = [0]     # wartość sterująca przekazana do urządzenia wykonawczego w celu zmiany natężenia dopływu wody do zbiornika
Q = [0.0]
u_min = 0
u_max = 10


for i in range(0, N):
    T.append(i * t_p / 60)
    e.append(h_zadane - H[i])  # wartość uchybu obliczana przez sumator
    u_temp = kp * (e[i] + (t_p / t_i) * sum(e))
    # zamiast kożystać z 2 "if'ów" wykonujemy min max aby wartość
    u.append(min(u_max, max(u_min, u_temp)))
    # przekazana do elementu wykonawczego była realna czyli 0<u<10 tak jak w poleceniu
    # po obliczeniu wartości sterującej
    q_d = (((u[-1] - u_min) / (u_max - u_min)) * (q_max - q_min) + q_min)
    Q.append(q_d)
    # wyznaczamy wartość natężenia dopływu
    # symulacja napełniania zbiornika,
    H.append(min(h_max, max(h_min, t_p * (q_d - B * sqrt(H[-1])) / A + H[-1])))
    # zmiana wysokości słupa wody w zbiorniku na przestrzeni czasu

# ustawienia wykresu
p = figure(title="Symulacja napełniania zbiornika o wymiarach: \nprzekrój poprzeczny: 2 m2 \nmaksymalna wysokość napełnienia: 10 m. \n"
                 "Maksymalna przepustowość dopływu: 50 l/s. \n"
                 "Współczynnik wypływu: 35 l/s.\n"
                 "Wysokość zadana 3m",
           x_axis_label="czas [min]", y_axis_label="wysokość wody w zbiorniku [m]")
p.title.text_font_size = "20px"
source = ColumnDataSource(data=dict(x=T, y=H))
p.line(source=source)
row = row([p])


p_1 = figure(title="Zależność wielkości sterującej od czasu",
             x_axis_label="czas [min]", y_axis_label="wielkość sterująca u(t)[V]")
p_1.title.text_font_size = "20px"
source_1 = ColumnDataSource(data=dict(x=T, y=Q))
p_1.line(source=source_1)

p_2 = figure(title="Zależność wielkości sterującej od czasu",
             x_axis_label="czas [min]", y_axis_label="wielkość sterująca u(t)[V]")
p_2.title.text_font_size = "20px"
source_2 = ColumnDataSource(data=dict(x=T, y=u))
p_2.line(source=source_2)

layout = column(p, p_1, p_2)

curdoc().add_root(layout)
