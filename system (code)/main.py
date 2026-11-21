
'''
MAIN LAYER
==============================
This layer coordinates the simulator and user interface.
'''
from simulator import Simulator
from ui import Interface

def main():
    sim = Simulator()
    app = Interface(sim)
    app.run()

if __name__ == "__main__":
    main()
