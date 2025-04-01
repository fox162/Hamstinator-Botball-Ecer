#!/usr/bin/python3
import os, sys, time, asyncio
sys.path.append("/usr/lib")
import _kipr as k
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import Goon.src.main as goon

LEFT = 0   # Top-left wheel in image
RIGHT = 1  # Top-right wheel in image
VL = k.analog(0)
VR = k.analog(1)
HL = k.analog(2)
HR = k.analog(3)

async def mainD():
    vam = 0
    start_time = time.time()
    time_now = 0
    while vam < 2:
        while k.analog(0) < 3900 and k.analog(1) < 3900:
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

def stop():
    k.motor(LEFT, 0)
    k.motor(RIGHT, 0)

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

        if VL > 3900 or VR > 3900:
            if VL > 3900:
                rspeed = 200
                lspeed = 50
                k.motor(1, rspeed)
                k.motor(0, lspeed)
            else:
                rspeed = 50
                lspeed = 200
                k.motor(0, lspeed)
                k.motor(1, rspeed)

        if VL > 3900 and VR > 3900:
            break  # Break loop when both values exceed threshold

        await asyncio.sleep(0.1)  # Non-blocking sleep

async def drive_line_back():
    while k.analog(0) < 3900 and k.analog(1) < 3900:
        k.motor(0, -80)
        k.motor(1, -80)
        await asyncio.sleep(0.1)  # Non-blocking sleep
    stop()

async def drive_till_line():
    while k.analog(0) < 3900 and k.analog(1) < 3900:
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

        if VL > 3900 or VR > 3900:
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

async def main():
    print("main")
    await drive_motor_for(1, -80, -80)  # Move backward for 1 second
    await drive_motor_for(0.2, 80, 80)  # Move forward for 0.2 seconds

    await RechtsUm()  # Turn right
    await mainD()     # Main driving function
    await RechtsUm()  # Turn right again

    await line_drive()  # Navigate along the line
    await drive_motor_for(1, 80, 80)   # Move forward for 1 second
    await line_drive()

    await drive_motor_for(0.5, -80, -80)  # Move backward for 0.5 seconds
    await LinksUm()   # Turn left

    #goon.GreiferAuf()  # Operate gripper
    await drive_motor_for(4, 80, 80)   # Move forward for 4 seconds
    #stop()

    goon.GoonStreak()  # Perform action (likely interaction with Goons)
    
    await drive_line_back()  # Navigate along the line back
    await LinksUm()  # Turn left

    await drive_motor_for(1.5, 80, 80)   # Move forward for 1.5 seconds
    await RechtsUm()   # Turn right

    await drive_motor_for(0.7, 80, 80)   # Move forward for 0.7 seconds
    await asyncio.sleep(4)   # Wait for 4 seconds

    await drive_motor_for(0.7, -80, -80)   # Move backward for 0.7 seconds
    await LinksUm()   # Turn left

    await line_drive()  # Line following
    await drive_motor_for(0.8, 80, 80)   # Move forward for 0.8 seconds
    await RechtsUm()    # Turn right

    await drive_motor_for(0.5, 80, 80)   # Move forward for 0.5 seconds

    #goon.GreiferAufBecher()   # Operate gripper on the cup
    #goon.GreiferZuBecher()    # Operate gripper to close

    await RechtsUm()  # Turn right
    await drive_motor_for(0.4, 80, 80)   # Move forward for 0.4 seconds
    await stop()  # Stop

    await RechtsUm()  # Turn right again
    await drive_motor_for(1, 80, 80)   # Move forward for 1 second

    await asyncio.sleep(4)  # Wait for 4 seconds
    #goon.GreiferAufBecher()  # Operate gripper
    #goon.stroke(1)  # Perform stroke action
    #goon.stroke(2)
    #goon.stroke(3)
    #goon.stroke(4)

    await drive_line_back()  # Line following back

    await drive_motor_for(0.2, -80, -80)  # Move backward for 0.2 seconds
    await LinksUm()  # Turn left

    await line_drive()  # Line following
    await drive_motor_for(2, 80, 80)   # Move forward for 2 seconds
    await stop()

    await LinksUm()  # Turn left again

    await drive_motor_for(3, 80, 80)  # Move forward for 3 seconds

    # Drinks section
    await asyncio.sleep(4)  # Wait for 4 seconds

    await drive_line_back()  # Line following back

    await LinksUm()  # Turn left
    await line_drive()  # Line following

    await drive_motor_for(1, 80, 80)  # Move forward for 1 second
    await stop()

    await line_drive()  # Line following
    await drive_motor_for(1, 80, 80)  # Move forward for 1 second
    await stop()

    await line_drive()  # Line following
    print("asdf")
    await LinksUm()  # Turn left

    await line_drive()  # Line following

    await drive_motor_for(4, 80, 80)  # Move forward for 4 seconds
    await stop()

    await LinksUm()  # Turn left again

    await drive_motor_for(1, 80, 80)  # Move forward for 1 second
    await stop()

async def run():
    wait_for_light()  # You can use this function as needed
    await asyncio.gather(
        asyncio.create_task(end_when(125)),  # Stop after 10 seconds
        asyncio.create_task(main())  # Run the main function
    )

# Run the event loop
asyncio.run(run())

