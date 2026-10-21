import threading
import time
import cv2
import battery

from djitellopy import Tello

# Globale Variablen
counter = 0 # Zähler für Versuche, ein Mission Pad zu finden
found = 0 # Zähler für gefundene Mission Pads
pad_ids = [] # Liste der bereits gefundenen Mission Pad IDs
lock = threading.Lock() # Lock für Thread-Synchronisation
running = True # Flag, um Threads sauber zu stoppen

# Initialisierung der Drohne
tello = Tello()
tello.connect()

# Batterie prüfen
battery.getBatteryValue(tello)

# Einstellungen für Mission Pads
tello.enable_mission_pads()
tello.set_mission_pad_detection_direction(0)  # 0 = downward, 1 = forward, 2 = both


# Funktion zur Interaktion mit gefundenen Mission Pads
def find_mission_pad():
    global counter, found, running

    while running and counter < 10 and found < 2:
        with lock:
            pad_id = tello.get_mission_pad_id()
        
        print(f"pad_id: {pad_id}")

        if pad_id != -1 and pad_id not in pad_ids:
            on_pad_found(pad_id)
        else:
            with lock:
                tello.move_forward(30)
                counter += 1
                print(f"Versuch {counter}")
        
        # Kurze Pause, um das Netzwerk/die Drohne nicht zu überlasten
        time.sleep(0.5)


# Funktion, wenn ein Pad gefunden wurde
def on_pad_found(pad_id):
    global found, running

    x = tello.get_mission_pad_distance_x()
    y = tello.get_mission_pad_distance_y()
    z = tello.get_mission_pad_distance_z()
    
    tello.go_xyz_speed_mid(x, y, z, 10, pad_id)
    tello.land()

    if found < 2:
        found += 1
        time.sleep(5)
        tello.takeoff()
        with lock:
            pad_ids.append(pad_id)
    else:
        running = False


# Hauptprogramm
try:
    # Videostream starten
    tello.streamon()
    tello.set_video_direction(0)  # 0 = untere Kamera
    
    frame_read = tello.get_frame_read()
    
    # Drohne starten
    tello.takeoff()

    # Hintergrund-Thread für die Mission-Pad-Suche starten
    t2 = threading.Thread(target=find_mission_pad)
    t2.start()

    print("Videostream läuft. Drücke 'q' im Videofenster, um das Programm zu beenden.")

    while running:
        img = frame_read.frame

        if img is not None:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, (960, 720))
            cv2.imshow("Tello - Untere Kamera", img)

        # Abbruch über Taste 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            running = False
            break

        # Kleine Pause für die GUI-Schleife
        time.sleep(0.01)

    # Warten, bis der Mission-Pad-Thread sich beendet
    t2.join(timeout=2.0)

except Exception as e:
    print(f"Ein Fehler ist aufgetreten: {e}")

finally:
    # Shutdown: Drohne landen, Stream stoppen, Verbindung trennen
    print("Programm wird beendet. Räume auf...")
    running = False
    try:
        tello.land()
    except:
        pass
    try:
        tello.streamoff()
    except:
        pass
    cv2.destroyAllWindows()
    tello.end()
    print("Verbindung zur Drohne getrennt.")