import os, sys, asyncio
sys.path.append("/usr/lib")
import _kipr as k  # Importiere _kipr wie im Beispielcode

LEFT = 0   # Top-left wheel in image
RIGHT = 1  # Top-right wheel in image
Greifer = 1
Hebel = 0

async def main():
    print("Starte Messung des Analogsensors 0 für 20 Sekunden...")
    k.enable_servos()
    k.set_servo_position(Greifer, 1900)
    k.set_servo_position(Hebel, 0)
    
    await GoonStreak()
    
    try:
        VL = k.analog(0)
        VR = k.analog(1) 
        HL = k.analog(2) 
        HR = k.analog(3)
    except KeyboardInterrupt:
        print("Programm durch Benutzer unterbrochen")
    finally:
        print("Messung beendet.")

async def Stop():
    k.motor(LEFT, 0)
    k.motor(RIGHT, 0)
    
async def Vor(duration):
    k.motor(LEFT, 80)
    k.motor(RIGHT, 80)
    await asyncio.sleep(duration)
    k.motor(LEFT, 0)
    k.motor(RIGHT, 0)
    
async def Vor2(duration):
    for i in range(4):
        k.motor(i, 80)
    await asyncio.sleep(duration)
    for i in range(4):
        k.motor(i, 0)
    
async def Hinten2(duration):
    for i in range(4):
        k.motor(i, -80)
    await asyncio.sleep(duration)
    for i in range(4):
        k.motor(i, 0)
    
async def LinksUm():
    k.motor(LEFT, -80)
    k.motor(RIGHT, 80)
    await asyncio.sleep(0.98)
    await Stop()
    
async def RechtsUm():
    k.motor(LEFT, 80)
    k.motor(RIGHT, -80)
    await asyncio.sleep(0.98)
    await Stop()
    
async def GRRR():
    k.motor(LEFT, 80)
    k.motor(RIGHT, -80)
    await asyncio.sleep(3)
    await Stop()
    
def Read():
    return k.analog(0), k.analog(1), k.analog(2), k.analog(3)
    
def GreiferZu():
    k.set_servo_position(Greifer, 2047)
    
def GreiferAuf():
    k.set_servo_position(Greifer, 1000)
    
def HebelRauf(stufe):
    pos = {0: 0, 1: 1370, 2: 1600, 3: 1780, 4: 2047}.get(stufe, 0)
    k.set_servo_position(Hebel, pos)
    
async def Goon(stufe):
    await asyncio.sleep(0.3)
    HebelRauf(stufe)
    await asyncio.sleep(1)
    GreiferAuf()
    await asyncio.sleep(0.3)
    HebelRauf(0)
    
async def GoonStreak():
    GreiferZu()
    await asyncio.sleep(1)
    await Hinten2(1)
    await asyncio.sleep(1)
    await Goon(4)
    await asyncio.sleep(2)
    GreiferAuf()
    await Vor2(1)
    await asyncio.sleep(1)
    GreiferZu()
    await asyncio.sleep(1)
    await Hinten2(1)
    await asyncio.sleep(1)
    await Goon(3)
    await asyncio.sleep(2)
    GreiferAuf()
    await Vor2(1)
    await asyncio.sleep(1)
    GreiferZu()
    await asyncio.sleep(1)
    await Hinten2(1)
    await asyncio.sleep(1)
    await Goon(2)
    await asyncio.sleep(2)
    GreiferAuf()
    await Vor2(1)
    await asyncio.sleep(1)
    GreiferZu()
    await asyncio.sleep(1)
    await Hinten2(1)
    await asyncio.sleep(1)
    await Goon(1)
    await asyncio.sleep(2)
    GreiferAuf()
    await Vor2(1)
    await asyncio.sleep(1)
    
async def Stroke(stufe):
    HebelRauf(stufe)
    await asyncio.sleep(1)
    GreiferZu()
    await asyncio.sleep(1)
    HebelRauf(0)
    await asyncio.sleep(2)
    GreiferAuf()
    await asyncio.sleep(1)
    
if __name__ == "__main__":
    asyncio.run(main())

