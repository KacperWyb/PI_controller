from simpful import *
import matplotlib.pyplot as plt

# Tworzenie rozmytego regulatora PI
def make_points(a, b, c, num_points=100):
    """
    Generuje punkty dla trójkątnego zbioru rozmytego.

    Args:
        a (float): Początek zakresu.
        b (float): Wierzchołek trójkąta.
        c (float): Koniec zakresu.
        num_points (int): Liczba punktów do wygenerowania.

    Returns:
        list: Lista punktów [(x1, y1), (x2, y2), ...].
    """
    import numpy as np

    x_left = np.linspace(a, b, num_points // 2)
    y_left = np.linspace(0, 1, num_points // 2)

    x_right = np.linspace(b, c, num_points // 2)
    y_right = np.linspace(1, 0, num_points // 2)

    x = np.concatenate((x_left, x_right))
    y = np.concatenate((y_left, y_right))

    return list(zip(x, y))

def create_fuzzy_pi():
    FS = FuzzySystem()

    # Różnica temperatury (wejście)
    S1 = FuzzySet(points=make_points(-100, 50, 50), term="zimno")
    S2 = FuzzySet(points=make_points(0, 50, 100), term="ciepło")
    S3 = FuzzySet(points=make_points(50, 100, 150), term="gorąco")
    FS.add_linguistic_variable("różnica_temperatury", LinguisticVariable([S1, S2, S3]))

    # Błąd całkowity (wejście)
    I1 = FuzzySet(points=make_points(-500, -250, 0), term="niski")
    I2 = FuzzySet(points=make_points(-250, 0, 250), term="średni")
    I3 = FuzzySet(points=make_points(0, 250, 500), term="wysoki")
    FS.add_linguistic_variable("błąd_całkowity", LinguisticVariable([I1, I2, I3]))

    # Moc grzałki (wyjście)
    P1 = FuzzySet(points=make_points(0, 0.5, 1.0), term="niska")
    P2 = FuzzySet(points=make_points(0.5, 1.5, 2.0), term="średnia")
    P3 = FuzzySet(points=make_points(1.5, 2.5, 3.0), term="wysoka")
    FS.add_linguistic_variable("moc_grzałki", LinguisticVariable([P1, P2, P3]))

    # Reguły logiki rozmytej
    rules = [
        "IF (różnica_temperatury IS zimno) AND (błąd_całkowity IS niski) THEN (moc_grzałki IS wysoka)",
        "IF (różnica_temperatury IS zimno) AND (błąd_całkowity IS średni) THEN (moc_grzałki IS średnia)",
        "IF (różnica_temperatury IS zimno) AND (błąd_całkowity IS wysoki) THEN (moc_grzałki IS średnia)",
        "IF (różnica_temperatury IS ciepło) AND (błąd_całkowity IS średni) THEN (moc_grzałki IS średnia)",
        "IF (różnica_temperatury IS gorąco) AND (błąd_całkowity IS wysoki) THEN (moc_grzałki IS niska)"
    ]
    FS.add_rules(rules)

    return FS




# Symulacja piekarnika


def simulate_oven(FS, T_otoczenia, T_docelowa, T_start, P_max, k, c, m, delta_t, sim_time):
    times = []
    temperatures = []
    T = T_start
    integral_error = 0  # Początkowy błąd całkowity

    for t in range(0, sim_time, delta_t):
        # Obliczanie różnicy temperatury
        delta_T = T_docelowa - T

        # Aktualizacja błędu całkowitego
        integral_error += delta_T * delta_t

        # Ustawienie wejść do systemu rozmytego
        FS.set_variable("różnica_temperatury", delta_T)
        FS.set_variable("błąd_całkowity", integral_error)

        # Obliczenie mocy grzałki
        moc = FS.inference()["moc_grzałki"] * P_max

        # Bilans cieplny
        Q_dostarczone = moc * delta_t
        Q_utracone = k * (T - T_otoczenia) * delta_t
        delta_Q = Q_dostarczone - Q_utracone
        delta_T_sim = delta_Q / (m * c)

        # Aktualizacja temperatury
        T += delta_T_sim
        print(T)

    return times, temperatures


# Parametry fizyczne i symulacji
T_otoczenia = 20  # Temperatura otoczenia (°C)
T_docelowa = 200  # Docelowa temperatura piekarnika (°C)
T_start = 20  # Początkowa temperatura piekarnika (°C)
P_max = 2  # Maksymalna moc grzałki (kW)
k = 0.006  # Współczynnik strat cieplnych (kW/°C)
c = 1.2  # Pojemność cieplna powietrza (kJ/(kg·°C))
m = 50 / 1000 * 1.2  # Masa powietrza (kg)
delta_t = 1  # Krok czasowy (s)
sim_time = 2000  # Czas symulacji (s)

# Tworzenie regulatora Fuzzy PI
FS = create_fuzzy_pi()

# Uruchomienie symulacji
times, temperatures = simulate_oven(
    FS, T_otoczenia, T_docelowa, T_start, P_max, k, c, m, delta_t, sim_time)

# Wizualizacja wyników
plt.figure(figsize=(10, 6))
plt.plot(times, temperatures, label="Temperatura piekarnika", linewidth=2)
plt.axhline(y=T_docelowa, color='r', linestyle='--',
            label="Temperatura docelowa (200°C)")
plt.xlabel("Czas (s)")
plt.ylabel("Temperatura (°C)")
plt.title("Symulacja piekarnika z rozmytym regulatorem PI")
plt.legend()
plt.grid()
plt.show()
