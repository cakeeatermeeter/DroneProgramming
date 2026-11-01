import threading
import time
import cv2
import main.tello_battery as tello_battery

from djitellopy import Tello

# Globale Variablen
lock = threading.Lock() # Lock für Thread-Synchronisation
running = True # Flag, um Threads sauber zu stoppen

# Initialisierung der Drohne
tello = Tello()
tello.connect()

# Batterie prüfen
tello_battery.getBatteryValue(tello)

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