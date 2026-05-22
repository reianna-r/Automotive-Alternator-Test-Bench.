'''
USER INTERFACE LAYER
==============================
This module is responsible for managing the graphical user interface (GUI)
of the system. It provides an environment for users to input test parameters, 
initiate simulations, view status indicators, as well as numerical and visual
outputs where applicable. It acts as the presentation layer and does not 
contain any core logic, thus ensuring that any updates to the simulation or
validation modules do not disrupt the interface.
'''


import customtkinter as ctk


class Interface:
    '''
    Graphical user interface layer that connects user inputs to the simulator
    and validator, and displays computed results in real time.

    Inputs:
        simulator (object): Simulation engine that computes electrical and thermal
            performance of the alternator system.

        evaluate_system (function): Validation function that evaluates simulation
            outputs against SAE J56 standards and returns PASS/FAIL results.

    Outputs:
        GUI window (CTk root): Interactive interface containing:
            - Input controls (RPM, load, system type)
            - Simulation trigger button
            - Graphical display  
            - Output console with simulation + validation results
            - System status indicator (PASS/FAIL)
    '''

    def __init__(self, simulator, evaluate_system):
        self.sim = simulator
        self.evaluate_system = evaluate_system  

        # configure global appearance settings
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.root = ctk.CTk() # main application window
        self.root.title("Automotive Alternator Test Bench")
        self.root.geometry("1920x1080")
        self.root.configure(fg_color="#0B0F19")

        # registers validation commands (converts Python methods into a format Tkinter can call)
        self.speed_validator = self.root.register(self.validate_speed)
        self.load_validator = self.root.register(self.validate_load)



## --------------------TITLE AND SUBTITLE CONFIGURATION --------------------
        # creating a header frame
        self.title_frame = ctk.CTkFrame(
            self.root,
            height=90,
            corner_radius=0,          
            fg_color="#111827")        

        self.title_frame.pack( side="top", fill="x") # setting header frame orientation 
        self.title_frame.pack_propagate(False) # prevents header frame from shrinking


        # container for left-aligned title and subtitle
        self.header_text_frame = ctk.CTkFrame(
            self.title_frame,
            fg_color="transparent")     
        
        self.header_text_frame.pack(side="left", padx=30, pady=10)


        # creating a title label inside the container
        self.title = ctk.CTkLabel(
            self.header_text_frame,
            text="AUTOMOTIVE ALTERNATOR TEST BENCH",
            font=ctk.CTkFont(size=30, weight="bold"),
            text_color="#FFFFFF",
            anchor="w")
        
        self.title.pack(anchor="w") # place the title with left alignment


        # creating a subtitle label inside the container
        self.subtitle = ctk.CTkLabel(
            self.header_text_frame,
            text="Performance Evaluation of Bosch AL9964SB Alternator Under SAE-J56 Test Conditions",
            font=ctk.CTkFont(size=14),
            text_color="#AAB4C5",
            anchor="w")
        
        self.subtitle.pack(anchor="w")



## --------------------RESTART AND PAUSE BUTTON CONFIGURATION --------------------
        # container for restart and pause buttons (inside header frame)
        self.header_button_frame = ctk.CTkFrame(
            self.title_frame,
            fg_color="transparent")
        
        self.header_button_frame.pack(side="right", padx=30)


        # restart button 
        self.restart_btn = ctk.CTkButton(
            self.header_button_frame,
            text="⟳ Restart",
            width=120,
            height=40,
            corner_radius=12,
            fg_color="#00E5FF",
            hover_color="#00B8CC",
            text_color="#0B0F19",
            command=lambda: None)
        
        self.restart_btn.pack(side="left", padx=10)


        # pause button
        self.pause_btn = ctk.CTkButton(
            self.header_button_frame,
            text="⏸ Pause",
            width=120,
            height=40,
            corner_radius=12,
            fg_color="#374151",
            hover_color="#4B5563",
            text_color="#FFFFFF",
            command=lambda: None)
        
        self.pause_btn.pack(side="left", padx=10)



## --------------------INPUT CONFIGURATION --------------------
        # container below the header; holds input panel, graph display area, output 
        self.body_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.body_frame.pack(fill="both", expand=True)

        # configure such that input panel size is fixed and main display expands to fill the horizontal
        self.body_frame.grid_columnconfigure(0, weight=0)
        self.body_frame.grid_columnconfigure(1, weight=1)

        # configure such that graph area takes most vertical space and output area expands proportionally
        self.body_frame.grid_rowconfigure(0, weight=5)
        self.body_frame.grid_rowconfigure(1, weight=1)

        
        # creating an input information (RPM, load, system type) frame
        self.input_frame = ctk.CTkFrame(
            self.body_frame,
            width=320,
            corner_radius=18,
            fg_color="#111827")
            
        # ensures the left-side input panel spans full screen  height
        self.input_frame.grid(
            row=0,
            column=0,
            rowspan=2,
            sticky="ns",
            padx=(20, 10),
            pady=20)


        # configure column sizing inside the input frame
        self.input_frame.columnconfigure(0, weight=1)
        self.input_frame.columnconfigure(1, weight=2)



## --------------------SHAFT SPEED BUTTON CONFIGURATION --------------------
        # defining a label style for speed, load, and system buttons
        label_style = {
            "font": ctk.CTkFont(size=13, weight="bold"),
            "text_color": "#D1D5DB"}

        # defining a shaft speed label describing the shaft speed input field (not interactive)
        speed_label = ctk.CTkLabel(
            self.input_frame,
            text="Shaft Speed (RPM)",
            **label_style)

        # places the label in the grid layout
        speed_label.grid(
            row=0, column=0,
            padx=15, pady=12,
            sticky="w")

        # creates an input field where the user enters shaft speed + visual hint of valid input range
        self.speed_entry = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="0 - 18000",
            corner_radius=10,
            validate="key",
            validatecommand=(self.speed_validator, "%P"))

        # places input field next to the label in the same row + allows horizontally expansion
        self.speed_entry.grid(
            row=0, column=1,
            padx=15, pady=12,
            sticky="ew")



## --------------------ELECTRICAL LOAD BUTTON CONFIGURATION --------------------
        # defining an electrical load label describing the load input field (not interactive)
        load_label = ctk.CTkLabel(
            self.input_frame,
            text="Electrical Load (%)",
            **label_style)

        # places the label in the grid layout
        load_label.grid(
            row=1, column=0,
            padx=15, pady=12,
            sticky="w")

        # creates an input field where the user enters electrical load + visual hint of valid input range
        self.load_entry = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="0 - 100",
            corner_radius=10,
            validate="key",
            validatecommand=(self.load_validator, "%P"))

        # places input field next to the label in the same row + allows horizontal expansion
        self.load_entry.grid(
            row=1, column=1,
            padx=15, pady=12,
            sticky="ew")



## --------------------SYSTEM TYPE BUTTON CONFIGURATION--------------------
        # defining a system type label describing the system voltage selection field (not interactive)
        system_label = ctk.CTkLabel(
            self.input_frame,
            text="System Type",
            **label_style)

        # places the label in the grid layout
        system_label.grid(
            row=2, column=0,
            padx=15, pady=12,
            sticky="w")

        # creates a dropdown selection for system type (12V or 24V only)
        self.system_entry = ctk.CTkComboBox(
            self.input_frame,
            values=["12", "24"],
            state="readonly", # prevents manual typing and forces dropdown selection only 
            corner_radius=10,
            button_color="#00E5FF",
            button_hover_color="#00B8CC")

        # places dropdown next to the label in the same row + allows horizontal expansion
        self.system_entry.grid(
            row=2, column=1,
            padx=15, pady=12,
            sticky="ew")

        # sets default system type to 12V
        self.system_entry.set("12")
        


        ## --------------------RUN SIMULATION BUTTON--------------------
        # creates a button that executes the simulation using the entered parameters
        self.run_button = ctk.CTkButton(
            self.input_frame,
            text="Run Simulation",
            height=45,
            corner_radius=12,
            fg_color="#00E5FF",
            hover_color="#00B8CC",
            text_color="#0B0F19",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.run_simulation)

        # places the run button below all input controls
        self.run_button.grid(
            row=3,
            column=0,
            columnspan=2,
            padx=15,
            pady=(25, 15),
            sticky="ew")



## --------------------GRAPH DISPLAY FRAME--------------------
     # creating the graph display frame
        self.graph_frame = ctk.CTkFrame(
            self.body_frame,
            corner_radius=18,
            fg_color="#111827")

        # grid layout configuration
        self.graph_frame.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(10, 20),
            pady=(20, 10))



## --------------------OUTPUT FRAME--------------------
        # creating the output frame that displays simulation and validation results
        self.output_frame = ctk.CTkFrame(
            self.body_frame,
            corner_radius=18,
            fg_color="#111827",
            height=170)
    


## --------------------OUTPUT FRAME--------------------
        #grid layout configuration
        self.output_frame.grid(
            row=1,
            column=1,
            sticky="ew",
            padx=(10, 20),
            pady=(10, 20))
        
        self.output_frame.grid_columnconfigure(0, weight=1)

        # creates a scrollable text box used to display simulation and system status
        self.output = ctk.CTkTextbox(
            self.output_frame,
            corner_radius=16,
            fg_color="#0F172A",
            text_color="#E5E7EB",
            font=ctk.CTkFont(family="Consolas", size=12))
        
        self.output.pack(fill="both", expand=True, padx=15, pady=15)


## --------------------INPUT VALIDATION FUNCTIONS--------------------
    def validate_speed(self, value):
        # allow empty field
        if value == "":
            return True

        # only digits allowed
        if not value.isdigit():
            return False

        number = int(value)
        return 0 <= number <= 18000


    def validate_load(self, value):
        # allow empty field
        if value == "":
            return True

        # only digits allowed
        if not value.isdigit():
            return False

        number = int(value)
        return 0 <= number <= 100


## --------------------FINAL--------------------
    def run_simulation(self):
        
        shaft_speed = float(self.speed_entry.get())
        electrical_load = float(self.load_entry.get())
        system_type = int(self.system_entry.get())

        self.sim.shaft_speed = shaft_speed
        self.sim.electrical_load = electrical_load
        self.sim.system_type = system_type

        current = self.sim.compute_current()
        temperature = self.sim.compute_temperature()
        voltage = self.sim.compute_voltage()

        results = self.evaluate_system(
            system_type,
            voltage,
            voltage - 0.2,
            shaft_speed,
            current,
            20,
            80,
            1200,
            [current * 0.99, current, current * 1.01],
            temperature,
            voltage + 1,
            16 if system_type == 12 else 32)

        self.output.delete("1.0", "end")

        self._write("=== SIMULATION RESULTS ===")
        self._write(f"Current      : {current:.2f} A")
        self._write(f"Voltage      : {voltage:.2f} V")
        self._write(f"Temperature  : {temperature:.2f} °C\n")

        self._write("=== VALIDATION RESULTS ===")
        self._write(f"Voltage OK   : {results['voltage']['voltage_ok']}")
        self._write(f"Line Drop OK : {results['voltage']['line_drop_ok']}")
        self._write(f"Idle Current : {results['current']['idle_ok']}")
        self._write(f"Rated Current: {results['current']['rated_ok']}")
        self._write(f"Thermal OK   : {results['thermal_ok']}")
        self._write(f"Ambient OK   : {results['ambient_ok']}")
        self._write(f"Load Dump OK : {results['load_dump_ok']}\n")

        status = "PASS" if results["overall_ok"] else "FAIL"
        self._write(f"=== OVERALL STATUS ===\n{status}")

    def _write(self, text):
        self.output.insert("end", text + "\n")

    def run(self):
        self.root.mainloop()