'''
SIMULATOR LAYER
==============================
This module simulates current, voltage, and temperature for an automotive alternator 
system using user-defined inputs and mathematical models. All simulation values are 
stored in a Pandas DataFrame for further analysis. The layer is designed to be 
independent of both the validation logic and any user interface components.
'''

import math
import pandas as pd
import numpy as np


class Simulator:
    '''ADD DOSCTSINRG !!!'''
    def __init__(self, k_speed=1250, k_heat = 0.00009, k_cool=0.02, t_ambient=298, k_v=2000, tau_v = 3, time_step=1, ):
        '''Initializes the simulator by defining user inputs, simulation
    parameters, physical constants, disturbance model parameters,
    calculation variables, and data storage structures used.'''

        # user inputs
        self.base_shaft_speed = 0
        self.base_electrical_load = 0

        # simulation parameters (optionally adjustable)
        self.t_ambient = t_ambient
        self.time_step = time_step
        
        # physical constants (never adjustable)
        self.i_max = 275 
        self.v_reg = 14.2 

        # constants (not adjustable in the UI layer; modify in main.py or Simulator constructor)
        self.k_speed = k_speed
        self.k_heat = k_heat
        self.k_cool = k_cool
        self.k_v = k_v
        self.tau_v = tau_v
        
        # load and shaft speed disturbance model parameters
        self.speed_noise_frac = 0.02
        self.load_noise_frac = 0.02    
        
        # calculation outputs
        self.shaft_speed = self.base_shaft_speed
        self.electrical_load = self.base_electrical_load
        self.current = 0.0
        self.temperature = t_ambient
        self.voltage = 0.0
  
        # data storage
        self.time_history = []
        self.speed_history = []
        self.load_history = []
        self.current_history = []
        self.temperature_history = []
        self.voltage_history = []


    ## --------------------INITIALIZING STATE-------------------- 
    def initialize_state(self): 
        ''' Initializes the simulation state at t = 0 using the user-defined operating 
    conditions. No time-dependant disturbances are applied at this stage.'''
        
        self.shaft_speed = self.base_shaft_speed
        self.electrical_load = self.base_electrical_load

        self.current = 0.0
        self.temperature = self.t_ambient
        self.voltage = 0.0

        # ensures previous simulation history is cleared
        self.time_history = []
        self.speed_history = []
        self.load_history = []
        self.current_history = []
        self.temperature_history = []
        self.voltage_history = []

        
    ## --------------------SHAFT SPEED AND LOAD CALCULATIONS-------------------- 
    def update_operating_conditions(self):
        '''User-defined shaft speed and electrical load inputs are treated as baseline operating
    conditions. At each timestep, Gaussian noise is applied to these values to model
    real-world disturbances. The noise-augmented values are used in subsequent calculations.'''

        self.shaft_speed = self.base_shaft_speed + np.random.normal(0, self.speed_noise_frac * self.base_shaft_speed)
        self.electrical_load = self.base_electrical_load + np.random.normal(0, self.load_noise_frac * self.base_electrical_load)
        
        self.shaft_speed = np.clip(self.shaft_speed, 0, None)
        self.electrical_load = np.clip(self.electrical_load, 0, 100)


    ## --------------------CURRENT MODEL--------------------
    def compute_current(self):
        '''Calculates current using a mathematical model derived from electromagnetic 
    principles and saturation models.'''

        self.current = (self.i_max* (1- math.exp(-self.shaft_speed/ self.k_speed)) * (self.electrical_load / 100))
        return self.current


    ## --------------------TEMPERATURE MODEL--------------------
    def compute_temperature(self):
        '''Calculates temperature using a mathematical model derived from thermal principles, 
    and values fed from the compute_current function.'''
        
        dTdt = (self.k_heat * self.current**2-self.k_cool* (self.temperature - self.t_ambient))    
        self.temperature += (dTdt * self.time_step)
        return self.temperature


    ## --------------------VOLTAGE MODEL--------------------
    def compute_voltage(self):
        '''Calculates voltage using a mathematical model derived from electromagnetic 
    principles and saturation models.'''

        v_target = self.v_reg * (1 - math.exp(-self.shaft_speed / self.k_v))
        dVdt = (v_target - self.voltage) / self.tau_v
        self.voltage += dVdt * self.time_step
        return self.voltage


    ## --------------------DATA STORAGE--------------------
    def store_timestep(self, time):
        '''Stores all calculated simulation values for the current timestep
    so they can later be assembled into a DataFrame.'''

        self.time_history.append(time)
        self.speed_history.append(self.shaft_speed)
        self.load_history.append(self.electrical_load)
        self.current_history.append(self.current)
        self.temperature_history.append(self.temperature)
        self.voltage_history.append(self.voltage)


    ## --------------------STEADY STATE DETECTION--------------------
    def has_reached_steady_state(self, window=10, voltage_tol=0.01, current_tol=0.01, temperature_tol=0.01):
        '''Determines whether the system has reached steady-state (by checking if
    variations in voltage, current, and temperature over the most recent
    time window are negligible.'''
        
        if len(self.voltage_history) < window: # ensures enough time-series data points available to assess for steady state
            return False

        # slicing to extract most recent values
        v = self.voltage_history[-window:]
        i = self.current_history[-window:]
        t = self.temperature_history[-window:]

        # determining if voltage, current, and temperature are in steady state conditions and returning boolean values                    
        voltage_steady = (max(v) - min(v) < max(voltage_tol * np.mean(v), 0.01))
        current_steady = (max(i) - min(i) < max(current_tol * np.mean(i), 0.1))
        temperature_steady = (max(t) - min(t) < max(temperature_tol * np.mean(t), 0.05))
        
        return (voltage_steady and current_steady and temperature_steady)


    ## --------------------DATAFRAME-------------------- 
    def build_dataframe(self):
        '''Creates a Pandas DataFrame containing all recorded simulation
    variables for each timestep.'''

        return pd.DataFrame({
            "Time": np.array(self.time_history),
            "ShaftSpeed": np.array(self.speed_history),
            "ElectricalLoad": np.array(self.load_history),
            "Current": np.array(self.current_history),
            "Temperature": np.array(self.temperature_history),
            "Voltage": np.array(self.voltage_history)})


    ## --------------------MAIN SIMULATION LOOP-------------------- 
    def run(self, simulation_time=300, run_until_steady=False):
        '''Executes the simulation over the specified duration: either until a specified maximum 
    or until steady state is achieved). At each timestep, operating conditions are updated, 
    output variables are calculated, and results are stored.'''
        
        self.initialize_state()

        # determining number of iterations to simulate (inclusive values)
        steps = int(round((simulation_time / self.time_step) + 1))

        for step in range(steps):
            current_time = step * self.time_step

            if step > 0:
                self.update_operating_conditions()

            self.compute_current()
            self.compute_temperature()
            self.compute_voltage()

            self.store_timestep(current_time)

            # if enabled, exit the loop only once steady state is achieved, otherwise until maximum simulation duration
            if run_until_steady:
                if self.has_reached_steady_state():
                    break

        results = self.build_dataframe()
        return results