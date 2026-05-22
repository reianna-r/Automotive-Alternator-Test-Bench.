'''
VALIDATION LAYER
==============================
This module is resposible for validating the following in accordance with 
the SAE J56 SURFACE VEHICLE STANDARD: (1) Voltage stability and line drop 
conditions. (2) Current performance at defined RPM milestones. (3) Thermal 
stabilization and ambient conditions. (4) Load dump safety (regulator 
performance). It indicates a PASS or FAIL for each parameter to determine 
the overall system status.This layer is designed to be independent of the 
simulation engine and user interface, allowing it to be reused in different 
testing or analysis setups.
'''

def check_voltage_stability(system_type, voltage, load_voltage):
    """Checks test voltage window and line drop condition."""

    if system_type == 12:
        v_target = 13.5
        v_min, v_max = 13.4, 13.6
    
    else:
        v_target = 27.0
        v_min, v_max = 26.8, 27.2

    voltage_ok = v_min <= voltage <= v_max


    # line drop check
    line_drop = abs(voltage - load_voltage)
    line_drop_ok = line_drop <= 0.5

    return {
        "voltage_ok": voltage_ok,
        "line_drop_ok": line_drop_ok,
        "line_drop": line_drop
    }


def check_current_performance(rpm, current, I_L, I_R):
    """Checks alternator current at key RPM milestones."""

    idle_ok = True
    rated_ok = True

    if rpm == 1500:
        idle_ok = current >= I_L

    if rpm == 6000:
        rated_ok = current >= I_R

    return {
        "idle_ok": idle_ok,
        "rated_ok": rated_ok
    }


# def check_cut_in_speed(rpm, cut_in_speed):
#     """Checks if alternator should be producing output."""

#     if rpm < cut_in_speed:
#         return current == 0  # expected no output
#     return True


# ==============================
# THERMAL VALIDATION
# ==============================

def check_thermal_stability(current_history):
    """
    Checks if current is stabilized within ±2% over time.
    current_history: list of current values over 5 min window
    """

    if len(current_history) < 2:
        return False

    max_current = max(current_history)
    min_current = min(current_history)

    if max_current == 0:
        return True

    variation = (max_current - min_current) / max_current
    return variation <= 0.02


def check_ambient_temperature(temp):
    """Checks if ambient temperature is within 23°C ±5°C."""
    return 18 <= temp <= 28


# ==============================
# LOAD DUMP TEST
# ==============================

def check_load_dump(voltage_after_dump, voltage_limit):
    """
    Checks regulator response during load dump event.
    """
    return voltage_after_dump <= voltage_limit


# ==============================
# MAIN EVALUATION FUNCTION
# ==============================

def evaluate_system(
    system_type,
    voltage,
    load_voltage,
    rpm,
    current,
    I_L,
    I_R,
    cut_in_speed,
    current_history,
    temp,
    voltage_after_dump,
    voltage_limit
):
    """Evaluates full alternator system based on all criteria."""

    voltage_results = check_voltage_stability(system_type, voltage, load_voltage)
    current_results = check_current_performance(rpm, current, I_L, I_R)

    thermal_ok = check_thermal_stability(current_history)
    ambient_ok = check_ambient_temperature(temp)

    load_dump_ok = check_load_dump(voltage_after_dump, voltage_limit)

    overall_ok = (
        ambient_ok and
        voltage_results["voltage_ok"] and
        voltage_results["line_drop_ok"] and
        current_results["idle_ok"] and
        current_results["rated_ok"] and
        thermal_ok and
        load_dump_ok
    )

    return {
        "voltage": voltage_results,
        "current": current_results,
        "thermal_ok": thermal_ok,
        "ambient_ok": ambient_ok,
        "load_dump_ok": load_dump_ok,
        "overall_ok": overall_ok
    }

    




