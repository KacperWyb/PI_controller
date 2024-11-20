import matplotlib.pyplot as plt

# Parametry piekarnika
T_ambient = 20.0  # temperatura otoczenia w stopniach Celsjusza
thermal_mass = 100.0  # bezwładność cieplna piekarnika
efficiency = 1.5  # efektywność grzałki

# Parametry regulatora PI
K_p = 2.0  # wzmocnienie proporcjonalne
K_i = 0.1  # wzmocnienie całkujące

# Parametry symulacji
setpoint = 180.0  # temperatura zadana w stopniach Celsjusza
T_current = T_ambient  # początkowa temperatura piekarnika
heating_power = 0.0  # początkowa moc grzania
h_Min = T_ambient
h_Max = 400
integral_error = 0.0  # początkowy błąd całkowy
time_step = 1  # krok czasowy w sekundach
simulation_time = 1000  # całkowity czas symulacji w sekundach

# Zapis wyników do wykresu
time_history = []
temperature_history = []
heating_power_history = []

# Pętla symulacji
for t in range(simulation_time):
    # Oblicz błąd
    error = setpoint - T_current

    # Aktualizuj błąd całkujący
    integral_error += error * time_step

    # Wyjście regulatora PI
    heating_power = K_p * error + K_i * integral_error
    heating_power = max(0, min(100, heating_power)
                        )  # Ogranicz moc grzania do 0-100%

    # Aktualizacja temperatury piekarnika
    T_current += (min(max(heating_power * h_Max, h_Min), h_Max) * efficiency -
                  (T_current - T_ambient)) / thermal_mass * time_step

    # Zapis wyników do analizy
    time_history.append(t)
    temperature_history.append(T_current)
    heating_power_history.append(heating_power)

# Wykres temperatury i mocy grzania
plt.figure(figsize=(12, 6))

# Temperatura
plt.subplot(2, 1, 1)
plt.plot(time_history, temperature_history, label='Temperature')
plt.axhline(y=setpoint, color='r', linestyle='--', label='Setpoint')
plt.xlabel('Time (s)')
plt.ylabel('Temperature (°C)')
plt.title('Temperature Control of Oven')
plt.legend()

# Moc grzania
plt.subplot(2, 1, 2)
plt.plot(time_history, heating_power_history, label='Heating Power (%)')
plt.xlabel('Time (s)')
plt.ylabel('Heating Power (%)')
plt.legend()

plt.tight_layout()
plt.show()