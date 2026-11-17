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
| Dynamic System Modelling | Simulate voltage regulation, current generation, and thermal response over time. |
| Measurement Generation | Generate time-series voltage, current, temperature, shaft speed, and electrical load data. |
| Signal Processing | Apply Savitzky–Golay filtering to reduce measurement fluctuations. |
| Steady-State Detection | Evaluate signal stability using sliding measurement windows. |
| Ripple Analysis | Quantify steady-state voltage and current fluctuations. |
| Current Equilibrium Analysis | Evaluate current variation over a continuous measurement window. |
| Automated Validation | Evaluate measured performance against predefined acceptance criteria. |
| Engineering Dashboard | Visualize simulation response and diagnostic information using interactive plots. |
| Graphical User Interface | Configure and execute simulations through a CustomTkinter interface. |
| Modular Architecture | Separate simulation, analysis, validation, and visualization components. |

---

## System Architecture

![Automotive Alternator Test Bench Dashboard](README.md/images/system-architecture.png)


The software is organized into independent modules, each responsible for a specific stage of the test bench workflow.

The main application coordinates communication between the modules and manages the overall simulation process.

### System Workflow

```text
                  USER / OPERATOR
                        |
                        v
              CUSTOMTKINTER GUI
                        |
              Simulation Parameters
                        |
                        v
                 MAIN APPLICATION
                        |
                        v
                SIMULATION ENGINE
                        |
                        v
               RAW MEASUREMENT DATA
                        |
                 Pandas DataFrame
                        |
               +--------+--------+
               |                 |
               v                 v
          ANALYSIS LAYER    VALIDATION LAYER
               |                 |
       +-------+-------+         |
       |       |       |         |
       v       v       v         |
     Filter  Peaks  Steady       |
                    State        |
               |                 |
               +--------+--------+
                        |
                        v
                PROCESSED RESULTS
                        |
                        v
              PLOTLY DASH DASHBOARD
                        |
               +--------+--------+
               |                 |
               v                 v
         RESPONSE PLOTS     DIAGNOSTICS
               |                 |
               +--------+--------+
                        |
                        v
                TEST RESULTS
                 PASS / FAIL /
                 INCOMPLETE
```

### Software Modules

| Module | Responsibility |
|---|---|
| `main.py` | Application entry point. Coordinates simulation execution, background processing, analysis, validation, and result handling. |
| `simulator.py` | Mathematical simulation engine. Models alternator shaft speed, electrical load, current generation, voltage regulation, and temperature response. |
| `analysis.py` | Processes simulation measurements using filtering, peak detection, steady-state detection, ripple analysis, and current equilibrium calculations. |
| `validation.py` | Evaluates processed simulation results against predefined performance limits and generates individual and overall validation statuses. |
| `ui.py` | Implements the graphical interface and interactive dashboard using CustomTkinter and Plotly Dash. |

This modular structure separates the mathematical model from the analysis and validation logic. Consequently, the simulation model can be modified without requiring the entire application to be rewritten.

---

## Simulation Model

The simulation engine approximates the electrical and thermal behaviour of an automotive alternator using mathematical relationships.

The model generates measurements at discrete time intervals, allowing the system's response to be evaluated throughout a simulation.

### 1. Shaft Speed and Electrical Load

The alternator operates under user-defined shaft speed and electrical loading conditions.

Small random disturbances are introduced into the operating conditions to represent measurement and operating fluctuations.

\[
\omega(t)=\omega_0+\eta_\omega(t)
\]

\[
L(t)=L_0+\eta_L(t)
\]

Where:

- \(\omega_0\): Initial shaft speed.
- \(L_0\): Initial electrical load.
- \(\eta_\omega(t)\): Random shaft-speed disturbance.
- \(\eta_L(t)\): Random electrical-load disturbance.

### 2. Current Generation

The generated current depends on shaft speed and electrical loading.

The model uses a speed-dependent saturation relationship:

\[
I(t)=I_{\max}
\left(1-e^{-\omega(t)/k_{\text{speed}}}\right)
\frac{L(t)}{100}
\]

Where:

- \(I_{\max}\): Maximum model current.
- \(\omega(t)\): Instantaneous shaft speed.
- \(k_{\text{speed}}\): Shaft-speed response parameter.
- \(L(t)\): Electrical load percentage.

The model represents increasing current availability as shaft speed increases, with output also dependent on the electrical load.

### 3. Voltage Regulation

The alternator voltage is modelled using a first-order response.

First, a speed-dependent target voltage is calculated:

\[
V_{\text{target}}(t)=V_{\text{set}}
\left(1-e^{-\omega(t)/k_v}\right)
\]

The actual voltage approaches this target according to:

\[
\frac{dV}{dt}=
\frac{V_{\text{target}}(t)-V(t)}{\tau_v}
\]

Where:

- \(V_{\text{set}}\): Selected regulated voltage.
- \(k_v\): Voltage response parameter.
- \(\tau_v\): Voltage response time constant.
- \(V(t)\): Simulated output voltage.

This introduces transient behaviour into the voltage response rather than assuming the output reaches its target instantaneously.

### 4. Thermal Behaviour

Temperature is modelled using a simplified heat-generation and heat-dissipation relationship.

\[
\frac{dT}{dt}
=
k_{\text{heat}}I(t)^2
-
k_{\text{cool}}(T-T_{\text{ambient}})
\]

Where:

- \(T\): Simulated alternator temperature in Kelvin.
- \(T_{\text{ambient}}\): Ambient temperature.
- \(I(t)\): Generated current.
- \(k_{\text{heat}}\): Heat-generation coefficient.
- \(k_{\text{cool}}\): Cooling coefficient.

The model accounts for increasing heat generation with electrical current and heat dissipation as the alternator temperature rises above ambient.

The differential equation is evaluated numerically using a time-stepping approach.

### Simulation Outputs

The simulator generates a time-series dataset containing:

| Measurement | Unit | Description |
|---|---|---|
| Time | s | Simulation time |
| Voltage | V | Alternator output voltage |
| Current | A | Generated electrical current |
| Temperature | K | Simulated alternator temperature |
| Shaft Speed | RPM | Instantaneous shaft rotational speed |
| Electrical Load | % | Instantaneous electrical loading |

The resulting dataset is passed to the analysis and validation modules.

---

## Signal Processing and Analysis

The analysis layer processes the raw simulation measurements to extract useful engineering information.

Instead of evaluating every measurement independently, the analysis module applies signal processing techniques to characterize the system's behaviour over time.

### 1. Signal Filtering

A Savitzky–Golay filter is applied to the measurement signals to reduce small fluctuations while preserving important signal characteristics.

The filter uses:

- Smoothing window: 10 seconds.
- Polynomial order: 2.

This produces filtered measurement signals that can be used for peak detection, steady-state analysis, and ripple calculations.

### 2. Peak Detection

Peak detection is implemented using `scipy.signal.find_peaks`.

Prominence thresholds are used to distinguish significant peaks from smaller fluctuations.

| Signal | Peak Prominence |
|---|---:|
| Voltage | 0.2 V |
| Current | 2 A |
| Temperature | 1 K |

Peak detection provides information about significant local maxima within the simulated measurement signals.

### 3. Steady-State Detection

Steady-state detection determines when a measurement signal satisfies predefined stability conditions.

The analysis uses sliding measurement windows to evaluate signal variation and rate of change.

The detection process considers:

- Signal variation within each measurement window.
- Rate of change over time.
- Multiple consecutive windows satisfying the stability criteria.

This prevents a signal from being classified as stable based on a single momentary period of low variation.

Individual steady-state results are evaluated for voltage, current, and temperature.

### 4. Ripple Analysis

Small fluctuations can remain in measurement signals after steady-state operation has been reached.

Ripple analysis quantifies these fluctuations using the standard deviation of the filtered steady-state measurements:

\[
\text{Ripple}=\sigma(x_{\text{steady}})
\]

Where \(x_{\text{steady}}\) represents the filtered measurement data within the steady-state region.

The current implementation calculates voltage and current ripple.

**Note:** The reported ripple is a standard-deviation measurement, not a peak-to-peak ripple measurement.

### 5. Current Equilibrium Analysis

Current equilibrium is evaluated separately from the general steady-state detection process.

The analysis requires a continuous 300-second current measurement window and evaluates current variation over that interval.

The current equilibrium criterion uses an allowed variation of approximately 2%.

The analysis reports whether the required measurement window was completed, the average current, the measured variation, and whether the equilibrium criterion was satisfied.

---

## Automated Validation

The validation layer evaluates the processed simulation results against predefined acceptance criteria.

Each validation function operates independently and returns a structured result containing:

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

**Important:** The 275 A current check currently verifies that the simulated current does not exceed the configured maximum limit. It does not independently verify that the alternator can deliver 275 A under a specified RPM and load condition.

The criteria are project-defined reference limits informed by the alternator model and engineering references. Their implementation does not establish formal certification or compliance with SAE J56.

### Overall System Evaluation

After all individual validation checks are completed, the validation module determines the overall system status.

The decision logic is:

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

The overall status follows these rules:

- **FAIL:** At least one validation criterion fails.
- **INCOMPLETE:** No criterion fails, but at least one criterion could not be tested.
- **PASS:** All validation criteria pass.

This approach prevents the system from reporting an overall PASS when required measurements are unavailable.

---

## User Interface and Visualization

The UI layer provides the operator-facing interface for configuring simulations, monitoring system behaviour, and reviewing analysis and validation results.

It combines a CustomTkinter graphical interface with a Plotly Dash engineering dashboard.

### 1. Simulation Control Interface

The CustomTkinter interface provides controls for configuring the simulation.

Users can specify operating conditions such as:

- Initial shaft speed (RPM).
- Electrical load (%).
- Electrical system type (12 V / 24 V).
- Maximum simulation duration.

The interface also manages simulation execution and provides access to the associated visualization dashboard.

Background simulation execution helps maintain interface responsiveness while computational processing is performed.

### 2. Engineering Data Dashboard

The Plotly Dash dashboard provides interactive time-series visualization of the simulated alternator measurements.

The primary plots display:

- Voltage vs. time.
- Current vs. time.
- Temperature vs. time.

These plots allow users to examine transient response, identify signal fluctuations, and interpret steady-state behaviour.

### 3. Diagnostic and Performance Visualization

The dashboard presents processed information from the analysis and validation modules.

This includes:

- Voltage, current, and temperature response curves.
- Detected steady-state information.
- Peak detection results.
- Voltage and current ripple measurements.
- Current equilibrium information.
- Validation results and overall system status.

Plotly's interactive graph functionality allows users to inspect the simulated measurement data and investigate specific regions of interest.

### Future Visualization Enhancements

Potential extensions to the dashboard include:

- Automated rise-time, overshoot, and settling-time metrics.
- Shaded steady-state tolerance bands.
- Markers identifying settling points and significant peaks.
- Magnified steady-state ripple visualization panels.
- Diagnostic cards displaying peak count, ripple percentage, and stability metrics.

These enhancements would further develop the dashboard into an engineering-oriented simulation and diagnostic interface.

---

## Technologies

| Technology | Application |
|---|---|
| Python | Main programming language and application development |
| NumPy | Numerical calculations and mathematical modelling |
| Pandas | Time-series measurement storage and DataFrame processing |
| SciPy | Signal filtering and peak detection |
| CustomTkinter | Graphical user interface and simulation controls |
| Plotly | Interactive engineering plots and data visualization |
| Dash | Interactive dashboard application |
| Git | Version control and source code management |
| GitHub | Project repository and version tracking |

---

## Getting Started

### Prerequisites

Before running the project, ensure the following are installed:

- Python 3.
- Git.
- A code editor such as Visual Studio Code.

The project uses Python libraries for numerical simulation, data analysis, and graphical visualization.

### 1. Clone the Repository

Open a terminal and run:

```bash
git clone https://github.com/reianna-r/Automotive-Alternator-Test-Bench..git
```

Navigate into the project directory:

```bash
cd Automotive-Alternator-Test-Bench
```

If the repository's actual folder name differs, use the folder created by Git when cloning.

### 2. Create a Virtual Environment

Creating a virtual environment keeps project dependencies separate from other Python installations.

**Windows:**

```bash
py -m venv venv
```

Activate the environment:

```bash
venv\Scripts\activate
```

**macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

Install the required Python packages:

```bash
python -m pip install numpy pandas scipy customtkinter plotly dash
```

### 4. Run the Application

From the project root directory, execute:

```bash
python main.py
```

On Windows, if the `python` command is unavailable, use:

```bash
py main.py
```

The main application initializes the simulation workflow and graphical interface.

---

## Repository Structure

The project is organized into separate Python modules to maintain a clear separation between simulation, analysis, validation, and visualization.

```text
Automotive-Alternator-Test-Bench/
│
├── main.py
│   └── Application entry point and workflow coordination
│
├── simulator.py
│   └── Alternator mathematical simulation engine
│
├── analysis.py
│   └── Signal processing and performance analysis
│
├── validation.py
│   └── Automated acceptance checks and result evaluation
│
├── ui.py
│   └── CustomTkinter interface and Plotly Dash dashboard
│
├── .gitignore
│
└── README.md
```

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
5. Review peak detection and ripple analysis.
6. Inspect the individual validation outcomes.
7. Confirm that the overall system status correctly reflects the individual validation results.

**Automated test suite:** A dedicated automated unit-test suite is not currently documented as part of this project. The scenarios above describe manual functional verification of the simulation and validation workflow.

---

## Known Limitations and Future Development

The current project provides a software-based simulation and automated evaluation workflow. However, there are several opportunities to improve its physical accuracy, test coverage, and engineering functionality.

### Simulation Improvements

- Develop a more detailed alternator electrical model.
- Incorporate additional physical operating characteristics and parameter identification from manufacturer data.
- Improve the representation of voltage regulator dynamics.
- Introduce additional transient operating conditions.

### Analysis Improvements

- Implement automated rise-time, overshoot, and settling-time calculations.
- Expand ripple analysis to include peak-to-peak measurements.
- Improve steady-state detection for signals with persistent fluctuations.
- Introduce additional statistical performance indicators.

### Validation Improvements

- Add rated-output capability checks at specified shaft speeds and electrical loads.
- Introduce additional transient performance checks.
- Expand acceptance criteria using verified manufacturer specifications and applicable engineering test procedures.
- Add automated unit and integration testing.

### Hardware-in-the-Loop Development

The current implementation is software-based and does not communicate with physical hardware.

A future extension could introduce external sensors, data acquisition hardware, and physical alternator measurements to support a Hardware-in-the-Loop (HIL) testing environment.

This would allow simulated operating conditions to be compared with measurements from an actual alternator and provide a pathway toward hardware-based verification.

---

## Engineering References

The project was developed with reference to the following engineering materials and concepts:

1. **Bosch Long Haul High Output Alternator AL9964SB** — Reference alternator model.
2. **SAE J56** — Automotive alternator performance testing reference.
3. **Control Systems Engineering Concepts** — First-order system response, transient behaviour, and steady-state performance.
4. **Numerical Methods** — Numerical integration and time-stepping methods.
5. **Signal Processing** — Savitzky–Golay filtering, peak detection, and statistical signal analysis.

*The project uses these references to inform its modelling and evaluation approach. It is not a certified implementation of an SAE J56 test procedure.*

---

<p align="center">
  <i>Automotive Alternator Test Bench — Simulation, Analysis, and Automated Validation.</i>
</p>
