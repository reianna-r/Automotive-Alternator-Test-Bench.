'''
MAIN LAYER
==============================
This module acts as the central controller for the automotive alternator 
test bench system by coordinating the simulator, validation, and 
graphical user interface layers.
'''

from simulator import Simulator
from validation import evaluate_system
from ui import Interface


def main():
    sim = Simulator()

    app = Interface(sim, evaluate_system)
    app.run()

# ensures program only launches when this file is directly run
if __name__ == "__main__": 
    main()