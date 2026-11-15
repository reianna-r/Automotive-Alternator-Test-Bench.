
'''
USER INTERFACE LAYER
==============================
This layer provides the user interface for the automotive alternator test bench. CustomTkinter manages user 
inputs and simulation controls. Plotly Dash provides interactive, continuously updating graphs.The interface connects to 
the Simulator and Analysis layers without
containing their underlying calculation logic.
'''

import customtkinter as ctk
import threading
import time
import webbrowser
import numpy as np

from dash import Dash, dcc, html, Input, Output
from plotly.subplots import make_subplots
import plotly.graph_objects as go

from simulator import Simulator
from analysis import Analysis
from validation import Validation


class Interface:
    def __init__(self, simulator):
        '''Manages the user interface and connects it to the alternator simulator.'''
        self.sim = simulator

        ## --------------------SHARED SIMULATION DATA--------------------
        self.lock = threading.Lock()
        self.data = {
            "time": [],
            "voltage": [],
            "current": [],
            "temperature": [],
            "speed": [],
            "load": [],
            "steady_time": None,
            "running": False,
            "status": "Waiting for simulation"}
        self.dash_started = False


        ## --------------------CUSTOMTKINTER AND PLOTLY DASH CONFIGURATION--------------------
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.root = ctk.CTk()
        self.root.title("Automotive Alternator Test Bench")
        self.root.geometry("1100x700")
        self.root.configure(fg_color="#142B45")
        self.build_interface()
        self.build_dashboard()


    ## --------------------CUSTOMTKINTER INTERFACE--------------------
    def build_interface(self):
        '''Creates and arranges the main CustomTkinter interface.'''
        header = ctk.CTkFrame(
            self.root,
            height=100,
            corner_radius=0,
            fg_color="#1E4266")

        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="AUTOMOTIVE ALTERNATOR TEST BENCH",
            font=ctk.CTkFont(size=27, weight="bold"),
            text_color="#F1F6FB"
        ).pack(pady=(18, 5))

        ctk.CTkLabel(
            header,
            text="Bosch AL9964SB | SAE J56 Performance Evaluation",
            font=ctk.CTkFont(size=14),
            text_color="#C4D6E6"
        ).pack()

        body = ctk.CTkFrame(
            self.root,
            fg_color="transparent")

        body.pack(fill="both", expand=True, padx=25, pady=25)

        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=2)
        body.grid_rowconfigure(0, weight=1)

        # create the input panel
        self.input_frame = ctk.CTkFrame(body, corner_radius=18, fg_color="#203D5B")
        self.input_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        self.input_frame.columnconfigure(0, weight=1)

        # define a shared style for input labels
        label_style = {"font": ctk.CTkFont(size=14, weight="bold"), "text_color": "#EAF2F8"}

        # register input validation functions
        speed_validation = self.root.register(lambda value: self.validate_input(value, 18000))
        load_validation = self.root.register(lambda value: self.validate_input(value, 100))
        duration_validation = self.root.register(lambda value: self.validate_input(value, 500))

        # shaft speed input
        ctk.CTkLabel(self.input_frame, text="Shaft Speed (RPM)", **label_style).pack(anchor="w", padx=20, pady=(30, 5))
        
        self.speed_entry = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="0 - 18000",
            height=40,
            fg_color="#142B45",
            border_color="#54799B",
            text_color="#F1F6FB",
            placeholder_text_color="#A9BED1")

        self.speed_entry.pack(fill="x", padx=20)
        self.speed_entry.configure(validate="key", validatecommand=(speed_validation, "%P"))

        # electrical load input
        ctk.CTkLabel(
            self.input_frame,
            text="Electrical Load (%)",
            **label_style
        ).pack(anchor="w", padx=20, pady=(20, 5))

        self.load_entry = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="0 - 100",
            height=40,
            fg_color="#142B45",
            border_color="#54799B",
            text_color="#F1F6FB",
            placeholder_text_color="#A9BED1")

        self.load_entry.pack(fill="x", padx=20)
        self.load_entry.configure(validate="key", validatecommand=(load_validation, "%P"))

        # electrical system type selection
        ctk.CTkLabel(self.input_frame, text="System Type", **label_style).pack(anchor="w", padx=20, pady=(20, 5))
        self.system_entry = ctk.CTkComboBox(self.input_frame, values=["12", "24"], state="readonly", height=40)
        self.system_entry.pack(fill="x", padx=20)
        self.system_entry.set("12")

        # maximum simulation duration input
        ctk.CTkLabel(self.input_frame, text="Maximum Simulation Time (s)", **label_style).pack(anchor="w", padx=20, pady=(20, 5))

        self.duration_entry = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="300 - 500 seconds",
            height=40,
            fg_color="#142B45",
            border_color="#54799B",
            text_color="#F1F6FB",
            placeholder_text_color="#A9BED1")

        self.duration_entry.pack(fill="x", padx=20)
        self.duration_entry.insert(0, "500")

        self.duration_entry.configure(
            validate="key",
            validatecommand=(duration_validation, "%P"))

        # run simulation button
        self.run_button = ctk.CTkButton(
            self.input_frame,
            text="RUN SIMULATION",
            height=48,
            corner_radius=12,
            fg_color="#2878B5",
            hover_color="#3679A8",
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self.run_simulation)
        self.run_button.pack(fill="x", padx=20, pady=(35, 12))

        # open Plotly dashboard button
        self.dashboard_button = ctk.CTkButton(
            self.input_frame,
            text="OPEN PLOTLY DASHBOARD",
            height=42,
            corner_radius=12,
            command=self.open_dashboard,
            fg_color="#345A7D",
            hover_color="#426F94",
            text_color="#FFFFFF",
            border_color="#54799B",
            border_width=1)

        self.dashboard_button.pack(fill="x", padx=20, pady=10)

        # simulation status indicator
        self.status_label = ctk.CTkLabel(
            self.input_frame,
            text="STATUS: WAITING",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#F3E3D0")

        self.status_label.pack(pady=25)

        # create the simulation output panel
        self.output_frame = ctk.CTkFrame(
            body,
            corner_radius=18,
            fg_color="#24364B")
        self.output_frame.grid(row=0, column=1, sticky="nsew")

        # output panel heading
        ctk.CTkLabel(
            self.output_frame,
            text="SIMULATION OUTPUT",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#A9D0F0"
        ).pack(anchor="w", padx=20, pady=20)

        # textbox for displaying simulation and validation results
        self.output = ctk.CTkTextbox(
            self.output_frame,
            fg_color="#142B45",
            text_color="#EAF2F8",
            border_color="#54799B",
            border_width=1,
            font=ctk.CTkFont(family="Consolas", size=13))

        self.output.pack(fill="both", expand=True, padx=20, pady=(0, 20))


    ## --------------------PLOTLY DASHBOARD--------------------
    def build_dashboard(self):
        '''Creates the Plotly Dash dashboard for live simulation data visualization.'''
        
        self.app = Dash(__name__, title="Alternator Test Bench Dashboard")

        self.app.layout = html.Div(
            style={
                "backgroundColor": "#0B0F19",
                "minHeight": "100vh",
                "padding": "20px",
                "color": "#F3E3D0",
                "fontFamily": "Arial"},

            children=[html.H1("AUTOMOTIVE ALTERNATOR TEST BENCH", style={"textAlign": "center", "color": "#00E5FF"}),
                # live numerical outputs
                html.Div(
                    id="live-values",
                    style={"display": "flex", "justifyContent": "space-around", "flexWrap": "wrap", "gap": "15px", "margin": "25px 0"}),

                # interactive graphs
                dcc.Graph(id="live-graph", config={"scrollZoom": True, "displayModeBar": True, "responsive": True}, style={"height": "850px"}),

                # automatic graph refresh
                dcc.Interval(id="graph-refresh", interval=250, n_intervals=0)])

        # dash callback (updates graph every 250 milliseconds)
        @self.app.callback(Output("live-graph", "figure"), Output("live-values", "children"), Input("graph-refresh", "n_intervals"))

        def update_dashboard(n):
            '''Updates the Plotly dashboard with the latest simulation data.'''
            with self.lock:
                times = self.data["time"].copy()
                voltages = self.data["voltage"].copy()
                currents = self.data["current"].copy()
                temperatures = self.data["temperature"].copy()
                steady_time = self.data["steady_time"]
                status = self.data["status"]

            # create subplots
            fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.10, subplot_titles=(
                    "Voltage Response",
                    "Current Response",
                    "Thermal Response"))

            # voltage graph
            fig.add_trace(
                go.Scatter(x=times, y=voltages, mode="lines", name="Voltage", line=dict(color="#00E5FF",width=2)), 
                row=1, 
                col=1)

            # current graph
            fig.add_trace(
                go.Scatter(x=times, y=currents, mode="lines", name="Current", line=dict(color="#F59E0B", width=2)),
                row=2,
                col=1)

            # temperature graph (must also convert Kelvin to Celsius for display)
            temperatures_C = [
                temp - 273.15 for temp in temperatures]

            fig.add_trace(
                go.Scatter(x=times, y=temperatures_C, mode="lines", name="Temperature", line=dict(color="#F87171", width=2)),
                row=3,
                col=1)

            # graph formatting
            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="#0B0F19",
                plot_bgcolor="#111827",
                font=dict(color="#E5E7EB"),
                title=dict(text=f"Alternator Response | {status}", x=0.5),
                hovermode="x unified",
                margin=dict(l=80, r=40, t=100, b=60),
                legend=dict(orientation="h", y=1.04, x=0))
            
            fig.update_yaxes(title_text="Voltage (V)", row=1, col=1)
            fig.update_yaxes(title_text="Current (A)", row=2, col=1)
            fig.update_yaxes(title_text="Temperature (°C)", row=3, col=1)
            fig.update_xaxes(title_text="Time (seconds)", row=3, col=1)

            # live numerical outputs
            if times:
                latest_v = voltages[-1]
                latest_i = currents[-1]
                latest_t = temperatures_C[-1]
                latest_time = times[-1]

            else:
                latest_v = 0
                latest_i = 0
                latest_t = 0
                latest_time = 0

            def metric(title, value, unit):
                return html.Div(
                    style={
                        "backgroundColor": "#1E293B",
                        "padding": "20px",
                        "borderRadius": "12px",
                        "minWidth": "150px",
                        "textAlign": "center"},

                    children=[html.P(title, style={"color": "#94A3B8", "fontSize": "14px"}), html.H2(f"{value:.2f} {unit}", style={"color": "#00E5FF"})])

            values = [
                metric("OUTPUT VOLTAGE", latest_v, "V"),
                metric("OUTPUT CURRENT", latest_i, "A"),
                metric("TEMPERATURE", latest_t, "°C"),
                metric("SIMULATION TIME", latest_time, "s")]

            return fig, values


    ## --------------------START PLOTLY SERVER--------------------
    def open_dashboard(self):
        '''Opens the Plotly Dash dashboard in a web browser. Starts the server if it is not already running.'''
        if not self.dash_started:
            self.dash_started = True
            threading.Thread(
                target=lambda: self.app.run(host="127.0.0.1", port=8050, debug=False, use_reloader=False),
                daemon=True
            ).start()

            self.root.after(1000, lambda: webbrowser.open("http://127.0.0.1:8050"))

        else:
            webbrowser.open("http://127.0.0.1:8050")


    ## --------------------RUN SIMULATION --------------------
    def run_simulation(self):
        '''Validates user inputs, updates simulator parameters, and starts the simulation in a background thread.'''
        try:
            shaft_speed = float(self.speed_entry.get())
            electrical_load = float(self.load_entry.get())
            system_type = int(self.system_entry.get())
            simulation_time = float(self.duration_entry.get())

            # input validation
            if not 0 <= shaft_speed <= 18000:
                raise ValueError("RPM must be between 0 and 18000.")

            if not 0 <= electrical_load <= 100:
                raise ValueError("Load must be between 0 and 100%.")

            if system_type not in (12, 24):
                raise ValueError("System must be 12V or 24V.")

            if not 300 <= simulation_time <= 500:
                raise ValueError(
                    "Simulation time must be between 300 and 500 seconds.")

        except ValueError as error:
            self.output.insert("end", f"INPUT ERROR: {error}\n")
            return

        # update simulator parameters   
        self.sim.base_shaft_speed = shaft_speed
        self.sim.base_electrical_load = electrical_load
        self.sim.v_reg = (14.2 if system_type == 12 else 27.5)

        # reset dashboard data
        with self.lock:
            self.data = {
                "time": [],
                "voltage": [],
                "current": [],
                "temperature": [],
                "speed": [],
                "load": [],
                "steady_time": None,
                "running": True,
                "status": "RUNNING"}

        self.output.delete("1.0", "end")
        self.output.insert("end", "SIMULATION STARTED\n\n")

        self.output.insert(
            "end",
            f"System Type: {system_type}V\n"
            f"Shaft Speed: {shaft_speed} RPM\n"
            f"Electrical Load: {electrical_load}%\n"
            f"Maximum Duration: {simulation_time} s\n\n")

        self.status_label.configure(
            text="STATUS: RUNNING",
            text_color="#F59E0B")

        self.run_button.configure(
            state="disabled",
            text="SIMULATION RUNNING...")

        # open dashboard automatically
        self.open_dashboard()

        # run simulation in background
        threading.Thread(
            target=self.simulation_worker,
            args=(simulation_time, system_type),
            daemon=True).start()


    ## --------------------BACKGROUND SIMULATION WORKER-------------------
    def simulation_worker(self, simulation_time, system_type):
        '''Runs the simulation, analysis, and validation in a separate thread to keep the UI responsive.'''
        try:
            self.sim.initialize_state()
            steps = int(round(simulation_time / self.sim.time_step)) + 1
            steady_detected = False

            # simulation loop
            for step in range(steps):
                current_time = (step * self.sim.time_step)

                if step > 0:
                    self.sim.update_operating_conditions()

                # calculate system outputs
                self.sim.compute_current()
                self.sim.compute_temperature()
                self.sim.compute_voltage()

                self.sim.store_timestep(current_time) # store simulation data

                with self.lock: # udpate live dashboard data
                    self.data["time"].append(current_time)
                    self.data["voltage"].append(self.sim.voltage)
                    self.data["current"].append(self.sim.current)
                    self.data["temperature"].append(self.sim.temperature)
                    self.data["speed"].append(self.sim.shaft_speed)
                    self.data["load"].append(self.sim.electrical_load)

                time.sleep(0.03) # control playback speed (0.03 s of real time per simulated timestep)


            results = self.sim.build_dataframe() # build final DataFrame

            analysis_engine = Analysis(
                results_df=results,
                time_step=self.sim.time_step)

            analysis_report = analysis_engine.process_all()

            # run validation using raw simulation data and analysis results
            validation_engine = Validation(
                results_df=results,
                analysis_results=analysis_report,
                system_type=system_type,
                ambient_temp_k=self.sim.t_ambient)

            validation_report = validation_engine.evaluate_system()
            steady_state = analysis_report["steady_state"]

            # use the Analysis layer's steady-state detection result for the graph marker
            if steady_state["steady_state_found"]:
                steady_index = (steady_state["steady_state_start_index"])
                steady_time = results["Time"].iloc[steady_index]
            else:
                steady_time = None
            
            # update dashboard status
            with self.lock:
                self.data["steady_time"] = steady_time
                self.data["running"] = False
                self.data["status"] = validation_report["overall_status"]

            # display final results in CustomTkinter
            self.root.after(0,
                lambda: self.display_results(
                    results,
                    analysis_report,
                    steady_detected,
                    validation_report))
        
        except Exception as error:
            with self.lock:
                self.data["running"] = False
                self.data["status"] = "ERROR"
            self.root.after(0, lambda error=error: self.display_error(error))


   ## --------------------DISPLAY ANALYSIS AND VALIDATION RESULTS--------------------
    def display_results(self, results, analysis_report, steady_detected, validation_report):
        '''Displays the final simulation, analysis, and validation results in the CustomTkinter output panel.'''
        self.output.insert(
            "end",
            "\n================================\n"
            "SIMULATION COMPLETE\n"
            "================================\n")

        self.output.insert(
            "end",
            f"Samples Generated: {len(results)}\n"
            f"Final Simulation Time: "
            f"{results['Time'].iloc[-1]:.2f} s\n")


        ## --------------------INDVIUDAL VOLTAGE AND TEMPERATURE STEADY STATE ANALYSIS--------------------
        steady = analysis_report["steady_state"]
        individual = steady["individual_steady_states"]

        self.output.insert(
            "end",
            "\n================================\n"
            "STEADY-STATE ANALYSIS\n"
            "================================\n")

        for signal, result in individual.items():
            self.output.insert(
                "end",
                f"\n{signal.upper()}\n")

            if result["steady_state_found"]:
                start_time = results["Time"].iloc[
                    result["start_index"]]

                self.output.insert(
                    "end",
                    "Result: STEADY\n"
                    f"Steady-State Start Time: {start_time:.2f} s\n"
                    f"Average Value: {result['steady_value']:.4f}\n")

            else:
                self.output.insert(
                    "end",
                    "Result: NOT DETECTED\n")


        ## --------------------OVERAL STEADY STATE--------------------
        if steady["steady_state_found"]:

            self.output.insert(
                "end",
                "\nOverall Voltage/Temperature Steady State: DETECTED\n"
                f"Steady Voltage: {steady['steady_voltage']:.2f} V\n"
                f"Steady Temperature: "
                f"{steady['steady_temperature'] - 273.15:.2f} C\n")

        else:
            self.output.insert(
                "end",
                "\nOverall Voltage/Temperature Steady State: "
                "NOT DETECTED\n")


        ## --------------------CURRENT EQUILIBIRUM ANALYSIS--------------------
        current_result = analysis_report["current_equilibrium"]

        self.output.insert(
            "end",
            "\n================================\n"
            "CURRENT ANALYSIS\n"
            "================================\n")

        if not current_result["test_completed"]:
            self.output.insert(
                "end",
                "Result: NOT TESTED\n"
                "Reason: Insufficient data for a continuous "
                "300-second measurement window.\n")

        elif current_result["average_current"] is None:
            self.output.insert(
                "end",
                "Result: NOT TESTED\n"
                "Reason: Current is zero or unavailable.\n")

        else:
            equilibrium_status = ("PASS" if current_result["equilibrium_reached"] else "FAIL")

            self.output.insert(
                "end",
                f"Result: {equilibrium_status}\n"
                f"Measured Variation: "
                f"{current_result['variation_percent']:.2f}%\n"
                f"Maximum Allowed Variation: "
                f"{current_result['allowed_variation_percent']:.2f}%\n"
                f"Average Current: "
                f"{current_result['average_current']:.2f} A\n"
                f"Minimum Current: "
                f"{current_result['minimum_current']:.2f} A\n"
                f"Maximum Current: "
                f"{current_result['maximum_current']:.2f} A\n")


        ## --------------------RIPPLE ANALYSIS-------------------- 
        self.output.insert(
            "end",
            "\n================================\n"
            "RIPPLE ANALYSIS\n"
            "================================\n")

        for key, value in analysis_report["ripple"].items():
            self.output.insert(
                "end",
                f"{key}: {value}\n")


        ## --------------------SYSTEM VALIDATION RESULTS--------------------  
        self.output.insert(
            "end",
            "\n================================\n"
            "SYSTEM VALIDATION RESULTS\n"
            "================================\n")

        for test_name, result in validation_report.items():
            if test_name == "overall_status":
                continue

            self.output.insert(
                "end",
                f"\n{test_name.replace('_', ' ').upper()}\n"
                f"Result: {result['status']}\n"
                f"Details: {result['message']}\n")


        ## --------------------FINAL SYSTEM RESULT--------------------  
        overall_status = validation_report["overall_status"]
        self.output.insert(
            "end",
            "\n================================\n"
            f"FINAL TEST RESULT: {overall_status}\n"
            "================================\n")

        if overall_status == "PASS":
            self.status_label.configure(text="STATUS: PASS", text_color="#10B981")

        elif overall_status == "FAIL":
            self.status_label.configure(text="STATUS: FAIL", text_color="#EF4444")

        else:
            self.status_label.configure(text="STATUS: INCOMPLETE", text_color="#F59E0B")

        self.run_button.configure(state="normal", text="RUN SIMULATION")


    ## --------------------ERROR DISPLAY--------------------  
    def display_error(self, error):
        '''Displays an error message in the output panel and updates the status label.'''
        self.output.insert("end", f"\nSIMULATION ERROR:\n{error}\n")
        self.status_label.configure(text="STATUS: ERROR", text_color="#EF4444")
        self.run_button.configure(state="normal", text="RUN SIMULATION")


    ## --------------------INPUT VALIDATION--------------------    
    def validate_input(self, value, maximum, minimum=0):
        '''Validates the user input parameters for the simulation. 
        Ensures that the input is a number and within the specified range.'''
        if value == "": # allow an empty box while user is typing
            return True

        # only allow numerical values.
        try:
            number = float(value)
        except ValueError:
            return False

        return minimum <= number <= maximum # prevent values outside the allowed range


    ## --------------------RUN UI--------------------  
    def run(self):
        self.root.mainloop()
