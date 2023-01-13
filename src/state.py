import copy

class RelayState:
    def __init__(self, num_switches = 6):
        self.num_switches = num_switches
        self.state = ["off"] * self.num_switches
    
    def equal(self, other_state, index = None):
        if index is not None:
            return self.state[int(index)] == other_state
        return self.state == other_state

    def get_state(self, index=None):
        if index is not None:
            return self.state[int(index)]
        else:
            return self.state
        
    def set_state(self, new_state, index=None):
        if (self.equal(new_state, index)):
            raise ValueError("State is not changed")
        if index is not None:
            if new_state in ["on", "off"] and 0 <= int(index) < self.num_switches:
                self.state[int(index)] = new_state
            else:
                raise ValueError("Invalid state or index passed.")
        else:
            if all(val in ["on", "off"] for val in new_state) and len(new_state) == self.num_switches:
                self.state = new_state
            else:
                raise ValueError("Invalid state passed.")
                        
    def imagine_state(self, new_state, index=None):
        resulted_state = copy.copy(self.state)
        if (self.equal(new_state, index)):
            raise ValueError("State is not changed")
        if index is not None:
            if new_state in ["on", "off"] and 0 <= int(index) < self.num_switches:
                resulted_state[int(index)] = new_state
            else:
                raise ValueError("Invalid state or index passed.")
        else:
            if all(val in ["on", "off"] for val in new_state) and len(new_state) == self.num_switches:
                resulted_state = new_state
            else:
                raise ValueError("Invalid state passed.")
        return resulted_state
