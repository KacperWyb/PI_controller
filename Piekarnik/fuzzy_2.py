from simpful import *
import matplotlib.pyplot as plt
import numpy as np


def create_fuzzy_pi():
    FS = FuzzySystem()

    # Definicja zakresów zmiennych
    error_range = [-30, 190]
    delta_error_range = [-40, 35]
    delta_u_range = [-1, 1]

    # Definicja funkcji przynależności dla błędu
    E_Neg = FuzzySet(function=Triangular_MF(a=-30, b=-20, c=-10), term="neg")
    E_Neg_l = FuzzySet(function=Triangular_MF(a=-20, b=-10, c=0), term="neg_l")
    E_Zero = FuzzySet(function=Triangular_MF(a=-1, b=0, c=1), term="zero")
    E_Pos_l = FuzzySet(function=Triangular_MF(a=0, b=50, c=70), term="pos_l")
    E_Pos = FuzzySet(function=Triangular_MF(a=20, b=125, c=190), term="pos")
    FS.add_linguistic_variable("error", LinguisticVariable(
        [E_Neg, E_Neg_l, E_Zero, E_Pos_l, E_Pos], universe_of_discourse=error_range))

    # Definicja funkcji przynależności dla zmiany błędu
    DE_Neg = FuzzySet(function=Triangular_MF(a=-40, b=-20, c=-10), term="neg")
    DE_Neg_l = FuzzySet(function=Triangular_MF(
        a=-20, b=-10, c=0), term="neg_l")
    DE_Zero = FuzzySet(function=Triangular_MF(a=-4, b=0, c=4), term="zero")
    DE_Pos_l = FuzzySet(function=Triangular_MF(a=0, b=10, c=20), term="pos_l")
    DE_Pos = FuzzySet(function=Triangular_MF(a=10, b=20, c=35), term="pos")
    FS.add_linguistic_variable("delta_error", LinguisticVariable(
        [DE_Neg, DE_Neg_l, DE_Zero, DE_Pos_l, DE_Pos], universe_of_discourse=delta_error_range))

    # Definicja funkcji przynależności dla zmiany sterowania
    DU_Decrease = FuzzySet(function=Triangular_MF(
        a=-1, b=-0.4, c=-0.10), term="decrease")
    DU_Decrease_l = FuzzySet(function=Triangular_MF(
        a=-0.2, b=-0.1, c=0), term="decrease_l")
    DU_NoChange = FuzzySet(function=Triangular_MF(
        a=-0.05, b=0, c=0.05), term="no_change")
    DU_Increase_l = FuzzySet(function=Triangular_MF(
        a=0, b=0.1, c=0.2), term="increase_l")
    DU_Increase = FuzzySet(function=Triangular_MF(
        a=0.10, b=0.4, c=1), term="increase")
    FS.add_linguistic_variable("delta_u", LinguisticVariable(
        [DU_Decrease, DU_Decrease_l, DU_NoChange, DU_Increase_l, DU_Increase], universe_of_discourse=delta_u_range))

    # Reguły sterowania
    rules = [
        "IF (error IS neg) AND (delta_error IS neg) THEN (delta_u IS decrease)",
        "IF (error IS neg) AND (delta_error IS neg_l) THEN (delta_u IS decrease_l)",
        "IF (error IS neg) AND (delta_error IS zero) THEN (delta_u IS decrease_l)",
        "IF (error IS neg) AND (delta_error IS pos_l) THEN (delta_u IS decrease_l)",
        "IF (error IS neg) AND (delta_error IS pos) THEN (delta_u IS no_change)",

        "IF (error IS neg_l) AND (delta_error IS neg) THEN (delta_u IS decrease)",
        "IF (error IS neg_l) AND (delta_error IS neg_l) THEN (delta_u IS decrease_l)",
        "IF (error IS neg_l) AND (delta_error IS zero) THEN (delta_u IS no_change)",
        "IF (error IS neg_l) AND (delta_error IS pos_l) THEN (delta_u IS no_change)",
        "IF (error IS neg_l) AND (delta_error IS pos) THEN (delta_u IS decrease_l)",

        "IF (error IS zero) AND (delta_error IS neg) THEN (delta_u IS decrease_l)",
        "IF (error IS zero) AND (delta_error IS neg_l) THEN (delta_u IS no_change)",
        "IF (error IS zero) AND (delta_error IS zero) THEN (delta_u IS no_change)",
        "IF (error IS zero) AND (delta_error IS pos_l) THEN (delta_u IS no_change)",
        "IF (error IS zero) AND (delta_error IS pos) THEN (delta_u IS increase_l)",

        "IF (error IS pos_l) AND (delta_error IS neg) THEN (delta_u IS increase_l)",
        "IF (error IS pos_l) AND (delta_error IS neg_l) THEN (delta_u IS no_change)",
        "IF (error IS pos_l) AND (delta_error IS zero) THEN (delta_u IS no_change)",
        "IF (error IS pos_l) AND (delta_error IS pos_l) THEN (delta_u IS increase_l)",
        "IF (error IS pos_l) AND (delta_error IS pos) THEN (delta_u IS increase)",

        "IF (error IS pos) AND (delta_error IS neg) THEN (delta_u IS no_change)",
        "IF (error IS pos) AND (delta_error IS neg_l) THEN (delta_u IS increase_l)",
        "IF (error IS pos) AND (delta_error IS zero) THEN (delta_u IS increase_l)",
        "IF (error IS pos) AND (delta_error IS pos_l) THEN (delta_u IS increase_l)",
        "IF (error IS pos) AND (delta_error IS pos) THEN (delta_u IS increase)"
    ]
    FS.add_rules(rules)
    return FS


def simulate_oven(FS, T_setpoint, T_ambient, P_max, k, cp, delta_t, sim_time):
    times, temperatures, power, Q_lost = [], [], [], []
    T = T_ambient
    prev_error = 0
    u = 0
    for t in range(0, sim_time, delta_t):
        if t == 100:
            T -= 30
        error = T_setpoint - T
        delta_error = error - prev_error
        prev_error = error

        # Ustawienie wartości wejściowych
        FS.set_variable("error", error)
        FS.set_variable("delta_error", delta_error)

        # Wyznaczenie sygnału sterującego
        u += FS.inference()["delta_u"]
        u = max(0, (min(u, 1)))
        P = 0.95 * u * P_max

        # Aktualizacja bilansu cieplnego
        Q_dostarczone = P * delta_t
        Q_utracone = k * (T - T_ambient) * delta_t

        delta_Temp = (Q_dostarczone - Q_utracone) / cp
        T += delta_Temp
        print(f"Error = {error} : Delta_Error = {delta_error} : ster = {u}")
        times.append(t)
        temperatures.append(T)
        power.append(P)
        Q_lost.append(Q_utracone)

    return times, temperatures, power, Q_lost
