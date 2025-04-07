#!/usr/bin/python3
import os, sys, time
sys.path.append("/usr/lib")
import _kipr as k

class Omi_Wheel:
    def __init__(self):
        self.FRONT_LEFT = 0   # Top-left wheel in image
        self.FRONT_RIGHT = 1  # Top-right wheel in image
        self.REAR_LEFT = 2    # Bottom-left wheel in image
        self.REAR_RIGHT = 3   # Bottom-right wheel in image

    def motor(self, motor_id, speed):
        """Control individual motors"""
        k.motor(motor_id, speed)

    def RechtsUp(self, speed=80):
        self.motor(self.FRONT_LEFT, 0)
        self.motor(self.FRONT_RIGHT, speed)
        self.motor(self.REAR_LEFT, speed)
        self.motor(self.REAR_RIGHT, 0)

    def LinksUp(self, speed=80):
        self.motor(self.FRONT_LEFT, speed)
        self.motor(self.FRONT_RIGHT, 0)
        self.motor(self.REAR_LEFT, 0)
        self.motor(self.REAR_RIGHT, speed)

    def LinksBack(self, speed=80):
        self.motor(self.FRONT_LEFT, -speed)
        self.motor(self.FRONT_RIGHT, 0)
        self.motor(self.REAR_LEFT, 0)
        self.motor(self.REAR_RIGHT, -speed)

    def RechtsBack(self, speed=80):
        self.motor(self.FRONT_LEFT, 0)
        self.motor(self.FRONT_RIGHT, -speed)
        self.motor(self.REAR_LEFT, -speed)
        self.motor(self.REAR_RIGHT, 0)

    def Vor(self, speed=80):
        self.motor(self.FRONT_LEFT, speed)
        self.motor(self.FRONT_RIGHT, speed)
        self.motor(self.REAR_LEFT, speed)
        self.motor(self.REAR_RIGHT, speed)

    def Back(self, speed=80):
        self.motor(self.FRONT_LEFT, -speed)
        self.motor(self.FRONT_RIGHT, -speed)
        self.motor(self.REAR_LEFT, -speed)
        self.motor(self.REAR_RIGHT, -speed)

    def RechtsUm(self, speed=80):
        self.motor(self.FRONT_LEFT, -speed)
        self.motor(self.FRONT_RIGHT, speed)
        self.motor(self.REAR_LEFT, -speed)
        self.motor(self.REAR_RIGHT, speed)

    def LinksUm(self, speed=80):
        self.motor(self.FRONT_LEFT, speed)
        self.motor(self.FRONT_RIGHT, -speed)
        self.motor(self.REAR_LEFT, speed)
        self.motor(self.REAR_RIGHT, -speed)

    def Rechts(self, speed=80):
        self.motor(self.FRONT_LEFT, -speed)
        self.motor(self.FRONT_RIGHT, speed)
        self.motor(self.REAR_LEFT, speed)
        self.motor(self.REAR_RIGHT, -speed)

    def Links(self, speed=80):
        self.motor(self.FRONT_LEFT, speed)
        self.motor(self.FRONT_RIGHT, -speed)
        self.motor(self.REAR_LEFT, -speed)
        self.motor(self.REAR_RIGHT, speed)

    def Stop(self, speed=80):
        self.motor(self.FRONT_LEFT, 0)
        self.motor(self.FRONT_RIGHT, 0)
        self.motor(self.REAR_LEFT, 0)
        self.motor(self.REAR_RIGHT, 0)

def main():
    robot = Omi_Wheel()
    robot.Rechts()
    time.sleep(1)
    robot.Links()
    time.sleep(1)
    robot.Vor()
    time.sleep(1)
    robot.Back()
    time.sleep(1)
    robot.LinksUm()
    time.sleep(1)
    robot.RechtsUm()
    time.sleep(1)
    robot.RechtsUp()
    time.sleep(1)
    robot.LeftUp()
    time.sleep(1)
    robot.Stop()

if __name__ == "__main__":
    main()