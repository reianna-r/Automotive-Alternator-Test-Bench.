'''
SIMULATOR LAYER
==============================
This module simulates current, voltage, and temperature for an automotive alternator 
system using user-defined inputs and configurable system constants. It models mathematical 
relationships between shaft speed, electrical load, and assumed design parameters to produce 
realistic operating values. It is designed to be independent of both the validation logic 
and any user interface components, allowing it to be integrated with alternative analysis or 
control systems.
'''

import math


class Simulator:
    '''A class to simulate an automotive alternator system: generates 
    current, temperature, and voltage values based on user inputs and 
    system constants using mathematical models.

Inputs:
        shaft_speed (float): Rotational speed of alternator shaft (RPM)
        electrical_load (float): Electrical demand (A)

    Simulator parameters:
        k_speed (float): Controls current growth rate with speed
        k_cool (float): Cooling rate 
        k_temp (float): Temperature-voltage coupling 
        time_step (float): Simulation timestep (seconds)
        t_ambient (float): Ambient environmental temperature (°C)

    Physical constants:
        i_max (float): Maximum current output (A)
        r_int (float): Internal resistance of alternator (Ω)
        req (float): Equivalent system resistance (Ω)
        thermal_capacity (float): Heat capacity of system (J/K)
        v_reg (float): Voltage regulator setpoint (V)
        power_loss (float): Baseline power loss (W)

    Outputs:
        current (float): Generated current (A)
        temperature (float): Internal temperature (°C)
        voltage (float): Output voltage (V)
'''

    def __init__(self, k_speed=1800, k_cool=0.5, k_temp=0.02, time_step=1, t_ambient=25):

        # physical constants (never adjustable)
        self.i_max = 120 # maximum current output (set by manufacturer limits)
        self.r_int = 0.02 #internal resistance of the alternator
        self.req = 0.04 # internal resistance of the system
        self.thermal_capacity = 1800
        self.v_reg = 14.2 # target voltage of alternator
        self.power_loss = 40 #power lost due to inefficiencies
        self.t_internal = 25 #COMMENT THIS!!!

        # simulator parameters (optionally adjustable)
        self.k_speed = k_speed # how quickly current increases with shaft speed
        self.k_cool = k_cool # how fast the system loses heat to environment
        self.k_temp = k_temp #temperature constant
        self.time_step = time_step #time interval per simulation step
        self.t_ambient = t_ambient # temperature of surroundings 

        # default simulator inputs (always adjustable)
        self.shaft_speed = 0.0
        self.electrical_load = 0.0

        
        # output variables
        self.current = 0.0
        self.temperature = 25 
        self.voltage = 0.0

    def compute_current(self):
        self.current = (
            self.i_max
            * (1 - math.exp(-self.shaft_speed / self.k_speed))
            * (self.electrical_load / 100)
        )
        return self.current

    def compute_temperature(self):
        heating = ((self.current ** 2 * self.req) + self.power_loss) / self.thermal_capacity * self.time_step
        cooling = self.k_cool * (self.t_internal - self.t_ambient) * self.time_step

        self.t_internal = self.t_internal + heating - cooling
        self.temperature = self.t_internal

        return self.temperature

    def compute_voltage(self):
        self.voltage = (
            self.v_reg
            - self.current * self.r_int
            - self.k_temp * (self.temperature - 25)
        )
        return self.voltage

    def run(self):
        print("\n==============================")
        print(" ALTERNATOR SIMULATION START ")
        print("==============================")

        self.get_user_inputs()
        # self.update_constants()

        current = self.compute_current()
        temperature = self.compute_temperature()
        voltage = self.compute_voltage()

        print("\n------------------------------")
        print(" RESULTS ")
        print("------------------------------")

        print(f"Current: {round(current, 4)} A")
        print(f"Temperature: {round(temperature, 2)} °C")
        print(f"Voltage: {round(voltage, 4)} V")

