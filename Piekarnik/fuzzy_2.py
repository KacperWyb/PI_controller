from simpful import *
import matplotlib.pyplot as plt
import numpy as np


def create_fuzzy_pi():
    FS = FuzzySystem()

    # Definicja zakresów zmiennych
    error_range = [-100, 190]
    delta_error_range = [-40, 30]
    delta_u_range = [0, 1]

    # Definicja funkcji przynależności dla błędu
    E_Neg = FuzzySet(function=Triangular_MF(a=-100, b=-25, c=0), term="neg")
    E_Zero = FuzzySet(function=Triangular_MF(a=-3, b=0, c=3), term="zero")
    E_Pos = FuzzySet(function=Triangular_MF(a=0, b=125, c=190), term="pos")
    FS.add_linguistic_variable("error", LinguisticVariable(
        [E_Neg, E_Zero, E_Pos], universe_of_discourse=error_range))

    # Definicja funkcji przynależności dla zmiany błędu
    DE_Neg = FuzzySet(function=Triangular_MF(a=-40, b=-20, c=0), term="neg")
    DE_Zero = FuzzySet(function=Triangular_MF(a=-7, b=0, c=7), term="zero")
    DE_Pos = FuzzySet(function=Triangular_MF(a=0, b=20, c=30), term="pos")
    FS.add_linguistic_variable("delta_error", LinguisticVariable(
        [DE_Neg, DE_Zero, DE_Pos], universe_of_discourse=delta_error_range))

    # Definicja funkcji przynależności dla zmiany sterowania
    DU_Decrease = FuzzySet(function=Triangular_MF(
        a=0.3, b=0.35, c=0.5), term="decrease")
    DU_NoChange = FuzzySet(function=Triangular_MF(
        a=0.4, b=0.55, c=0.7), term="no_change")
    DU_Increase = FuzzySet(function=Triangular_MF(
        a=0.6, b=0.9, c=1), term="increase")
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


def simulate_oven(FS, T_setpoint, T_ambient, P_max, k, cp, delta_t, sim_time):
    times, temperatures, power = [], [], []
    T = T_ambient
    prev_error = 0
    for t in range(0, sim_time, delta_t):
        error = T_setpoint - T
        delta_error = error - prev_error
        prev_error = error

        # Ustawienie wartości wejściowych
        FS.set_variable("error", error)
        FS.set_variable("delta_error", delta_error)

        # Wyznaczenie sygnału sterującego
        P = FS.inference()["delta_u"] * P_max

        # Aktualizacja bilansu cieplnego
        Q_dostarczone = P * delta_t
        Q_utracone = k * (T - T_ambient) * delta_t

        delta_Temp = (Q_dostarczone - Q_utracone) / cp
        T += delta_Temp

        times.append(t)
        temperatures.append(T)
        power.append(P)

    return times, temperatures, power


def plot_results(times, temperatures, power):
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

    plt.figure(figsize=(10, 6))
    plt.plot(times, power, label="Moc grzałki", linewidth=2, color='orange')
    plt.xlabel("Czas (s)")
    plt.ylabel("Moc (kW)")
    plt.title("Sterowanie mocą grzałki")
    plt.legend()
    plt.grid()
    plt.show()


# Parametry symulacji
T_ambient = 20  # Temperatura otoczenia (°C)
T_setpoint = 200  # Temperatura docelowa (°C)
P_max = 2  # Maksymalna moc grzałki (kW)
k = 0.006  # Współczynnik strat cieplnych (kW/°C)
rho = 1.2  # Gęstość powietrza (kg/m³)
V = 50  # Objętość piekarnika (litry)
m = V / 1000 * rho  # Masa powietrza (kg)
c = 1.005  # ciepło właściwe (kJ/(kg·°C))
cp = c * m  # pojemność cieplna [kJ/°C]
delta_t = 1  # Krok czasowy (s)
sim_time = 100  # Czas symulacji (s)

# Inicjalizacja regulatora Fuzzy PI
FS = create_fuzzy_pi()

# Uruchomienie symulacji
times, temperatures, power = simulate_oven(
    FS, T_setpoint, T_ambient, P_max, k, cp, delta_t, sim_time)

# Wizualizacja wyników
plot_results(times, temperatures, power)
