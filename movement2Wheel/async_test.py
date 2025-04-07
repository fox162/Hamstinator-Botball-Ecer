#!/usr/bin/python3
import os, sys, time, asyncio
sys.path.append("/usr/lib")
import _kipr as k
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import Goon.src.main as goon

LEFT = 0   # Top-left wheel in image
RIGHT = 1  # Top-right wheel in image
line_startr = 0
line_blackr = 3900
line_startl = 0
line_blackl = 3900
VL = k.analog(0)
VR = k.analog(1)
HL = k.analog(2)
HR = k.analog(3)

LEFT = 0   # Top-left wheel in image
RIGHT = 1  # Top-right wheel in image
Greifer = 1
Hebel = 0

LEFT = 0   # Top-left wheel in image
RIGHT = 1  # Top-right wheel in image
Greifer = 1
Hebel = 0
EisG = 3
EisS = 2

#me loves u mel

async def eis_off():
    await asyncio.to_thread(k.set_servo_position, 2, 1132)
    await asyncio.to_thread(k.set_servo_position, 3, 1300)

async def eis_open():
    await asyncio.to_thread(k.set_servo_position, 3, 1300)

async def eis_close():
    await asyncio.to_thread(k.set_servo_position, 3, 900)
    await asyncio.sleep(0.001)
    await asyncio.to_thread(k.set_servo_position, 3, 820)
    await asyncio.sleep(0.001)
    await asyncio.to_thread(k.set_servo_position, 3, 720)
    await asyncio.sleep(0.001)
    await asyncio.to_thread(k.set_servo_position, 3, 620)
    await asyncio.sleep(0.001)
    await asyncio.to_thread(k.set_servo_position, 3, 520)
    await asyncio.sleep(0.001)
    await asyncio.to_thread(k.set_servo_position, 3, 420)
    await asyncio.sleep(0.001)
    await asyncio.to_thread(k.set_servo_position, 3, 320)
    await asyncio.sleep(0.001)
    await asyncio.to_thread(k.set_servo_position, 3, 220)
    await asyncio.sleep(0.001)
    await asyncio.to_thread(k.set_servo_position, 3, 120)
    await asyncio.sleep(0.001)
    await asyncio.to_thread(k.set_servo_position, 3, 20)
    await asyncio.sleep(0.001)
    await asyncio.to_thread(k.set_servo_position, 3, 5)
    
async def eis_hang_down():
    await asyncio.to_thread(k.set_servo_position, 2, 1920)
    
async def eis_hang_up():
    await asyncio.to_thread(k.set_servo_position, 2, 1920)
    await asyncio.sleep(0.001)
    await asyncio.to_thread(k.set_servo_position, 2, 1180)
    await asyncio.sleep(0.001)
    await asyncio.to_thread(k.set_servo_position, 2, 1170)
    await asyncio.sleep(0.001)
    await asyncio.to_thread(k.set_servo_position, 2, 1160)
    await asyncio.sleep(0.001)
    await asyncio.to_thread(k.set_servo_position, 2, 1150)
    await asyncio.sleep(0.001)
    await asyncio.to_thread(k.set_servo_position, 2, 1140)
    await asyncio.sleep(0.001)
    await asyncio.to_thread(k.set_servo_position, 2, 1130)
    await asyncio.sleep(0.001)
    await asyncio.to_thread(k.set_servo_position, 2, 1120)
    await asyncio.sleep(0.001)
    await asyncio.to_thread(k.set_servo_position, 2, 1110)
    await asyncio.sleep(0.001)
    await asyncio.to_thread(k.set_servo_position, 2, 1090)
    await asyncio.sleep(0.001)
    await asyncio.to_thread(k.set_servo_position, 2, 1080)
    await asyncio.sleep(0.001)
    await asyncio.to_thread(k.set_servo_position, 2, 1070)
    await asyncio.sleep(0.001)
    await asyncio.to_thread(k.set_servo_position, 2, 1060)
    await asyncio.sleep(0.001)
    await asyncio.to_thread(k.set_servo_position, 2, 1050)
    
    
    
    
    
async def eis_grab():
    await eis_open()
    await asyncio.sleep(0.2)
    await eis_hang_down()
    await asyncio.sleep(0.5)
    await eis_close()
    await asyncio.sleep(0.6)
    await eis_hang_up()
    
async def Stop():
    await asyncio.to_thread(k.motor, LEFT, 0)
    await asyncio.to_thread(k.motor, RIGHT, 0)


async def Vor(duration):
    await asyncio.to_thread(k.motor, LEFT, 80)
    await asyncio.to_thread(k.motor, RIGHT, 80)
    await asyncio.sleep(duration)
    await Stop()

async def backl(duration):
    await asyncio.to_thread(k.motor, LEFT, -200)
    await asyncio.to_thread(k.motor, RIGHT, -200)
    await asyncio.sleep(duration)
    await Stop()
    
async def Vor2(duration):
    for i in range(4):
        await asyncio.to_thread(k.motor, i, 80)
    await asyncio.sleep(duration)
    for i in range(4):
        await asyncio.to_thread(k.motor, i, 0)


async def Hinten2(duration):
    for i in range(4):
        await asyncio.to_thread(k.motor, i, -80)
    await asyncio.sleep(duration)
    for i in range(4):
        await asyncio.to_thread(k.motor, i, 0)


async def GreiferZu():
    await asyncio.to_thread(k.set_servo_position, Greifer, 2047)


async def GreiferAuf():
    await asyncio.to_thread(k.set_servo_position, Greifer, 1300)


async def HebelRauf(stufe):
    pos = {0: 0, 1: 1370, 2: 1600, 3: 1780, 4: 2047}.get(stufe, 0)
    k.set_servo_position(Hebel, pos)


async def Goon(stufe):
    await asyncio.sleep(0.3)
    await HebelRauf(stufe)
    await asyncio.sleep(0.7)
    print("here?")
    await GreiferAuf()
    print("or here?")
    await asyncio.sleep(0.3)
    await HebelRauf(0)

    
async def HebelUp(pos):
    await asyncio.to_thread(k.set_servo_position, Hebel, pos)


async def GoonStreak():
    print("1")
    await GreiferZu()
    await HebelUp(70)
    await asyncio.sleep(0.3)
    await backl(1)
    await asyncio.sleep(0.5)
    await Goon(4)
    print("2")
    await asyncio.sleep(0.5)
    await GreiferAuf()
    print("2.1")
    await Vor(0.6)
    await asyncio.sleep(0.3)
    await GreiferZu()
    await HebelUp(50)
    print("3")
    await asyncio.sleep(0.2)
    await backl(1)
    await asyncio.sleep(0.2)
    await Goon(3)
    await asyncio.sleep(0.5)
    await GreiferAuf()
    print("4")
    await Vor(1)
    await asyncio.sleep(0.6)
    await GreiferZu()
    await HebelUp(50)
    await asyncio.sleep(0.2)
    await backl(1)
    await asyncio.sleep(0.2)
    print("5")
    await Goon(2)
    await asyncio.sleep(0.5)
    await GreiferAuf()
    await Vor(1)
    await asyncio.sleep(0.6)
    print("6")
    await GreiferZu()
    await HebelUp(50)
    await asyncio.sleep(0.2)
    await backl(1)
    await asyncio.sleep(0.2)
    print("7")
    await Goon(1)
    await asyncio.sleep(0.5)
    await GreiferAuf()


async def Stroke(stufe):
    await GreiferAuf()
    await HebelRauf(stufe)
    await asyncio.sleep(1)
    await GreiferZu()
    await asyncio.sleep(1)
    await HebelRauf(0)
    await asyncio.sleep(2)
    await GreiferAuf()
    await asyncio.sleep(1)

        
async def mainD():
    vam = 0
    start_time = time.time()
    time_now = 0
    while vam < 2:
        while k.analog(0) < line_blackl and k.analog(1) < line_blackr:
            await vor()  # Call vor asynchronously
        time_now = time.time()
        if time_now >= start_time + 2.47:
            vam += 1
            print(vam)

async def end_when(z):
    t = time.time()
    while True:
        if time.time() >= t + z:
            sys.exit("Ende der Zeit erreicht")
        await asyncio.sleep(0.1)  # Non-blocking sleep to prevent blocking the event loop

async def stop():
    k.motor(0, 0)
    k.motor(1, 0)

async def back(time_duration):
    times = time.time()
    while time.time() < times + time_duration:
        k.motor(0, -200)
        k.motor(1, -200)
        await asyncio.sleep(0.1)  # Non-blocking sleep to prevent blocking

async def Vor(duration):
    start_time = time.time()
    end_time = start_time + duration
    while time.time() < end_time:
        k.motor(LEFT, 80)
        k.motor(RIGHT, 80)
        await asyncio.sleep(0.1)  # Non-blocking sleep to prevent blocking

async def LinksUm():
    print("left")
    start_time = time.time()
    end_time = start_time + 0.98
    while time.time() < end_time:
        k.motor(LEFT, -80)
        k.motor(RIGHT, 80)
    k.motor(RIGHT, 0)
    k.motor(LEFT, 0)
    await asyncio.sleep(0.1)  # Non-blocking sleep

async def RechtsUm():
    print("right")
    start_time = time.time()
    end_time = start_time + 0.98
    while time.time() < end_time:
        k.motor(LEFT, 80)
        k.motor(RIGHT, -80)
    k.motor(RIGHT, 0)
    k.motor(LEFT, 0)
    await asyncio.sleep(0.1)  # Non-blocking sleep

async def HalfRightUm():
    print("right")
    start_time = time.time()
    end_time = start_time + 0.45
    while time.time() < end_time:
        k.motor(LEFT, 80)
        k.motor(RIGHT, -80)
    k.motor(RIGHT, 0)
    k.motor(LEFT, 0)
    await asyncio.sleep(0.1)  # Non-blocking sleep
    
async def vor():
    k.motor(RIGHT, 80)
    k.motor(LEFT, 80)
    await asyncio.sleep(0.1)  # Non-blocking sleep

async def line_drive():
    VL = 0
    VR = 0
    HL = 0
    HR = 0
    rspeed = 200
    lspeed = 200
    while True:
        VL = k.analog(0)
        VR = k.analog(1)
        HL = k.analog(2)
        HR = k.analog(3)
        k.motor(1, 80)  # 1 = r
        k.motor(0, 80)  # 0 = l

        if VL >= line_blackl or VR >= line_blackr:
            if VL >= line_blackl:
                rspeed = 200
                lspeed = 50
                k.motor(1, rspeed)
                k.motor(0, lspeed)
            else:
                rspeed = 50
                lspeed = 200
                k.motor(0, lspeed)
                k.motor(1, rspeed)

        if VL >= line_blackl and VR >= line_blackr:
            break  # Break loop when both values exceed threshold

        await asyncio.sleep(0.1)  # Non-blocking sleep
        
        
async def line_drive_for(dur):
    VL = 0
    VR = 0
    HL = 0
    HR = 0
    rspeed = 200
    lspeed = 200
    t = time.time()
    while time.time() < t + dur:
        VL = k.analog(0)
        VR = k.analog(1)
        HL = k.analog(2)
        HR = k.analog(3)
        k.motor(1, 80)  # 1 = r
        k.motor(0, 80)  # 0 = l

        if VL >= line_blackl or VR >= line_blackr:
            if VL >= line_blackl:
                rspeed = 200
                lspeed = 50
                k.motor(1, rspeed)
                k.motor(0, lspeed)
            else:
                rspeed = 50
                lspeed = 200
                k.motor(0, lspeed)
                k.motor(1, rspeed)

        if VL >= line_blackl and VR >= line_blackr:
            break  # Break loop when both values exceed threshold

        await asyncio.sleep(0.1)  # Non-blocking sleep

async def drive_line_back():
    while k.analog(0) < line_blackl and k.analog(1) < line_blackr:
        k.motor(0, -80)
        k.motor(1, -80)
        await asyncio.sleep(0.1)  # Non-blocking sleep
    stop()

async def drive_till_line():
    print("line")
    while k.analog(0) < line_blackl and k.analog(1) < line_blackr:
        print(k.analog(0))
        print(k.analog(1))
        k.motor(0, 80)
        k.motor(1, 80)
        await asyncio.sleep(0.1)  # Non-blocking sleep
    stop()

async def line_cor(t):
    time_s = time.time()
    VL = 0
    VR = 0
    HL = 0
    HR = 0
    rspeed = 80
    lspeed = 80
    while time_s + t > time.time():
        VL = k.analog(0)
        VR = k.analog(1)
        HL = k.analog(2)
        HR = k.analog(3)
        k.motor(1, 10)  # 1 = r
        k.motor(0, 10)  # 0 = l

        if VL > line_blackl or VR > line_blackr:
            if VL > 3900:
                rspeed = 80
                lspeed = 10
                k.motor(1, rspeed)
                k.motor(0, lspeed)
            else:
                rspeed = 10
                lspeed = 80
                k.motor(0, lspeed)
                k.motor(1, rspeed)

        await asyncio.sleep(0.1)  # Non-blocking sleep

async def wait_for_light():
    z = k.analog(5)
    print("a")
    while True:
        z = k.analog(5)
        if z < 190:
            break
            sys.exit()
        await asyncio.sleep(0.1)  # Non-blocking sleep

async def drive_motor_for(duration, left_speed, right_speed):
    start_time = time.time()
    end_time = start_time + duration
    while time.time() < end_time:
        k.motor(LEFT, left_speed)
        k.motor(RIGHT, right_speed)
        await asyncio.sleep(0.1)  # Non-blocking sleep to prevent blocking
    #await stop()

async def main():
    await GreiferZu()
    await HebelRauf(4)
    print("main")
    line_startl = k.analog(0)
    line_blackl = 3900 #line_startl + 200
    line_startr = k.analog(1)
    line_blackr = 3900 #line_startr
    await drive_motor_for(1, -80, -80)  # Move backward for 1 second
    await drive_motor_for(0.2, 80, 80)  # Move forward for 0.2 seconds

    await RechtsUm()  # Turn right
    await drive_motor_for(0.5,-80,-80)
    await mainD()
    await drive_motor_for(0.5, 80, 80)
    await RechtsUm()  # Turn right again

    await HebelRauf(0)
    
    asyncio.sleep(1)
    
    await line_drive()  # Navigate along the line
    await drive_motor_for(1, 80, 80)   # Move forward for 1 second
    await line_drive()
    await HebelRauf(4)

    await drive_motor_for(0.5, -80, -80)  # Move backward for 0.5 seconds
    await LinksUm()   # Turn left

    await GreiferZu()
    await HebelRauf(3)
    
    
    await drive_motor_for(2, 80, 84)   # Move forward for 4 seconds
    await stop()
    await GreiferAuf()
    await asyncio.to_thread(k.set_servo_position, Hebel, 500)
    await asyncio.sleep(0.5)
    await drive_motor_for(0.3,80,80)
    await asyncio.sleep(0.5)
    await drive_motor_for(0.3,-80,-80)
    await stop()
    await asyncio.sleep(0.2)
    await HebelRauf(0)
    await asyncio.sleep(1)

    await GoonStreak()
    await HebelRauf(2)
    await GreiferZu()
    
    
    # drinks picked
    # next: eis
    
    
    await backl(1)

    await linskUm()
    await drive_motor_for(0.3,80,80)
    await stop()
    await eis_grab()
    
    await drive_motor_for(0.8,80,0)
    await Vor(0.5)
    await drive_motor_for(0.5,0,80)
    await drive_till_line()
   
    await eis_off()
    
    
    # eis picked
    # next: Cups
    
    
    
    await RechtsUm()
    await backl(0.5)
    await HebelRauf(0)
    await GreiferAuf()
    await Vor(0.3)
    await GreiferZu()
    await HalfRightUm()
    await GreiferAuf()
    
    await stroke(1)
    await stroke(2)
    await stroke(3)
    await stroke(4) 
    
    # drinks og
    # next: get blue drings
    
    await drive_line_back()
    await HalfRightUm()
    await line_drive()
    
    # pick drinks:
    
    await drive_motor_for(2, 80, 84)   # Move forward for 4 seconds
    await stop()
    await GreiferAuf()
    await asyncio.to_thread(k.set_servo_position, Hebel, 500)
    await asyncio.sleep(0.5)
    await drive_motor_for(0.3,80,80)
    await asyncio.sleep(0.5)
    await drive_motor_for(0.3,-80,-80)
    await stop()
    await asyncio.sleep(0.2)
    await HebelRauf(0)
    await asyncio.sleep(1)

    await GoonStreak()
    await HebelRauf(2)
    await GreiferZu()

    # picked drinks
    # next: ice 2
    
    await drive_line_back()
    await LinksUm()
    await line_drive()
    await line_drive()
    await RechtsUm()
    await line_drive_for(0.5)
    await backl(0.2)
    await LinksUm()
    await Vor(0.8)
    await stop()
    await eis_grab()
    await drive_till_line()
    
    
    

async def testing():
    await drive_motor_for(0.8,80,0)
    await Vor(0.5)
    await drive_motor_for(0.5,0,80)
    await drive_till_line()
    await Vor(1)
    await LinksUm()
    
    
    
    
async def run():
    await wait_for_light()  # You can use this function as needed
    #HebelRauf(4):
    await asyncio.gather(
        asyncio.create_task(end_when(15)),  # Stop after 10 seconds
        asyncio.create_task(testing())
        #asyncio.create_task(back(2))  # Run the main function
    )

# Run the event loop
asyncio.run(run())
