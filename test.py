print("Starte Messung des Analogsensors 0 fC<r 20 Sekunden...")
    
    # Startzeit speichern
    # 20 Sekunden laufen lassen
    #if sensor_wert0 > 3900:
             #  print("0",end='')
    try:
        # Messung fC<r 20 Sekunden durchfC<hren
        VL = k.analog(0)
        VR = k.analog(1) 
        HL = k.analog(2) 
        HR = k.analog(3)

        
        while VL < 3900 OR VR < 3900:
            # Lesen des Analogsensors 0
            VL = k.analog(0)
            VR = k.analog(1) 
            HL = k.analog(2) 
            HR = k.analog(3) 
            Vor()
            time.sleep(0.1)
        RechtsUm()
        Vor(6)
        while VL < 3900 OR VR < 3900:
            # Lesen des Analogsensors 0
            VL = k.analog(0)
            VR = k.analog(1) 
            HL = k.analog(2) 
            HR = k.analog(3) 
            Vor()
            time.sleep(0.1)
        Back(1)
        LinksUm()
        Vor(2)
        

        
      
          
    except KeyboardInterrupt:
        print("Programm durch Benutzer unterbrochen")
    finally:
        print("Messung beendet.")


def Stop():
   k.motor(LEFT, 0)
   k.motor(RIGHT, 0)
def Vor():
   k.motor(LEFT, 80)
   k.motor(RIGHT, 80)  
def Vor(duration):
    start_time = time.time()
    end_time = start_time + duration
    while time.time() < end_time:
        k.motor(LEFT, 80)
        k.motor(RIGHT, 80)
def Back():
   k.motor(LEFT, -80)
   k.motor(RIGHT, -80)  
def Back(duration):
    start_time = time.time()
    end_time = start_time + duration
    while time.time() < end_time:
        k.motor(LEFT, -80)
        k.motor(RIGHT, -80)
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
    

if __name__ == "__main__":
    main()
    

if __name__ == "__main__":
    main()