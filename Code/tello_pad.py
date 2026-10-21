import threading
import time
import cv2
import battery

from djitellopy import Tello

#global variables
counter = 0 #counter to limit the number of attempts to find a mission pad
found = 0 #counter for found mission pads
pad_ids = [] #list of found mission pad ids

tello = Tello()
tello.connect()

battery.getBatteryValue(tello) #checks battery value before flight and exits if battery is too low

#settings for the tello drone
tello.enable_mission_pads()
tello.set_mission_pad_detection_direction(0) # 0 = downward, 1 = forward, 2 = both

tello.takeoff()

# height = tello.get_height()
# print(f"Height: {height} cm")

# tello.move_down(30)

def videoRecorder():
    # 1. Videostream einschalten
    tello.streamon()

    # 2. Auf die untere Kamera umschalten
    # 0 = untere Kamera, 1 = Vorwärtskamera 
    tello.set_video_direction(0)

    # Frame-Reader starten, um die Bilder abzugreifen
    frame_read = tello.get_frame_read()

    print("Videostream läuft. Drücke 'q' im Videofenster, um das Programm zu beenden.")

    while True:
        # Aktuelles Bild von der Kamera holen
        img = frame_read.frame
            
        # Falls das Bild geladen wurde, anzeigen
        if img is not None:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) # Color conversion from BGR to RGB
            img = cv2.resize(img, (960, 720)) # Resize the image to 960x720
            cv2.imshow("Tello - Untere Kamera", img)
            
        # Abbruch, wenn die Taste 'q' gedrückt wird
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

#function to find mission pads
def find_mission_pad():

    global counter, found

    while counter < 10 and found < 2:

        pad_id = tello.get_mission_pad_id()
        print(f"pad_id: {pad_id}")

        if pad_id != -1 and pad_id not in pad_ids:
            on_pad_found(pad_id)

        else :
            tello.move_forward(30)
            counter += 1
            print(counter)

#function for interaction with found mission pads
def on_pad_found(pad_id):

    global found

    x = tello.get_mission_pad_distance_x()
    y = tello.get_mission_pad_distance_y()
    z = tello.get_mission_pad_distance_z()
    
    tello.go_xyz_speed(x, y, z, 10)
    
    tello.land()

    if found < 2:
        found += 1

        time.sleep(5)
        tello.takeoff()
        pad_ids.append(pad_id) #adds found mission pad to the list

    else:
        tello.end()

t1 = threading.Thread(target=videoRecorder)
t2 = threading.Thread(target=find_mission_pad)

t1.start()
t2.start()