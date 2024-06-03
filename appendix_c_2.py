class DC(RoutingProtocol):
    def pre_communication(self,network):
        logging.info('Direct Communication: Setup phase')
        for node in network:
            node.next_hop = BSID
    def broadcast(self, network):
        pass