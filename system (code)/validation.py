
'''
VALIDATION LAYER
================
This layer is resposible for validating the following in accordance with 
the SAE J56 SURFACE VEHICLE STANDARD: (1) Voltage stability and line drop 
conditions. (2) Current performance at defined RPM milestones. (3) Thermal 
stabilization and ambient conditions. (4) Load dump safety (regulator 
performance). It indicates a PASS or FAIL for each parameter to determine 
the overall system status.This layer is designed to be independent of the 
simulation engine and user interface, allowing it to be reused in different 
testing or analysis setups.'''

class Validation:
    '''Evaluates alternator's performance by comparing raw simulation data and processed analysis results 
    against SAE J56 standards. Generates an overall PASS, FAIL, or NOT TESTED result.'''
    def __init__(self, results_df, analysis_results, system_type=12, ambient_temp_k=298):
        self.results = results_df
        self.analysis_results = analysis_results

        self.steady_state = analysis_results["steady_state"]
        self.peaks = analysis_results["peaks"]
        self.ripple = analysis_results["ripple"]

        self.current_equilibrium = analysis_results["current_equilibrium"]

        self.system_type = int(system_type)
        self.ambient_temp_k = ambient_temp_k

        # alternator operating limits
        self.rated_current = 275
        self.max_temperature = 393  # Kelvin (120 C)

        # voltage regulation limits
        self.voltage_nominal = (14.2 if self.system_type == 12 else 27.5)
        self.voltage_tolerance = 0.5

        # voltage ripple limit
        self.voltage_ripple_max = 0.1

        # ambient temperature limits
        self.ambient_temp_min = 18
        self.ambient_temp_max = 28


    ## --------------------RESULT FORMATTING--------------------
    def make_result(self, passed, message):
        return {"status": "PASS" if passed else "FAIL", "pass": bool(passed), "message": message}

    def not_tested(self, message):
        return {"status": "NOT TESTED", "pass": None, "message": message}


    ## --------------------VOLTAGE VALIDATION-------------------- 
    def validate_voltage(self):
        '''Validates steady-state voltage against the specified voltage limits.'''
        voltage_result = self.analysis_results["individual_steady_states"]["voltage"]

        if not voltage_result["steady_state_found"]:
            return self.not_tested(
                "Voltage steady state was not detected.")

        voltage = voltage_result["steady_value"]

        lower_limit = (self.voltage_nominal - self.voltage_tolerance)
        upper_limit = (self.voltage_nominal + self.voltage_tolerance)

        passed = lower_limit <= voltage <= upper_limit

        return self.make_result(passed, f"Steady-state voltage: {voltage:.2f} V | "
            f"Allowed range: {lower_limit:.2f} - "
            f"{upper_limit:.2f} V")


    ## --------------------CURRENT EQUILBIRUM VALIDATION-------------------- 
    def validate_current(self):
        '''Validates current stability by checking variation over a continuous 300-second window.'''
        result = self.current_equilibrium

        # if not enough data to complete a 300-second test
        if not result["test_completed"]:
            return self.not_tested(
                "Insufficient data. A continuous 300-second "
                "current measurement window is required.")

        average_current = result["average_current"]

        # relative variation cannot be evaluated at zero current.
        if average_current is None:
            return self.not_tested(
                "Current equilibrium cannot be evaluated because "
                "the measured current is zero or unavailable.")

        variation = result["variation_percent"]
        allowed = result["allowed_variation_percent"]

        passed = result["equilibrium_reached"]

        message = (
            f"Current variation: {variation:.2f}% | "
            f"Maximum allowed: {allowed:.2f}% | "
            f"Average current: {average_current:.2f} A | "
            f"Measurement window: "
            f"{result['window_start_time']:.2f} - "
            f"{result['window_end_time']:.2f} s")

        return self.make_result(passed, message)


    ## --------------------CURRENT RATING VALIDATION-------------------- 
    def validate_current_rating(self):
        '''Checks whether the maximum measured current exceeds the alternator's rated current.'''
        maximum_current = self.results["Current"].max()
        passed = maximum_current <= self.rated_current
        return self.make_result(
            passed,
            f"Maximum measured current: {maximum_current:.2f} A | "
            f"Maximum allowed: {self.rated_current:.2f} A")

    
    ## --------------------TEMPERATURE VALIDATION-------------------- 
    def validate_temperature(self):
        '''Validates steady-state operating temperature against the maximum allowable temperature.'''
        temperature_result = self.analysis_results["individual_steady_states"]["temperature"]

        if not temperature_result["steady_state_found"]:
            return self.not_tested("Temperature steady state was not detected.")

        temperature = temperature_result["steady_value"]

        temperature_c = temperature - 273.15
        limit_c = self.max_temperature - 273.15

        passed = temperature <= self.max_temperature

        return self.make_result(
            passed,
            f"Steady-state temperature: {temperature_c:.2f} C | "
            f"Maximum allowed: {limit_c:.2f} C")

    
    ## --------------------VOLTAGE RIPPLE VALIDATION-------------------- 
    def validate_voltage_ripple(self):
        '''Checks whether steady-state voltage ripple is within the specified tolerance.'''
        if not self.steady_state["steady_state_found"]:
            return self.not_tested("Voltage ripple cannot be checked without voltage and temperature steady state.")

        ripple = self.ripple["voltage_ripple"]

        if ripple is None:
            return self.not_tested(
                "Voltage ripple data is unavailable.")

        passed = ripple <= self.voltage_ripple_max

        return self.make_result(
            passed,
            f"Voltage ripple (standard deviation): {ripple:.8f} V | "
            f"Maximum allowed: {self.voltage_ripple_max:.2f} V")


    ## --------------------AMBIENT TEMPERATURE VALIDATION-------------------- 
    def validate_ambient_temperature(self):
        '''Checks whether the ambient temperature falls within the specified operating range.'''
        ambient_temp_c = self.ambient_temp_k - 273.15

        passed = (self.ambient_temp_min <= ambient_temp_c <= self.ambient_temp_max)

        return self.make_result(
            passed,
            f"Ambient temperature: {ambient_temp_c:.2f} C | "
            f"Allowed range: {self.ambient_temp_min} - "
            f"{self.ambient_temp_max} C")

   
    ## --------------------OVERAL SYSTEM VALIDATION-------------------- 
    def evaluate_system(self):
        '''Evaluates all validation criteria and determines the overall system PASS, FAIL, or INCOMPLETE status.'''
        report = {
            "voltage": self.validate_voltage(),
            "current_equilibrium": self.validate_current(),
            "current_rating": self.validate_current_rating(),
            "temperature": self.validate_temperature(),
            "voltage_ripple": self.validate_voltage_ripple(),
            "ambient_temperature": self.validate_ambient_temperature()}

        statuses = [result["status"] for result in report.values()]

        if "FAIL" in statuses:
            overall_status = "FAIL"

        elif "NOT TESTED" in statuses:
            overall_status = "INCOMPLETE"

        else:
            overall_status = "PASS"

        report["overall_status"] = overall_status

        return report
