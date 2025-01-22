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


def update_temperature_PI(T, T_docelowa, k, T_otoczenia, m, c, delta_t, integral_error, T_grzalka):
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
        T_grzalka (float): Aktualna temperatura grzałki (°C).

    Returns:
        float: Nowa temperatura piekarnika (°C).
        float: Zaktualizowany skumulowany błąd.
        float: Nowa temperatura grzałki (°C).
    """
    # Obliczanie błędu
    error = T_docelowa - T

    # Aktualizacja skumulowanego błędu
    integral_error += error * delta_t

    # Wyznaczenie mocy grzałki na podstawie regulatora PI
    P = Kp * (error + ((delta_t / Ki) * integral_error))
    # Ograniczenie mocy grzałki do zakresu [0, 2.0 kW]
    P = max(0, min(P, P_max))

    # Obliczanie dostarczonej mocy do grzałki - sygnał sterujący
    Q_dostarczone = P * delta_t
    # Energia utracona poprzez nie perfekcyjną izolację piekarnika (kJ)
    Q_utracone = k * (T - T_otoczenia) * delta_t
    T_utracone = (Q_utracone / (m * c))   # Zmiana energii na temperaturę (°C)

    print(f"kilo waty {Q_dostarczone}\dCiepło utracone {T_utracone}")

    # Obliczanie temperatury grzałki
    # grzałka ochładza się w zależności od tego jaka jest różnica temperatury pomiędzy temperaturą piekarnika a temperaturą grzałki
    T_grzalka += (P * delta_t) - \
        ((grzalka_cooling_rate * (T_grzalka - T) * delta_t) / (m*c))
    # Temperatura grzałki nie może spaść poniżej otoczenia
    T_grzalka = max(T, T_grzalka)

    # Temperatura dostarczona przez grzałkę
    delta_T = 0.15 * (T_grzalka - T) - T_utracone

    return T + delta_T, integral_error, T_grzalka


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
Kp = 0.0005  # Wzmocnienie proporcjonalne
Ki = 10  # Wzmocnienie całkujące
integral_error = 0  # Skumulowany błąd

# Parametry grzałki
T_grzalka = 20  # Początkowa temperatura grzałki (°C)
grzalka_cooling_rate = 0.0012  # Współczynnik chłodzenia grzałki (°C/s)

# Parametry symulacji
T = T_otoczenia  # Początkowa temperatura piekarnika (°C)
T_docelowa = 200  # Docelowa temperatura (°C)
delta_t = 1  # Krok czasowy (s)
sim_time = 2000  # Czas symulacji (s)
total_time = 0  # Czas trwania symulacji (s)
T_grzalka = 20  # Początkowa temperatura grzałki (°C)

# Listy do przechowywania danych do wykresu
times = []
temperatura_piekarnik = []
temperatura_grzalka = []
temperatura_strata = []

# Symulacja
while total_time < sim_time:
    T, integral_error, T_grzalka = update_temperature_PI(
        T, T_docelowa, k, T_otoczenia, m, c, delta_t, integral_error, T_grzalka)
    total_time += delta_t
    times.append(total_time)
    temperatura_piekarnik.append(T)
    print(
        f"Czas: {total_time}s, Temperatura: {T:.2f}°C, Temperatura grzałki: {T_grzalka:.2f}°C")

print(
    f"Osiągnięto temperaturę docelową {T_docelowa}°C po {total_time} sekundach.")

# Wyświetlenie wykresu
plot_temperature(times, temperatura_piekarnik)
