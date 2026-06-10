'''
SIMULATOR LAYER
==============================
This module simulates current, voltage, and temperature for an automotive alternator 
system using user-defined inputs and mathematical models. All simulation values are 
stored in a Pandas DataFrame for further analysis. The layer is designed to be 
independent of both the validation logic and any user interface components.
'''

import math
import random 
import pandas as pd


class Simulator:
    def __init__(self, k_speed=1250, k_heat = 0.00009, k_cool=0.02, t_ambient=298, k_v=50, tau_v = 3, time_step=1, ):
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

        # constants (not adjustable in the UI layer)
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
    conditions. No time-dependant disturbance are applied at this stage.'''
        
        self.shaft_speed = self.base_shaft_speed
        self.electrical_load = self.base_electrical_load

        self.current = 0.0
        self.temperature = self.t_ambient
        self.voltage = 0.0
        

## --------------------SHAFT SPEED AND LOAD CALCULATIONS--------------------
    def update_operating_conditions(self):
        '''User-defined shaft speed and electrical load inputs are treated as baseline operating
    conditions. At each timestep, Gaussian noise is applied to these values to model
    real-world disturbances. The noise-augmented values are used in subsequent calculations.'''

        self.shaft_speed = (self.base_shaft_speed + random.gauss(0, self.speed_noise_frac * self.base_shaft_speed))
        self.electrical_load = (self.base_electrical_load + random.gauss(0, self.load_noise_frac * self.base_electrical_load))
        
        self.shaft_speed = max(0, self.shaft_speed) # prevents negative shaft speed values
        self.electrical_load = max(0, min(100, self.electrical_load)) # prevents percentages from exceeding 100


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


## --------------------DATAFRAME-------------------- 
    def build_dataframe(self):
        '''Creates a Pandas DataFrame containing all recorded simulation
    variables for each timestep.'''
        
        return pd.DataFrame({
            "Time": self.time_history,
            "ShaftSpeed":
                self.speed_history,
            "ElectricalLoad":
                self.load_history,
            "Current":
                self.current_history,
            "Temperature":
                self.temperature_history,
            "Voltage":
                self.voltage_history})


## --------------------MAIN SIMULATION LOOP-------------------- 
    def run(self, simulation_time=(150 +1)):
        '''Executes the simulation over the specified duration. At each timestep, operating 
        conditions are updated, output variables are calculated, and results are stored. 
        All recorded data is assembled into a DataFrame and returned.'''
        
        self.initialize_state() 

        # Determine the number of simulation iterations
        steps = int(simulation_time / self.time_step)

        for step in range(steps):
            current_time = (step * self.time_step)

            if step > 0:
                self.update_operating_conditions()
            
            else:
            # t = 0 uses the user-defined conditions (disturbances not applied)
                self.shaft_speed = self.base_shaft_speed
                self.electrical_load = self.base_electrical_load

            # calculate outputs
            self.compute_current()
            self.compute_temperature()
            self.compute_voltage()

            self.store_timestep(current_time)

        results = self.build_dataframe()

        return results



# #CODE USED TO TEST SIMULATOR IN THE TERMINAL

# if __name__ == "__main__":

#     print("\n=== SIMULATOR TEST MODE (TEMP) ===")

#     # --- USER INPUTS (TEMP UI LAYER) ---
#     system_type = input("Enter system type (12V or 24V): ").strip()

#     shaft_speed = float(input("Enter base shaft speed (RPM): "))
#     electrical_load = float(input("Enter electrical load (%): "))

#     print("\n--- CONFIG SUMMARY ---")
#     print(f"System Type: {system_type}")
#     print(f"Shaft Speed: {shaft_speed} RPM")
#     print(f"Electrical Load: {electrical_load}%")

#     # --- CREATE SIMULATOR ---
#     simulator = Simulator()

#     # TEMP: manually inject inputs (since UI layer doesn't exist yet)
#     simulator.base_shaft_speed = shaft_speed
#     simulator.base_electrical_load = electrical_load

#     # TEMP: system type mapping
#     if system_type == "12V":
#         simulator.v_reg = 14.2
#     elif system_type == "24V":
#         simulator.v_reg = 27.0
#     else:
#         raise ValueError("Invalid system type. Use 12V or 24V.")

#     print(f"\nRegulator voltage set to: {simulator.v_reg} V")

#     # --- RUN SIMULATION ---
#     results = simulator.run(simulation_time=(150 + 1))  # TEMP shorter run for testing

#     # --- OUTPUT ---
#     print("\n=== ALL RESULTS ===")
#     print(results)

#     print("\n=== FINAL STATE ===")
#     print(results.iloc[-1])
