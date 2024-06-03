class EnergySource(object):
    """docstring for ClassName"""
    def __init__(self, parent):
        self.energy = INITIAL_ENERGY
        self.node = parent
    def recharge(self):
        self.energy = INITIAL_ENERGY

class Battery(EnergySource):
    """docstring for Battery"""
    def consume(self, energy):
        if self.energy >= energy:
            self.energy -= energy

        else:
            logging.info("node %d: battery is depleted." % (self.node.id))
            self.energy = 0
            self.node.battery_depletion()
class PluggedIn(EnergySource):
    """docstring for PluggedIn"""
    def consume(self, energy):
        pass