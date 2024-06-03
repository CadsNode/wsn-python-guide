class RoutingProtocol(object):
    """docstring for ClassName"""
    def pre_communication(self, network):
        if NOTIFY_POSITION:
            network.notify_position()
    def setup_phase(self, network, round_nb=None):
        if round_nb == 0:
            self._initial_setup(network)
        else:
            self._setup_phase(network)
    def _initial_setup(self, network):
        self._setup_phase(network)
    def _setup_phase(self,network):
        pass
    def broadcast(self, network):
        network.broadcast_next_hop()
    def notify_position(self):
        for node in self.get_alive_nodes():
            node.transmit(msg_length =MSG_LENGTH, destination=self.get_BS())