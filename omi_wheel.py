#!/usr/bin/python3
import os, sys, time
sys.path.append("/usr/lib")
import _kipr as k  # Importiere _kipr wie im Beispielcode
FRONT_LEFT = 0   # Top-left wheel in image
FRONT_RIGHT = 1  # Top-right wheel in image
REAR_LEFT = 2    # Bottom-left wheel in image
REAR_RIGHT = 3   # Bottom-right wheel in image
def main():
    print("Starte Messung des Analogsensors 0 fC<r 20 Sekunden...")
    
    # Startzeit speichern
    start_time = time.time()
    end_time = start_time + 5  # 20 Sekunden laufen lassen
    
    try:
        # Messung fC<r 20 Sekunden durchfC<hren
        while time.time() < end_time:
              time.sleep(0.1)
                #Hier Ware hinein
                      

    except KeyboardInterrupt:
        print("Programm durch Benutzer unterbrochen")
    finally:
        print("Messung beendet.")
def GoRight():
    k.motor(FRONT_LEFT, -80)
    k.motor(FRONT_RIGHT, 80)
    k.motor(REAR_LEFT, 80)
    k.motor(REAR_RIGHT, -80)

def GoRightUp():
    k.motor(FRONT_LEFT, 0)
    k.motor(FRONT_RIGHT, 80)
    k.motor(REAR_LEFT, 80)
    k.motor(REAR_RIGHT, 0)
def GoLeftUp():
    k.motor(FRONT_LEFT, 80)
    k.motor(FRONT_RIGHT, 0)
    k.motor(REAR_LEFT, 0)
    k.motor(REAR_RIGHT, 80)
def GoRightBack():
    k.motor(FRONT_LEFT, -80)
    k.motor(FRONT_RIGHT, 0)
    k.motor(REAR_LEFT, 0)
    k.motor(REAR_RIGHT, -80)
def GoLeftBack():
    k.motor(FRONT_LEFT, 0)
    k.motor(FRONT_RIGHT, -80)
    k.motor(REAR_LEFT, -80)
    k.motor(REAR_RIGHT, 0)
def Vor():
    k.motor(FRONT_LEFT, 80)
    k.motor(FRONT_RIGHT, 80)
    k.motor(REAR_LEFT, 80)
    k.motor(REAR_RIGHT, 80)
def LinksUm():
    k.motor(FRONT_LEFT, -80)
    k.motor(FRONT_RIGHT, 80)
    k.motor(REAR_LEFT, -80)
    k.motor(REAR_RIGHT, 80)
def RechtsUm():
    k.motor(FRONT_LEFT, 80)
    k.motor(FRONT_RIGHT,-80)
    k.motor(REAR_LEFT, 80)
    k.motor(REAR_RIGHT, -80)

    

if __name__ == "__main__":
    main()