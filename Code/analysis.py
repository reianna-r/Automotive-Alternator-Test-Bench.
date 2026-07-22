'''
ANALYSIS LAYER
==============================
This module analyzes and processes raw time-series data from the simulation 
engine by applying signal filtering and feature extraction methods (such as 
peak detection, and ripple frequency analysis). The use of processed data
in the validation layer as opposed to raw data ensures the accuracy of 
pass/fail decisions by preventing short transient events from being incorrectly 
flagged as failures. The layer is designed to be independent from other layers.
'''

import numpy as np
from scipy.signal import savgol_filter, find_peaks


class Analysis:
    '''Takes raw time-series data from the simulator layer and processes it using filtering and feature extraction techniques.'''
    def __init__(self, results_df, time_step=1):
        self.df = results_df # stores the simulation output DataFrame received from the simulator layer
        self.dt = time_step # defines the time interval between simulation samples 

        # Extract simulation signals from the DataFrame as NumPy arrays 
        self.time = np.array(self.df["Time"])
        self.voltage = np.array(self.df["Voltage"])
        self.current = np.array(self.df["Current"])
        self.temperature = np.array(self.df["Temperature"])
        self.speed = np.array(self.df["ShaftSpeed"])
        self.load = np.array(self.df["ElectricalLoad"])

        # initialize filtered signals with raw data until filtering is performed
        self.voltage_smooth = self.voltage.copy()
        self.current_smooth = self.current.copy()
        self.temperature_smooth = self.temperature.copy()


    ## --------------------SIGNAL FILTERING--------------------
    def smooth_signals(self, smooth_time=10, poly=2):
        '''Applies a Savitzky-Golay filter to reduce noise while preserving
    the shape of the signal. Takes in parameters smooth_time (seconds 
    to be smoothed over) and poly (polynomial order used by the filter.'''

        window = int(smooth_time / self.dt) # convert smoothing time into number of samples to be smoothed 
        
        window = max(window, poly + 1) # window must be larger than polynomial order
        
        # window cannot be longer than the signal
        max_window = len(self.voltage) # voltage is used here for number of time-step values; but any signal array with the same length could be used
        window = min(window, max_window)
        
        # window must be odd
        if window % 2 == 0: 
            window -= 1

        self.voltage_smooth = savgol_filter(self.voltage,window_length=window,polyorder=poly)
        self.current_smooth = savgol_filter(self.current,window_length=window,polyorder=poly)
        self.temperature_smooth = savgol_filter(self.temperature,window_length=window,polyorder=poly)

        return {
            "voltage": self.voltage_smooth,
            "current": self.current_smooth,
            "temperature": self.temperature_smooth} 
    

    ## --------------------PEAK DETECTION-------------------- 
    def detect_peaks(self,voltage_prominence=0.2, current_prominence=2,temperature_prominence=1):
        '''Detects transient events in the signals by taking prominence (minimum peak required 
        to be considered significant) parameters and returning dictionaries containing indices 
        and values of peaks.'''
            
        # local variables created for readability 
        voltage_signal = self.voltage_smooth
        current_signal = self.current_smooth
        temperature_signal = self.temperature_smooth

        # uses the sci py find_peaks function to identify potential peaks in the data
        voltage_peaks, _ = find_peaks(voltage_signal, prominence=voltage_prominence) 
        current_peaks, _ = find_peaks(current_signal, prominence=current_prominence)
        temperature_peaks, _ = find_peaks(temperature_signal, prominence=temperature_prominence)

        return {
            "voltage_peak_times": self.time[voltage_peaks],
            "voltage_peak_values": voltage_signal[voltage_peaks],

            "current_peak_times": self.time[current_peaks],
            "current_peak_values": current_signal[current_peaks],

            "temperature_peak_times": self.time[temperature_peaks],
            "temperature_peak_values": temperature_signal[temperature_peaks]}


    ## --------------------STEADY STATE IDENTIFICATION AND EXTRACTION-------------------- 
    def detect_steady_state(self, window_size=10, threshold=0.01, rate_threshold=0.001, required_stable_window=5):
        '''Detects the point where the system becomes steady-state and extracts averaged steady-state values.'''

        def is_steady(window): # defining what steady state is for a small window
            '''Defining what a steady state window looks like by evaluating signal variation (maximum 
            minus minimum values) and the magnitude of changes between consecutive samples (slope).'''

            variation = np.max(window) - np.min(window) # calculates variation of values inside a window
            variation_ok = variation < threshold * max(abs(np.mean(window)), 1e-6) # evaluates if the window variation is small enough to be considered 'stable'
        
            rate_of_change = (np.diff(window))/self.dt # calculates rate of change of values 
            rate_ok = (np.all(np.abs(rate_of_change) < rate_threshold)) # evaluates if rate of change can be considered negligible

            return variation_ok and rate_ok

        start_index = None
        stable_count = 0

        for i in range(len(self.voltage_smooth)-window_size+1): # extract small time window for each variable
            v_window = self.voltage_smooth[i:i+window_size]
            i_window = self.current_smooth[i:i+window_size]
            t_window = self.temperature_smooth[i:i+window_size]

            # checks if all signals in the window are stable to define steady-state
            if (is_steady(v_window) and is_steady(i_window) and is_steady(t_window)): 
                stable_count += 1

                if stable_count >= required_stable_window:
                    start_index = i - required_stable_window + 1 
                    break

            else:
                stable_count = 0

        # steady state was never found
        if start_index is None:
            return {
            "steady_state_found": False,
            "steady_voltage": None,
            "steady_current": None,
            "steady_temperature": None}
            
        return {
        "steady_state_found": True,
        "steady_voltage": np.mean(self.voltage_smooth[start_index:]),
        "steady_current": np.mean(self.current_smooth[start_index:]),
        "steady_temperature": np.mean(self.temperature_smooth[start_index:]),
        "steady_state_start_index": start_index}
    

    ## --------------------RIPPLE ANALYSIS--------------------
    def ripple_analysis(self, steady_state):
        '''Measures steady-state voltage and current ripple using the standard
        deviation of the steady-state signals.'''

        # if steady state was never reached, ripple cannot be calculated
        if not steady_state["steady_state_found"]:
            return {
                "voltage_ripple": None,
                "current_ripple": None}

        start = steady_state["steady_state_start_index"] 

        voltage_window = self.voltage_smooth[start:]
        current_window = self.current_smooth[start:]

        voltage_ripple = np.std(voltage_window)
        current_ripple = np.std(current_window)

        return {
            "voltage_ripple": voltage_ripple,
            "current_ripple": current_ripple}


    ## --------------------FINAL PROCESSING--------------------
    def process_all(self):
        '''Runs full analysis pipeline and returns validation-ready metrics.'''
        self.smooth_signals()

        steady = self.detect_steady_state()

        return {
            "steady_state": steady,
            "peaks": self.detect_peaks(),
            "ripple": self.ripple_analysis(steady)}
            