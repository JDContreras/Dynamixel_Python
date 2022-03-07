import os

if os.name == 'nt':
    import msvcrt
    def getch():
        return msvcrt.getch().decode()
else:
    import sys, tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    def getch():
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

from dynamixel_sdk import *                   
from dynamixel_sdk import PortHandler, PacketHandler
# Direcciones de las variables a controlar para el AX-12
ADDR_AX_TORQUE_ENABLE      = 24               
ADDR_AX_GOAL_POSITION      = 30
ADDR_AX_PRESENT_POSITION   = 36
TORQUE_ENABLE               = 1   
TORQUE_DISABLE              = 0  
DXL_MINIMUM_POSITION_VALUE  = 1           # limite minimo de posicion
DXL_MAXIMUM_POSITION_VALUE  = 1023        # limite maximo de posicion
DXL_MOVING_STATUS_THRESHOLD = 1           # threshold para posicion

# Protocol version
PROTOCOL_VERSION            = 1.0               # See which protocol version is used in the Dynamixel

# parametros de comunicacion
DXL_ID                      = 1                 # Dynamixel ID : 1
BAUDRATE                    = 1000000             # Dynamixel default baudrate : 57600
DEVICENAME                  = 'COM3'    # Check which port is being used on your controller

class AX_12_Control:
    def __init__(self, ID, port, baudrate):
        self.portHandler = PortHandler(port)
        self.packetHandler = PacketHandler(PROTOCOL_VERSION)
        self.baudrate = baudrate
        self.State = False
        self.ID = ID #list de ID

    def connect(self):
        if self.portHandler.openPort():
            print("Succeeded to open the port")
        else:
            print("Failed to open the port")

    
        if self.portHandler.setBaudRate(self.baudrate):
            print("Succeeded to change the baudrate")
        else:
            print("Failed to change the baudrate")

    def enable(self):
        for i in self.ID:
            check = self.write(i,1,24,1)
            if check == False:
                self.State = False
                print("fail to enable motor with ID " + str(i) )
                return False
        self.State = True
        return True
    
    def disable(self):
        for i in self.ID:
            check = self.write(i,1,24,0)
            if check == False:
                print("fail to disable motor with ID " + str(i) )
                return False
        self.State = False
        return True


    def write(self, ID, value, address, size):
        packetHandler, portHandler = self.packetHandler, self.portHandler
        if portHandler.is_open:
            if size == 1:
                dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, ID, address, value)
            elif size == 2: 
                dxl_comm_result, dxl_error = packetHandler.write2ByteTxRx(portHandler, ID, address, value)
            else:
                print("invalid size")
                return False

            if dxl_comm_result != COMM_SUCCESS:
                print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
                return False
            elif dxl_error != 0:
                print("%s" % packetHandler.getRxPacketError(dxl_error))
                return False
            else:
                return True
        else: 
            print("first open the port")
            return False

    def setTorque(self,Motor, Torque):
        data = int(Torque*1023/100)
        if data>1023:
            self.write(self.ID[Motor],1023,34,2)
        else: 
            self.write(self.ID[Motor],data,34,2)
    
    def setSpeed(self, Motor, Speed):
        data = int(Speed*1023/100)
        if data>1023:
            self.write(self.ID[Motor],1023,32,2)
        else: 
            self.write(self.ID[Motor],data,32,2)

    def setGoalPosition(self, Motor, Pos):
        #todo: set limits
        data = int(Pos*1023/100)
        if data>1023:
            self.write(self.ID[Motor],1023,30,2)
        else: 
            self.write(self.ID[Motor],data,30,2)

    def move(self, Motor, pos, vel, tor):
        #todo: error check en escalera
        if self.State:
            self.setTorque(Motor,tor)
            self.setSpeed(Motor,vel)
            self.setGoalPosition(Motor,pos)
            return 0
        else: 
            print("first enable the motor")
            return 1

    def read(self, ID, address, size):
        packetHandler, portHandler = self.packetHandler, self.portHandler
        if portHandler.is_open:
            if size == 1:
                value, dxl_comm_result, dxl_error = packetHandler.read1ByteTxRx(portHandler, ID, address)
            elif size == 2: 
                value, dxl_comm_result, dxl_error = packetHandler.read2ByteTxRx(portHandler, ID, address)
            else:
                print("invalid size")
                return False

            if dxl_comm_result != COMM_SUCCESS:
                print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
                return False
            elif dxl_error != 0:
                print("%s" % packetHandler.getRxPacketError(dxl_error))
                return False
            else:
                return value

    
        else: 
            print("first open the port")
            return False



# M = AX_12_Control([1,2],"COM3",1000000)
# M.connect()
# M.enable()
# 
# 
# M.move(0,10,100,30)
# M.move(1,10,100,30)
# 
# print(M2)
