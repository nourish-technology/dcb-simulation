import time
from typing import List, Optional

"""
Simulator for the DCB

Open Questions:

-Should low IO be simulated, or just higher level dispenser/actuator abstractions?
-If also sumulating low level IO, should it be changed when dispenser pour is called?
-How to simulate digital_in change?
-How best simulate actuator move? Takes arbitrary amout of time...

"""


DELIMITER = '\n'

class Dispenser(object):
    def __init__(self, id: int, timeout_ms: int = 1000):
        self.id: int = id
        self.timeout_ms: int = timeout_ms

        # if using DST: fixed duration dispense cycle, records how long should pour, None if not using
        self.fixed_dispense_cycle_length: Optional(float) = None
        
        # records if spout is pouring, None if idle, start time if pouring
        self.dispenser_start: Optional(float) = None

class Actuator(object):
    def __init__(self, id: int, timeout_ms: int = 1000):
        self.id: int = id
        self.timeout_ms: int = timeout_ms

        self.current_position: int = 0
        self.last_position_reached: int = 0
        self.target_position: int = 0

        # records if acutator is moving, None if idle, start time if pouring
        self.dispenser_start: Optional(float) = None


class DCB(object):
     
    def __init__(self, identity: str, station_id: str, io_count: int, dispenser_count: int, actuator_count: int):
        
        # Identification
        self.identity: str = identity
        self.station_id: str = station_id
        
        # Low level IO interface
        self.digital_outputs: List(bool) = [False for i in range(io_count)]
        self.digital_inputs: List(bool) = [False for i in range(io_count)]
        
        self.expansion_0_do:  List(bool) = [False for i in range(io_count)]
        self.expansion_0_di:  List(bool) = [False for i in range(io_count)]
        self.expansion_1_do:  List(bool) = [False for i in range(io_count)]
        self.expansion_1_di:  List(bool) = [False for i in range(io_count)]

        # Abstracted components
        self.dispensers =  [Dispenser(id=i) for i in range(dispenser_count)]
        self.actuators =  [Actuator(id=i) for i in range(actuator_count)]

    def prompt_command(self, command: str) -> str:
        # parses command, changes state accordingly, returns appropriate response
        pass




