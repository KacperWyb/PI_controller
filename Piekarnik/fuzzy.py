from simpful import *
import matplotlib.pyplot as plt
import numpy as np

# Tworzenie rozmytego regulatora PI


def create_fuzzy_pi():
    FS = FuzzySystem()

    # Definicja zmiennych lingwistycznych
    error_range = [-501, 501]
    delta_error_range = [-201, 181]
    delta_u_range = [0, 2.1]

    # Definicja funkcji przynależności dla błędu
    E_Neg = FuzzySet(function=Triangular_MF(a=-500, b=-250, c=-50), term="neg")
    E_Zero = FuzzySet(function=Triangular_MF(a=-200, b=0, c=200), term="zero")
    E_Pos = FuzzySet(function=Triangular_MF(a=50, b=250, c=500), term="pos")
    FS.add_linguistic_variable("error", LinguisticVariable(
        [E_Neg, E_Zero, E_Pos], universe_of_discourse=error_range))

    # Definicja funkcji przynależności dla zmiany błędu
    DE_Neg = FuzzySet(function=Triangular_MF(a=-200, b=-100, c=0), term="neg")
    DE_Zero = FuzzySet(function=Triangular_MF(a=-50, b=0, c=100), term="zero")
    DE_Pos = FuzzySet(function=Triangular_MF(a=0, b=100, c=180), term="pos")
    FS.add_linguistic_variable("delta_error", LinguisticVariable(
        [DE_Neg, DE_Zero, DE_Pos], universe_of_discourse=delta_error_range))

    # Definicja funkcji przynależności dla zmiany sterowania
    DU_Decrease = FuzzySet(function=Triangular_MF(
        a=0, b=0.5, c=1), term="decrease")
    DU_NoChange = FuzzySet(function=Triangular_MF(
        a=0.5, b=1, c=1.5), term="no_change")
    DU_Increase = FuzzySet(function=Triangular_MF(
        a=1, b=1.5, c=2), term="increase")
    FS.add_linguistic_variable("delta_u", LinguisticVariable(
        [DU_Decrease, DU_NoChange, DU_Increase], universe_of_discourse=delta_u_range))

    # Reguły sterowania
    rules = [
        "IF (error IS neg) AND (delta_error IS neg) THEN (delta_u IS decrease)",
        "IF (error IS neg) AND (delta_error IS zero) THEN (delta_u IS decrease)",
        "IF (error IS neg) AND (delta_error IS pos) THEN (delta_u IS no_change)",
        "IF (error IS zero) AND (delta_error IS neg) THEN (delta_u IS decrease)",
        "IF (error IS zero) AND (delta_error IS zero) THEN (delta_u IS no_change)",
        "IF (error IS zero) AND (delta_error IS pos) THEN (delta_u IS increase)",
        "IF (error IS pos) AND (delta_error IS neg) THEN (delta_u IS no_change)",
        "IF (error IS pos) AND (delta_error IS zero) THEN (delta_u IS increase)",
        "IF (error IS pos) AND (delta_error IS pos) THEN (delta_u IS increase)"
    ]
    FS.add_rules(rules)
    return FS


# Symulacja piekarnika
def simulate_oven(FS, T_otoczenia, T_docelowa, T_start, P_max, k, c, m, delta_t, sim_time):
    times = []
    temperatures = []
    T = T_start
    integral_error = 0  # Początkowy błąd całkowity
    ster = []
    grzalka_cooling_rate = 0.0012
    T_grzalka = T_start
    for t in range(0, sim_time, delta_t):
        # Obliczanie różnicy temperatury
        uchyb = T_docelowa - T

        # Aktualizacja błędu całkowitego
        integral_error = max(-500, min(integral_error + uchyb * delta_t, 500))

        # Ustawienie wejść do systemu rozmytego
        FS.set_variable("error", integral_error)
        FS.set_variable("delta_error", uchyb)

        # Obliczenie mocy grzałki
        P = FS.inference()["delta_u"]

        # Bilans cieplny
        Q_utracone = k * (T - T_otoczenia) * delta_t
        # Zmiana energii na temperaturę (°C)
        T_utracone = (Q_utracone / (m * c))

        # Obliczanie temperatury grzałki
        # grzałka ochładza się w zależności od tego jaka jest różnica temperatury pomiędzy temperaturą piekarnika a temperaturą grzałki
        T_grzalka += (P * delta_t) - \
            ((grzalka_cooling_rate * (T_grzalka - T) * delta_t) / (m*c))
        # Temperatura grzałki nie może spaść poniżej otoczenia
        T_grzalka = max(T, T_grzalka)

        # Aktualizacja temperatury
        T += round(0.15 * (T_grzalka - T) - T_utracone, 3)

        # Zapisywanie wyników
        times.append(t)
        temperatures.append(T)
        ster.append(P)
        print(uchyb)

    return times, temperatures, ster

# Wizualizacja wyników symulacji


def plot_results(times, temperatures):
    plt.figure(figsize=(10, 6))
    plt.plot(times, temperatures, label="Temperatura piekarnika", linewidth=2)
    plt.axhline(y=200, color='r', linestyle='--',
                label="Temperatura docelowa (200°C)")
    plt.xlabel("Czas (s)")
    plt.ylabel("Temperatura (°C)")
    plt.title("Symulacja piekarnika z rozmytym regulatorem PI")
    plt.legend()
    plt.grid()
    plt.show()


# Parametry symulacji
T_otoczenia = 20  # Temperatura otoczenia (°C)
T_docelowa = 200  # Docelowa temperatura piekarnika (°C)
T_start = 20  # Początkowa temperatura piekarnika (°C)
P_max = 2  # Maksymalna moc grzałki (kW)
k = 0.006  # Współczynnik strat cieplnych (kW/°C)
c = 1.2  # Pojemność cieplna powietrza (kJ/(kg·°C))
m = 50 / 1000 * 1.2  # Masa powietrza (kg)
delta_t = 1  # Krok czasowy (s)
sim_time = 1000  # Czas symulacji (s)

# Tworzenie regulatora Fuzzy PI
FS = create_fuzzy_pi()

# Uruchomienie symulacji
times, temperatures, ster = simulate_oven(
    FS, T_otoczenia, T_docelowa, T_start, P_max, k, c, m, delta_t, sim_time)

# Wizualizacja wyników
plot_results(times, temperatures)


def plot_results(times, temperatures):
    plt.figure(figsize=(10, 6))
    plt.plot(times, temperatures, label="Temperatura piekarnika", linewidth=2)
    plt.axhline(y=3, color='r', linestyle='--',
                label="Temperatura docelowa (200°C)")
    plt.xlabel("Czas (s)")
    plt.ylabel("Temperatura (°C)")
    plt.title("Symulacja piekarnika z rozmytym regulatorem PI")
    plt.legend()
    plt.grid()
    plt.show()


plot_results(times, ster)
