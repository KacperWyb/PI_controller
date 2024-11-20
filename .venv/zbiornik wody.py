import math
import numpy as np
import matplotlib.pyplot as plt

# Parametry symulacji
Tp = 0.1        # Krok czasowy w sekundach
A = 1.5         # Powierzchnia zbiornika lub pojemność
b = 0.035       # Współczynnik odpływu
q_inflow = 0.05 # Stała dopływu cieczy
h = [0.0]       # Początkowy poziom cieczy (lista do przechowywania wartości h)
tsim = 3600     # Czas symulacji w sekundach
N = int(tsim / Tp)  # Liczba kroków czasowych

# Pętla obliczeniowa - iteracyjne obliczanie poziomu h
for step in range(N):
    h_current = h[-1]  # Ostatnia wartość poziomu cieczy
    h_new = h_current + (q_inflow - b * math.sqrt(h_current)) * (Tp / A)  # Równanie różnicowe
    h.append(h_new)  # Dodanie nowej wartości do listy

# Wyświetlenie ostatnich 10 wartości poziomu h
print("Ostatnie wartości poziomu h:", h[-10:])

# wizualizacja poziomu cieczy w czasie
time_points = np.arange(0, tsim + Tp, Tp)  # Czasowe punkty pomiarowe
plt.plot(time_points, h, label="Poziom cieczy h(t)")
plt.xlabel("Czas [s]")
plt.ylabel("Poziom cieczy h")
plt.title("Symulacja poziomu cieczy w zbiorniku")
plt.legend()
plt.show()
