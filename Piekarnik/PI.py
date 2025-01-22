import numpy as np
import matplotlib.pyplot as plt


def plot_temperature(times, temperatures):
    """
    Wyświetla wykres zmiany temperatury w czasie.

    Args:
        times (list of float): Lista czasów (sekundy).
        temperatures (list of float): Lista temperatur (°C).
    """
    plt.figure(figsize=(10, 6))
    plt.plot(times, temperatures, label="Temperatura piekarnika", linewidth=2)
    plt.axhline(y=200, color='r', linestyle='--',
                label="Temperatura docelowa (200°C)")
    plt.xlabel("Czas (s)")
    plt.ylabel("Temperatura (°C)")
    plt.title("Zmiana temperatury w czasie")
    plt.legend()
    plt.grid()
    plt.show()


def update_temperature_PI(T, T_docelowa, k, T_otoczenia, m, c, delta_t, integral_error):
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
        integral_error (float): Skumulowany błąd (°C·s).

    Returns:
        float: Nowa temperatura piekarnika (°C).
        float: Zaktualizowany skumulowany błąd.
    """

    # Obliczanie uchybu
    error = T_docelowa - T

    # Aktualizacja skumulowanego uchybu
    # Maksymalny błąd całkujący (ustawiony na podstwie wykonanych doświadczeń)
    max_integral_error = 1000
    integral_error += error * delta_t
    integral_error = max(-max_integral_error,
                         min(integral_error, max_integral_error))

    # Wyznaczenie mocy grzałki na podstawie regulatora PI
    P = Kp * (error + ((delta_t / Ki) * integral_error))
    P = max(0, min(P, 2))  # Ograniczenie mocy grzałki do zakresu [0, 2.0 kW]

    # Obliczanie zmiany temperatury
    Q_dostarczone = P * delta_t  # Energia dostarczona przez grzałkę (kJ)
    Q_utracone = k * (T - T_otoczenia)  # Energia utracona (kJ)
    delta_Q = Q_dostarczone - Q_utracone  # Energia netto (kJ)
    delta_T = delta_Q / (m * c)  # Zmiana temperatury (°C)

    return T + delta_T, integral_error


# Parametry fizyczne
k = 0.006  # Współczynnik strat cieplnych (kW/°C)
T_otoczenia = 20  # Temperatura otoczenia (°C)
V = 50  # Objętość piekarnika (litry)
rho = 1.2  # Gęstość powietrza (kg/m³)
c = 1.2  # Pojemność cieplna powietrza (kJ/(kg·°C))
m = V/1000 * rho  # Masa powietrza w piekarniku (kg)
P_max = 2  # Górny zakres mocy grzałki (kW)
# m * c ==> energia potrzebna do zmiany temperatury powietrza o jeden stopień celcjusza


# Parametry regulatora PI
Kp = 0.2  # Wzmocnienie proporcjonalne
Ki = 7  # Wzmocnienie całkujące
integral_error = 0  # Skumulowany błąd

# Wywołanie symulacji - konfiguracja
T = 20  # Początkowa temperatura piekarnika (°C)
T_docelowa = 200  # Docelowa temperatura (°C)
delta_t = 1  # Krok czasowy (s)
sim_time = 13000  # Czas symulacji (s)

# Zmienne pomocnicze do przechowywania danych do wykresu
times = []
temperatures = []
total_time = 0

# Symulacja
while total_time < sim_time:
    T, integral_error = update_temperature_PI(
        T, T_docelowa, k, T_otoczenia, m, c, delta_t, integral_error)
    total_time += delta_t
    times.append(total_time)
    temperatures.append(T)
    print(f"Czas: {total_time}s, Temperatura: {T:.2f}°C")

# Wyświetlenie wykresu
plot_temperature(times, temperatures)

print(
    f"Osiągnięto temperaturę docelową {T_docelowa}°C po {total_time} sekundach.")
