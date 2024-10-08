import subprocess
import platform
import time
import datetime
import matplotlib
matplotlib.use('Agg')  # Użycie nieinteraktywnego backendu
import matplotlib.pyplot as plt
import socket
import os

# Listy do przechowywania danych
czas = []
sila_sygnalu = []
status_internetu = []

# Flaga do kontrolowania generowania raportu raz dziennie

dzisiejsza_data = datetime.date.today()

def get_wifi_signal_windows():
    result = subprocess.run(["netsh", "wlan", "show", "interfaces"], capture_output=True, text=True)
    output = result.stdout
    for line in output.split('\n'):
        if "Signal" in line:
            signal_line = line.strip()
            signal_strength = int(signal_line.split(":")[1].strip().replace('%', ''))
            return signal_strength
    return None

def get_wifi_signal_linux():
    result = subprocess.run(["iwconfig"], capture_output=True, text=True)
    output = result.stdout
    for line in output.split('\n'):
        if "Link Quality" in line:
            signal_line = line.strip()
            parts = signal_line.split('  ')
            for part in parts:
                if "Link Quality" in part:
                    quality = part.split('=')[1].split('/')
                    signal_strength = int(int(quality[0]) / int(quality[1]) * 100)
                    return signal_strength
    return None

def get_wifi_signal():
    system = platform.system()
    if system == "Windows":
        return get_wifi_signal_windows()
    elif system == "Linux":
        return get_wifi_signal_linux()
    else:
        print("Nieobsługiwany system operacyjny")
        return None

def check_internet():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return 100
    except OSError:
        return 0

def main():
    global dzisiejsza_data
    
    while True:
        try:
            teraz = datetime.datetime.now()
            sygnal = get_wifi_signal()
            internet = check_internet()
            
            czas.append(teraz)
            sila_sygnalu.append(sygnal)
            status_internetu.append(internet)
            
            # Sprawdź, czy jest godzina 19 i czy raport nie został już wygenerowany dzisiaj
            if teraz.hour in (1, 5, 9, 13,17, 21)  and teraz.minute == 00 :
                # Generuj wykres
                
                plt.figure(figsize=(10,5))
                plt.plot(czas, sila_sygnalu, label='Siła sygnału WiFi')
                plt.plot(czas, status_internetu, label='WiFi')
                plt.xlabel('Czas')
                plt.ylabel('Siła sygnału (%)')
                plt.title('Jakość sygnału WiFi')
                plt.legend()
                plt.grid(True)
                plt.tight_layout()
                
                # Sprawdź, czy katalog 'raporty' istnieje, jeśli nie, utwórz go
                if not os.path.exists('raporty'):
                    os.makedirs('raporty')
                
                # Zapisz wykres do pliku PDF
                nazwa_pliku = 'raporty/raport_wifi_{}.pdf'.format(teraz.strftime('%Y%m%d%H'))
                plt.savefig(nazwa_pliku)
                plt.close()
                
                print(f'Raport wygenerowany: {nazwa_pliku}')
                
                # Ustaw flagę, że raport został wygenerowany
                
                
                # Wyczyść dane na następny dzień
                czas.clear()
                sila_sygnalu.clear()
                status_internetu.clear() 
                time.sleep(60)
                
            elif teraz.date() != dzisiejsza_data:
                # Nowy dzień, zresetuj flagę i datę
                dzisiejsza_data = teraz.date()
            
            # Czekaj jedną minutę
            time.sleep(10)
        except Exception as e:
            print(f'Wystąpił błąd: {e}')
            time.sleep(10)

if __name__ == "__main__":
    main()