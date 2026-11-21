# Automotive Alternator Test Bench

<p align="center">
  <img src="https://img.shields.io/badge/Language-Python-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Simulation-Software--in--the--Loop-purple?style=for-the-badge" alt="Software in the Loop">
  <img src="https://img.shields.io/badge/Analysis-SciPy%20%7C%20NumPy-orange?style=for-the-badge" alt="Analysis">
  <img src="https://img.shields.io/badge/Visualization-Plotly%20Dash-red?style=for-the-badge" alt="Plotly Dash">
  <img src="https://img.shields.io/badge/Interface-CustomTkinter-green?style=for-the-badge" alt="CustomTkinter">
</p>

---

## Table of Contents

| Section | Description |
|---|---|
| [Overview](#overview) | Project background and purpose |
| [Features](#features) | System validation, steady-state versus transient analysis |
| [System Architecture](#system-architecture) | Software architecture and block diagram |
| [Simulation Model](#simulation-model) | Mathematical modelling of alternator behaviour |
| [Signal Processing and Analysis](#signal-processing-and-analysis) | Filtering, peak detection, ripple and steady-state analysis |
| [Automated Validation](#automated-validation) | Performance criteria and PASS/FAIL evaluation |
| [User Interface and Visualization](#user-interface-and-visualization) | Simulation controls and dashboard |
| [Technologies](#technologies) | Languages and libraries |
| [Getting Started](#getting-started) | Installation and execution |
| [Repository Structure](#repository-structure) | Project organization |
| [Known Limitations](#known-limitations-and-future-development) | Current limitations and planned improvements |
| [References](#references) | Technical references |


---

## Overview

This project is a **software-in-the-loop** automated test bench system that simulates and evaluates the electrical and thermal performance of an automotive alternator. It is modelled after the **Bosch Long Haul High Output Alternator AL9964SB**. 

In the absence of physical hardware, it implements a dynamic simulation layer to model alternator behaviour under user-specified test conditions. From this, the system generates time-series based outputs for performance metrics (voltage, current, and temperature). A real-time interactive dashboard visualizes system behaviour and allows analysis through features such as simulator parameter adjustment, real-time time-series visualization, peak and ripple analysis, and transient versus steady-state detection. Using scientific computing, data processing, and diagnostics, the system replicates **hardware-in-the-loop (HIL)** validation workflows commonly used in test and validation engineering environments (but does not currently interface with a physical alternator, external sensors, or hardware test equipment).

The system follows a modular architecture consisting of four primary layers: the simulation layer, analysis layer, validation layer, and user interface (UI) layer. The UI allows operators to define test conditions and parameters, then presenting these results through interactive graphical displays and diagnostic summaries. The simulation layer models the alternator’s electrical and thermal behaviour over time. The validation layer evaluates these generated outputs against performance metrics derived from the **SAE J56 standard** to identify failures and anomalies. 

The primary objective of this project is to demonstrate how automated test bench systems can improve efficiency in component testing processes. Additionally, the project showcases how preliminary performance validation can be conducted through simulation when physical hardware is unavailable, thus enabling earlier development process.

---

## Features

| Feature | Description |
|---|---|
| Configurable Simulation | Set shaft speed, electrical load, voltage system, and simulation duration. |
| Dynamic System Modelling | Simulate and generate time-series voltage, current, and thermal response data. |
| Signal Processing | Apply Savitzky–Golay filtering to reduce measurement fluctuations. |
| Steady-State Detection | Evaluate signal stability to distinguish transient from steady state behaviours. |
| Ripple Analysis | Quantify steady-state voltage and current fluctuations. |
| Automated Validation | Evaluate measured performance against predefined acceptance criteria. |
| Engineering Dashboard | Visualize simulation response and diagnostic information using interactive real-time plots. |

---

## System Architecture

The software is organized into independent modules, each responsible for a specific stage of the test bench workflow. This structure separates the mathematical model from the analysis and validation logic. Consequently, the simulation model can be modified without requiring the entire application to be rewritten. The main application coordinates communication between the modules and manages the overall simulation process.

![System Architecture](system%20architecture.png)


| Module | Responsibility |
|---|---|
| `main.py` | Application entry point. Coordinates simulation execution, background processing, analysis, validation, and result handling. |
| `simulator.py` | Mathematical simulation engine. Models alternator current generation, voltage regulation, and temperature response based on input shaft speed, electrical load,. |
| `analysis.py` | Processes simulation measurements using filtering, peak detection, steady-state detection, ripple analysis, and current equilibrium calculations. |
| `validation.py` | Evaluates processed simulation results against predefined performance criteria (SAE J56) and generates individual and overall validation statuses. |
| `ui.py` | Implements the graphical interface and interactive dashboard using CustomTkinter and Plotly Dash. |

---

## Simulation Model


The simulation engine approximates the electrical and thermal behaviour of an automotive alternator using mathematical relationships.

The model generates measurements at discrete time intervals, allowing the system's response to be evaluated throughout a simulation.

### 1. Shaft Speed and Electrical Load

The alternator operates under user-defined shaft speed and electrical loading conditions. Small random disturbances are introduced into the operating conditions to represent measurement and operating fluctuations.

$$
\omega(t) = \omega_0 + \eta_\omega(t)
$$

$$
L(t) = L_0 + \eta_L(t)
$$

Where:

- $\omega_0$: Initial shaft speed.
- $L_0$: Initial electrical load.
- $\eta_\omega(t)$: Random shaft-speed disturbance.
- $\eta_L(t)$: Random electrical-load disturbance.

### 2. Current Generation

The generated current depends on shaft speed and electrical loading. The model uses a speed-dependent saturation relationship that represents increasing current availability as shaft speed increases, with output also dependent on the electrical load.

$$
I(t) = I_{\max}
\left(1-e^{-\omega(t)/k_{\text{speed}}}\right)
\frac{L(t)}{100}
$$

Where:

- $I_{\max}$: Maximum model current.
- $\omega(t)$: Instantaneous shaft speed.
- $k_{\text{speed}}$: Shaft-speed response parameter.
- $L(t)$: Electrical load percentage.


### 3. Voltage Regulation

The alternator voltage is modelled using a first-order response. First, a speed-dependent target voltage is calculated:

$$
V_{\text{target}}(t) =
V_{\text{set}}
\left(1-e^{-\omega(t)/k_v}\right)
$$

The actual voltage approaches this target according to:

$$
\frac{dV}{dt} =
\frac{V_{\text{target}}(t)-V(t)}{\tau_v}
$$

Where:

- $V_{\text{set}}$: Selected regulated voltage.
- $k_v$: Voltage response parameter.
- $\tau_v$: Voltage response time constant.
- $V(t)$: Simulated output voltage.

This introduces transient behaviour into the voltage response rather than assuming the output reaches its target instantaneously.

### 4. Thermal Behaviour

Temperature is modelled using a simplified heat-generation and heat-dissipation relationship.

$$\frac{dT}{dt} = k_{\mathrm{heat}} I(t)^2 - k_{\mathrm{cool}}(T-T_{\mathrm{ambient}})$$

Where:

- $T$: Simulated alternator temperature in Kelvin.
- $T_{\text{ambient}}$: Ambient temperature.
- $I(t)$: Generated current.
- $k_{\text{heat}}$: Heat-generation coefficient.
- $k_{\text{cool}}$: Cooling coefficient.

The model accounts for increasing heat generation with electrical current and heat dissipation as the alternator temperature rises above ambient.


### Simulation Outputs

The simulator generates a time-series dataset that is passed to the analysis and validation modules:

| Measurement | Unit | Description |
|---|---|---|
| Time | s | Simulation time |
| Voltage | V | Alternator output voltage |
| Current | A | Generated electrical current |
| Temperature | K | Simulated alternator temperature |
| Shaft Speed | RPM | Instantaneous shaft rotational speed |
| Electrical Load | % | Instantaneous electrical loading |

---

## Signal Processing and Analysis

The analysis layer processes the raw simulation measurements to extract useful information. Instead of evaluating every measurement independently, the analysis module applies signal processing techniques to characterize the system's behaviour over time.

### 1. Signal Filtering

A Savitzky–Golay filter is applied to the measurement signals to reduce small fluctuations while preserving important signal characteristics, such that it can be used for steady-state analysis and ripple calculations.

The filter uses:
- Smoothing window: 10 seconds.
- Polynomial order: 2.

### 2. Steady-State Detection

Steady-state detection determines when a measurement signal satisfies predefined stability conditions by using sliding measurement windows to evaluate signal variation and rate of change.

The detection process considers:
- Signal variation within each measurement window.
- Rate of change over time.
- Multiple consecutive windows satisfying the stability criteria.

This prevents a signal from being classified as stable based on a single momentary period of low variation. Individual steady-state results are evaluated for voltage, current, and temperature.

### 3. Ripple Analysis

Small fluctuations can remain in measurement signals after steady-state operation has been reached.
Ripple analysis quantifies these fluctuations using the standard deviation of the filtered steady-state measurements (current and voltage):

$$
\mathrm{Ripple} = \sigma(x_{\mathrm{steady}})
$$

Where $x_{\mathrm{steady}}$ represents the filtered measurement data within the steady-state region.


### 5. Current Equilibrium Analysis

Current equilibrium is evaluated separately from the general steady-state detection process.

The analysis requires a continuous 300-second (5 minute) current measurement window and evaluates current variation over that interval, as is detailed according to SAE J56 standards. The current equilibrium criterion uses an allowed variation of approximately 2%.

---

## Automated Validation

The validation layer evaluates the processed simulation results against the SAE J65 standard for determination of the electrical characteristic data of alternators for road vehicles.  Each validation function operates independently and returns a structured result containing:
- Validation status.
- Boolean pass/fail value, where applicable.
- Diagnostic message explaining the result.

The system supports three individual validation statuses:

| Status | Meaning |
|---|---|
| PASS | The measurement satisfies the defined acceptance criterion. |
| FAIL | The measurement violates the defined acceptance criterion. |
| NOT TESTED | The required measurement data or operating condition is unavailable. |

### Implemented Validation Criteria

| Validation Check | Acceptance Criterion | Evaluation |
|---|---|---|
| Voltage Regulation | 14.2 ± 0.5 V for 12 V systems; 27.5 ± 0.5 V for 24 V systems. | Evaluates the detected steady-state voltage. |
| Current Equilibrium | Current variation within the allowed approximately 2% limit over a continuous 300-second window. | Uses the current equilibrium result from the analysis layer. |
| Maximum Current Limit | Maximum measured current must not exceed 275 A. | Checks the maximum current in the simulation dataset. |
| Temperature | Steady-state temperature must not exceed 393 K (approximately 120°C). | Evaluates detected steady-state temperature. |
| Voltage Ripple | Voltage ripple must not exceed 0.1 V. | Evaluates steady-state voltage standard deviation. |
| Ambient Temperature | Ambient temperature must be between 18°C and 28°C. | Checks the configured ambient temperature parameter. |


### Overall System Evaluation

After all individual validation checks are completed, the validation module determines the overall system status.

```text
              Evaluate All Checks
                      |
                      v
              Any Result FAIL?
                 /       \
               YES        NO
                |          |
                v          v
              FAIL    Any NOT TESTED?
                          /      \
                        YES       NO
                         |         |
                         v         v
                    INCOMPLETE    PASS
```
---

## User Interface and Visualization

The UI layer provides the operator-facing interface for configuring simulations, monitoring system behaviour, and reviewing analysis and validation results. It combines a CustomTkinter graphical interface with a Plotly Dash engineering dashboard.

### 1. Simulation Control Interface

The CustomTkinter interface provides controls for configuring the simulation.

Users can specify operating conditions such as:

- Initial shaft speed (RPM).
- Electrical load (%).
- Electrical system type (12 V / 24 V).
- Maximum simulation duration.

The interface also manages simulation execution and provides access to the associated visualization dashboard.


### 2. Engineering Data Dashboard

The Plotly Dash dashboard provides interactive time-series visualization of the simulated alternator measurements.

The primary plots display:
- Voltage vs. time.
- Current vs. time.
- Temperature vs. time.

These plots allows examination of transient response, signal fluctuations, and steady-state behaviour.

### 3. Diagnostic and Performance Visualization

The dashboard presents processed information from the analysis and validation modules.

This includes:

- Voltage, current, and temperature response curves.
- Detected steady-state information.
- Voltage and current ripple measurements.
- Current equilibrium information.
- Validation results and overall system status.

Plotly's interactive graph functionality allows users to inspect the simulated measurement data and investigate specific regions of interest.

---

## Libraries Used

| Library | Application |
|---|---|
| NumPy | Numerical calculations and mathematical modelling |
| Pandas | Time-series measurement storage and DataFrame processing |
| SciPy | Signal filtering and peak detection |
| CustomTkinter | Graphical user interface and simulation controls |
| Plotly | Interactive engineering plots and data visualization |
| Dash | Interactive dashboard application |

---

## Getting Started

### Prerequisites

In order to run the project, the following must be installed: 
- Python 3.
- Git.
- A code editor such as Visual Studio Code.
- Python packages: numpy, pandas, scipy, customtkinter, plotly, dash

---

## Testing and Verification

The application can be evaluated by executing simulations under different operating conditions and examining the resulting measurements and validation reports.

### Suggested Manual Test Scenarios

| Test Scenario | Purpose |
|---|---|
| Low Shaft Speed | Examine voltage and current behaviour at reduced rotational speed. |
| High Shaft Speed | Evaluate output behaviour at elevated rotational speed. |
| Low Electrical Load | Examine alternator response under light loading conditions. |
| High Electrical Load | Evaluate current generation and thermal response under increased loading. |
| 12 V System | Verify voltage regulation against the configured 12 V acceptance range. |
| 24 V System | Verify voltage regulation against the configured 24 V acceptance range. |
| Extended Simulation | Examine temperature progression and current equilibrium over longer measurement periods. |

### Verification Workflow

1. Configure the desired simulation conditions through the graphical interface.
2. Execute the simulation.
3. Review the generated voltage, current, temperature, shaft speed, and electrical load measurements.
4. Examine the filtered signals and steady-state detection results.
5. Inspect the individual validation outcomes.
6. Confirm that the overall system status correctly reflects the individual validation results.

---

## Known Limitations and Future Development

The current project provides a software-based simulation and automated evaluation workflow. However, there are several opportunities to improve its physical accuracy, test coverage, and engineering functionality.

### Simulation Improvements

- Incorporate additional physical operating characteristics and parameter identification from manufacturer data.
- Introduce additional transient operating conditions.

### Analysis Improvements

- Implement automated rise-time, overshoot, and settling-time calculations.
- Introduce additional statistical performance indicators.

### Validation Improvements

- Add rated-output capability checks at specified shaft speeds and electrical loads.
- Add automated unit and integration testing.

### Hardware-in-the-Loop Development

The current implementation is software-in-the-loop and does not communicate with physical hardware. A future extension could introduce external sensors, and physical alternator measurements 
to support a Hardware-in-the-Loop (HIL) testing environment. This would allow simulated operating conditions to be compared with measurements from an actual alternator.

---

## References

1. SAE J56 (June 1999): Road Vehicles—Alternators with Regulators—Test Methods and General Requirements.
2. Bosch AL9964SB product brochure: Long Haul High Output Alternator, model AL9964SB.

*The project uses these references to inform its modelling and evaluation approach. It is not a certified implementation of an SAE J56 test procedure.*

---

<p align="center">
  <i>Automotive Alternator Test Bench — Simulation, Analysis, and Automated Validation.</i>
</p>
