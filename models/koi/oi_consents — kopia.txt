import pandas as pd

# Wczytaj dane z pliku
with open('twoj_plik.txt', 'r') as file:
    lines = file.readlines()

# Inicjalizacja pustych list
pesel_list = []
numer_wygrany_list = []

# Przetwarzanie każdej linii
for line in lines:
    # Podziel linię na części, używając znaku '|'
    parts = line.strip().split('|')

    # Pierwszy element to pesel, drugi to lista numerów wygranych
    pesel = parts[0]
    numer_wygrany = eval(parts[1])[0] if len(eval(parts[1])) > 0 else None  # Wyłuskaj pierwszy numer z listy

    # Dodaj do list
    pesel_list.append(pesel)
    numer_wygrany_list.append(numer_wygrany)

# Stwórz DataFrame
df = pd.DataFrame({'pesel': pesel_list, 'numer_wygrany': numer_wygrany_list})

# Wyświetl DataFrame
print(df)
