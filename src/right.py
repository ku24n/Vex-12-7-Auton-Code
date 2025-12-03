#consts
PLACEHOLDER = 5
DEGREESPLACEHOLDER = 50

# ---------------------------------------------------------------------------- #
#                                                                              #
# 	Module:       main.py                                                      #
# 	Author:       limjedidiah8152                                              #
# 	Created:      11/6/2025, 8:09:52 AM                                        #
# 	Description:  V5 project                                                   #
#                                                                              #
# ---------------------------------------------------------------------------- #

# Library imports
from vex import *

#variables
e_brake_is_up = False
match_loader_is_up = False

# intializations
brain = Brain()
controller = Controller()
drive_train_intertial = Inertial(Ports.PORT19) # intertial sensor

# pneumatics
e_brake = DigitalOut(brain.three_wire_port.a) # e brake wheel
# descorer = DigitalOut(brain.three_wire_port.b) 
match_loader = DigitalOut(brain.three_wire_port.c)

#distance sensors
distance_a = Distance(Ports.PORT10) # distance sensor top
distance_b = Distance(Ports.PORT11) # distance sensor bottom

# define motors
intake_motor_entrance = Motor(Ports.PORT2, True) # entrance intake
intake_motor_top = Motor(Ports.PORT4, True) # top intake
outtake_motor = Motor(Ports.PORT6) # top outtake

#drive train motors
left_motor_a = Motor(Ports.PORT20, True) # left front motor
left_motor_b = Motor(Ports.PORT10, True) # left back motor
right_motor_a = Motor(Ports.PORT11) # right front motor
right_motor_b = Motor(Ports.PORT1) # right back motor

# define drive train
left_motor_group = MotorGroup(left_motor_a, left_motor_b)
right_motor_group = MotorGroup(right_motor_a, right_motor_b)
drive_train = SmartDrive(left_motor_group, right_motor_group, drive_train_intertial)

# functions
def intake(): # start intake
    intake_motor_entrance.spin(FORWARD)
    while not distance_a.is_object_detected() and not distance_b.is_object_detected(): # while no blocks in top chamber spin the top motor
        intake_motor_top.spin(FORWARD)

def intake_stop(): # stop intake
    intake_motor_entrance.stop()
    intake_motor_top.stop()

def intake_for_seconds(sec): # spin intake motor for sec SECONDS
    intake()
    wait(sec, SECONDS)
    intake_stop()

def outtake(): # start outtake
    intake()
    outtake_motor.spin(FORWARD)

def outtake_stop(): # stop outtake
    intake_stop()
    outtake_motor.stop()

def outtake_for_seconds(sec): # outtake for sec SECONDS
    outtake()
    wait(sec, SECONDS)
    outtake_stop()

def e_brake_down():
    e_brake.set(True)
    e_brake_is_up = False

def e_brake_up():
    e_brake.set(False)
    e_brake_is_up = True

def match_loader_up():
    match_loader.set(True)
    match_loader_is_up = True

def match_loader_down():
    match_loader.set(False)
    match_loader_is_up = True

# main functions

def pre_autonomous(): # runs before autonomous
    # calibrate inertial
    drive_train_intertial.calibrate()
    while drive_train_intertial.is_calibrating():
        wait(50, MSEC)


pre_autonomous()

def autonomous():
    drive_train_intertial.set_heading(0) # reset heading

    brain.screen.clear_screen()
    brain.screen.print("autonomous code")
    # place automonous code here
    drive_train.set_drive_velocity(20, PERCENT)
    drive_train.set_turn_velocity(20, PERCENT)
    outtake_motor.set_velocity(100, PERCENT)

    # route
    # start intake
    intake()
    drive_train.drive_for(FORWARD, PLACEHOLDER, INCHES) # start forward
    drive_train.turn_for(LEFT, DEGREESPLACEHOLDER, DEGREES) # right 
    # stop intake
    intake_stop()
    drive_train.drive_for(REVERSE, PLACEHOLDER,INCHES) # backwards align with goal
    drive_train.turn_for(LEFT, DEGREESPLACEHOLDER, DEGREES) # turn so output faces goal
    drive_train.drive_for(REVERSE, PLACEHOLDER, INCHES) # back into goal
    # start outtake
    outtake()
    # if time + to column vvv

def user_control():
    

    brain.screen.clear_screen()
    brain.screen.print("driver control")
    # place driver control in this while loop
    while True:
        turn = controller.axis1.position()
        forward = controller.axis3.position()

        drive_train.drive(DirectionType.FORWARD, forward, VelocityUnits.PERCENT) 
        
        if turn > 0:
            drive_train.turn(RIGHT, turn, VelocityUnits.PERCENT)
            brain.screen.print("turn RIGHT\n")
        elif turn < 0:
            drive_train.turn(LEFT, -turn, VelocityUnits.PERCENT)
            brain.screen.print("turn LEFT\n")
        # button functions
        if e_brake_is_up: # map e brake functions to one button
            controller.buttonUp.pressed(e_brake_down)
        elif not e_brake_is_up:
            controller.buttonUp.pressed(e_brake_up)

        if match_loader_is_up: # map match loader functions to one button
            controller.buttonDown.pressed(match_loader_down)
        elif not e_brake_is_up:
            controller.buttonDown.pressed(match_loader_up)

        controller.buttonR1.pressed(intake) # can change buttons later
        controller.buttonL1.pressed(outtake) # can change buttons later

        wait(20, MSEC)
# create competition instance
comp = Competition(user_control, autonomous)

# actions to do when the program starts
brain.screen.clear_screen()

autonomous() # remove at comp