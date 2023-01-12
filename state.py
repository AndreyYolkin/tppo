class RelayState:
    def __init__(self, num_switches = 6):
        self.num_switches = num_switches
        self.state = ["off"] * self.num_switches
    
    def get_state(self,index=None):
        if index is not None:
            return {"state": self.state[index]}
        else:
            return {"state": self.state}
        
    def set_state(self, new_state, index=None):
        print(new_state)
        if index is not None:
            if new_state in ["on", "off"] and 0 <= index < self.num_switches:
                self.state[index] = new_state
            else:
                raise ValueError("Invalid state or index passed.")
        else:
            if all(val in ["on", "off"] for val in new_state) and len(new_state) == self.num_switches:
                self.state = new_state
            else:
                raise ValueError("Invalid state passed.")
