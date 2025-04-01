#!/usr/bin/python3
import os, sys, time
sys.path.append("/usr/lib")
import _kipr as k  # Importiere _kipr wie im Beispielcode
LEFT = 0   # Top-left wheel in image
RIGHT = 1  # Top-right wheel in image
Greifer = 1
Hebel = 0
def main():
    print("Starte Messung des Analogsensors 0 fC<r 20 Sekunden...")
    k.enable_servos()
    k.set_servo_position(Greifer, 1900)
    k.set_servo_position(Hebel, 0)
    
    GoonStreak()

    
    # Startzeit speichern
    # 20 Sekunden laufen lassen
    
    try:
        # Messung fuer 20 Sekunden durchfC<hren
        VL = k.analog(0)
        VR = k.analog(1) 
        HL = k.analog(2) 
        HR = k.analog(3)

        """print(VL,VR,HL,HR)
        while (k.analog(0) < 3900) & (k.analog(1) < 3900):
            print("Pr")
            Vor()
            time.sleep(0.1)
        RechtsUm()
        Counter = 0
        while (k.analog(0) < 3900) & (k.analog(1) < 3900) & (Counter <= 2):
            VL = k.analog(0)
            VR = k.analog(1) 
            HL = k.analog(2) 
            HR = k.analog(3)
            if VL < 3900 & VR < 3900:
                Counter += 1
                time.sleep(2)
            Vor()
            time.sleep(0.1)
        LinksUm()
        Vor(3)"""
        
            
        #Hebelteil 0 wenn unten 2047 wenn oben
        #Greifer 1000 Offen 2047 Zu, Drink zu 1900, Drink auf 1500, Becher zu 1600, Becher Offen 1200
                
        
    except KeyboardInterrupt:
        print("Programm durch Benutzer unterbrochen")
    finally:
        print("Messung beendet.")


def Stop():
   k.motor(LEFT, 0)
   k.motor(RIGHT, 0) 
def Vor(duration):
    start_time = time.time()
    end_time = start_time + duration
    while time.time() < end_time:
        k.motor(LEFT, 80)
        k.motor(RIGHT, 80)
def Vor2(duration):
    start_time = time.time()
    end_time = start_time + duration
    while time.time() < end_time:
        k.motor(1, 80)
        k.motor(2, 80)
        k.motor(3, 80)
        k.motor(0, 80)
    k.motor(1, 0)
    k.motor(2, 0)
    k.motor(3, 0)
    k.motor(0, 0)
def Hinten2(duration):
    start_time = time.time()
    end_time = start_time + duration
    while time.time() < end_time:
        k.motor(1, -80)
        k.motor(2, -80)
        k.motor(3, -80)
        k.motor(0, -80)
    k.motor(1, 0)
    k.motor(2, 0)
    k.motor(3, 0)
    k.motor(0, 0)
def Vor():
    k.motor(LEFT, 80)
    k.motor(RIGHT, 80)
def LinksUm():
    start_time = time.time()
    end_time = start_time + 0.98
    while time.time() < end_time:
    	k.motor(LEFT, -80)
    	k.motor(RIGHT, 80)
    k.motor(RIGHT, 0)
    k.motor(LEFT, 0)
def RechtsUm():
    start_time = time.time()
    end_time = start_time + 0.98
    while time.time() < end_time:
    	k.motor(LEFT, 80)
    	k.motor(RIGHT, -80)
    k.motor(RIGHT, 0)
    k.motor(LEFT, 0)
def GRRR():
    start_time = time.time()
    end_time = start_time + 3
    while time.time() < end_time:
    	k.motor(LEFT, 80)
    	k.motor(RIGHT, -80)
    k.motor(RIGHT, 0)
    k.motor(LEFT, 0)
def Read():
    VL = k.analog(0)
    VR = k.analog(1) 
    HL = k.analog(2) 
    HR = k.analog(3)
def GreiferZu():
    k.set_servo_position(Greifer, 2047)
def GreiferZuBecher():
    k.set_servo_position(Greifer, 1600)
def GreiferZuDrink():
    k.set_servo_position(Greifer, 2047)
def GreiferAuf():
    k.set_servo_position(Greifer, 1000)
def GreiferAufBecher():
    k.set_servo_position(Greifer, 1200)
def GreiferAufDrink():
    k.set_servo_position(Greifer, 1500)
def HebelRauf(stufe):
    if stufe == 0:
        k.set_servo_position(Hebel, 0)
    if stufe == 4:
        k.set_servo_position(Hebel, 2047)
    if stufe == 3:
        k.set_servo_position(Hebel, 1780)
    if stufe == 2:
        k.set_servo_position(Hebel, 1600)
    if stufe == 1:
        k.set_servo_position(Hebel, 1370)
        
def Goon(stufe):
    time.sleep(0.3)
    HebelRauf(stufe)
    time.sleep(1)
    GreiferAufDrink()
    time.sleep(0.3)
    HebelRauf(0)
def GoonStreak():
    GreiferZuDrink()
    time.sleep(1)
    Hinten2(1)
    time.sleep(1)
    Goon(4)
    time.sleep(2)
    GreiferAuf()
    Vor2(1)
    time.sleep(1)
    GreiferZuDrink()
    time.sleep(1)
    time.sleep(0.3)
    Hinten2(1)
    time.sleep(1)
    Goon(3)
    time.sleep(2)
    GreiferAuf()
    Vor2(1)
    time.sleep(1)
    GreiferZuDrink()
    time.sleep(1)
    time.sleep(0.3)
    Hinten2(1)
    time.sleep(1)
    Goon(2)
    time.sleep(2)
    GreiferAuf()
    Vor2(1)
    time.sleep(1)
    GreiferZuDrink()
    time.sleep(1)
    Hinten2(1)
    time.sleep(1)
    Goon(1)
    time.sleep(2)
    GreiferAuf()
    Vor2(1)
    time.sleep(1)
def Stroke(stufe):
    HebelRauf(stufe)
    time.sleep(1)
    GreiferZuDrink()
    time.sleep(1)
    HebelRauf(0)
    time.sleep(2)
    GreiferAuf()
    time.sleep(1)   
#Hebelteil 0 wenn unten 2047 wenn oben
        #Greifer 1000 Offen 2047 Zu, Drink zu 1900, Drink auf 1500, Becher zu 1600, Becher Offen 1200
    

if __name__ == "__main__":
    main()
    
