import time
from threading import Lock, Thread
from typing import List, Optional, Union, Any

"""
Simulator for the DCB

Open Questions:

-Should low IO be simulated, or just higher level dispenser/actuator abstractions?
-If also sumulating low level IO, should it be changed when dispenser pour is called?
-How to simulate digital_in change?
-How best simulate actuator move? Takes arbitrary amout of time...

"""

DELIMITER = '\n'
ERROR = "ERROR"
OK = "OK"

class Dispenser(object):
    def __init__(self, id: int, timeout_ms: int = 1000):
        self.id: int = id
        self.timeout_ms: int = timeout_ms

        # if using DST: fixed duration dispense cycle, records how long should pour, None if not using
        self.fixed_dispense_cycle_length: Optional[float] = None
        
        # records if spout is pouring, None if idle, start time if pouring
        self.dispenser_start: Optional[float] = None

    def reset_pour_timeout(self):
        self.dispenser_start = time.time()

class Actuator(object):
    def __init__(self, id: int, timeout_ms: int = 1000):
        self._id: int = id
        self._timeout_ms: int = timeout_ms

        self._current_position: int = 0
        self._last_position_reached: int = 0
        self._target_position: int = 0

        # records if acutator is moving, None if idle, start time if pouring
        self._actuator_start: Optional[float] = None

        self._lock = Lock()
        self._stop = False
        self._thread: Optional[Thread] = None
    
    def start_move(self, target):
        # if annother action is in progress
        if self._thread is not None:
            # set the stop flag
            with self._lock:
                self._stop = True
            # wait for the thread to see flag and exit
            self._thread.join()
        # create new thread
        self._thread =  Thread(self._move, args=(target, ))
        # reset the stop flag
        with self._lock:
            self._stop = True
        # start the action
        self._thread.start()
        return
    
    def _move(self, target):
        with self._lock:
            self._target_position = target
            self._current_position = 0
            self._actuator_start = time.time()

        while (time.time() - self._actuator_start) * 1000 < self._timeout_ms:
            time.sleep(0.01)
            with self._lock:
                if self._stop:
                    self._actuator_start = None
                    self._current_position = 0
                    self._target_position = 0
                    return

        
        with self._lock:
            self._actuator_start = None
            self._current_position = target
            self._target_position = 0

        return
    
    def get_current_position_str(self) -> str:
        with self._lock:
            return str(self._current_position)
    
    def get_target_position_str(self) -> str:
        with self._lock:
            return str(self._target_position)
    
    def is_moving(self):
        with self._lock:
            return self._actuator_start is not None




class DCB(object):
     
    def __init__(self, identity: str, station_id: str, io_count: int, dispenser_count: int, actuator_count: int):
        
        # Identification
        self.identity: str = identity
        self.station_id: str = station_id
        
        # Low level IO interface
        self.digital_outputs: List[bool] = [False for i in range(io_count)]
        self.digital_inputs: List[bool] = [False for i in range(io_count)]
        
        self.expansion_0_do: List[bool] = [False for i in range(io_count)]
        self.expansion_0_di: List[bool] = [False for i in range(io_count)]
        self.expansion_1_di: List[bool] = [False for i in range(io_count)]
        self.expansion_1_do: List[bool] = [False for i in range(io_count)]

        # Abstracted components
        self.dispensers = [Dispenser(id=i) for i in range(dispenser_count)]
        self.actuators = [Actuator(id=i) for i in range(actuator_count)]

    def _in_range(self, index: Union[int, str], array: List[Any]):
        if 0 <= int(index) < len(array):
            return True
        return False
    
    def prompt_command(self, command: str) -> str:
        # parses command, changes state accordingly, returns appropriate response 
        response = self._parse_command(command)
        return response + DELIMITER

    def _parse_command(self, command: str) -> str:

        if command[:3] == "DOP":
            if command[3] == "?":
                if not self._in_range(command[4], self.digital_outputs):
                    print("Requested DO change that was out of range")
                    return ERROR
                return "DOP=" + str(int(self.digital_outputs[command[4]]))
                
        if command[:3] == "DSP":
            dispenser_id = int(command[4])
            
            if not self._in_range(dispenser_id, self.dispensers):
                print("Requested Dispenser that is out of range")
                return ERROR
            
            self.dispensers[dispenser_id].reset_pour_timeout()
            return OK

        if command[:3] == "MSP":
            actuator_id = int(command[4])
        
            if not self._in_range(command[4], self.actuators):
                print("Requested actruator that is out of range")
                return ERROR

            if command[3] == "?":
                return "MSP:" + actuator_id + "=" + self.actuators[actuator_id].get_target_position_str()

            target = int(command[6])
            self.actuators[actuator_id].start_move(target)
            return OK

        

        





