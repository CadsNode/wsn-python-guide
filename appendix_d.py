class Network(list):
    """docstring for Network"""
    def __init__(self, init_nodes=None):
        logging.debug('Instantiating the nodes...')
        if init_nodes:
            self.extend(init_nodes)
        else:
            nodes = [Node(i, self) for i in range(0,NB_NODES)]
            self.extend(nodes)
            base_station = Node(BSID, self)
            base_station.pos_x = BS_POS_X
            base_station.pos_y = BS_POS_Y
            self.append(base_station)
        self._dict = {}
        for node in self:
            self._dict[node.id] = node
        self.round = 0
        self.routing_protocol = None
        self.initial_energy = self.get_remaining_energy()
        self.first_depletion = 0
        self.per30_depletion = 0
        self.energy_spent = []
    def get_remaining_energy(self,ignore_nodes=None):
        set = self.get_alive_nodes()
        if len(set) == 0:
            return 0
        if ignore_nodes:
            set = [node for node in set if node not in ignore_nodes]
        transform = lambda x: x.energy_source.energy
        energies = [transform(x) for x in set]
        return sum(x for x in energies)

    def simulate(self):
        tracer = Tracer()
        self.routing_protocol.pre_communication(self)
        all_alive = 1
        percent70_alive = 1
        self.deaths_this_round = 0

        for round_nb in range(0, MAX_ROUNDS):
            self.round = round_nb
            print_args = (round_nb, self.get_remaining_energy())
            print("round %d: Calculated total remaining energy is: %f" % print_args)
            nb_alive_nodes = self.count_alive_nodes()
            if nb_alive_nodes == 0:
                break
            tracer['alive_nodes'][2].append(nb_alive_nodes)
            if TRACE_ENERGY:
                tracer['energies'][2].append(self.get_remaining_energy())
            
            self.routing_protocol.setup_phase(self, round_nb)

            if self.deaths_this_round != 0:
                if all_alive == 1:
                    all_alive = 0
                    self.first_depletion = round_nb
                if float(nb_alive_nodes)/float(NB_NODES) < 0.7 and percent70_alive == 1:
                    percent70_alive = 0
                    self.per30_depletion = round_nb
            self.deaths_this_round = 0
            self.routing_protocol.broadcast(self)
            self._run_round(round_nb)
        tracer['first_depletion'][2].append(self.first_depletion)
        tracer['30per_depletion'][2].append(self.per30_depletion)
        return tracer

    def count_alive_nodes(self):
        return sum(x.alive for x in self[:-1])
    def _run_round(self, round):
        before_energy = self.get_remaining_energy()
        for i in range(0, MAX_TX_PER_ROUND):
            self._sensing_phase()
            self._communication_phase()
        after_energy = self.get_remaining_energy()
        self.energy_spent.append(before_energy- after_energy)
    def _sensing_phase(self):
        for node in self.get_alive_nodes():
            node.sense()
    def _communication_phase(self):
        alive_nodes = self.get_alive_nodes()
        self._recursive_comm(alive_nodes)

    def get_alive_nodes(self):
        return [node for node in self[0:-1] if node.alive]
    
    def _recursive_comm(self, alive_nodes):
        next_alive_nodes = alive_nodes[:]
        for node in alive_nodes:
            depends_on_other_node = 0
            for other_node in alive_nodes:
                if other_node.next_hop == node.id:
                    depends_on_other_node = 1
                    break
            if not depends_on_other_node:
                node.transmit()
                next_alive_nodes = [n for n in next_alive_nodes if n != node]
        if len(next_alive_nodes) == 0:
            return
        else:
            self._recursive_comm(next_alive_nodes)
    def set_aggregation_function(self,function):
        for node in self:
            node.aggregation_function = function
    def get_average_energy(self):
        return np.average(self.energy_spent)
    def get_BS(self):
        return self[-1]

    def broadcast_next_hop(self):
        base_station = self.get_BS()
        for node in self.get_alive_nodes():
            base_station.transmit(msg_length=MSG_LENGTH, destination=node)
   
    def get_sensor_nodes(self):
        return [node for node in self[0:-1]] # RETURN ALL NODES EXCEPT BASE STATION
    def get_node(self,id):
        return self._dict[id]

    def get_heads(self, only_alives=1):
        input_set = self.get_alive_nodes() if only_alives else self
        return [node for node in input_set if node.is_head()]

    def reset(self):
        for node in self:
            node.energy_source.recharge()
            node.reactivate()
        self[-1].pos_x = BS_POS_X
        self[-1].pos_y = BS_POS_Y

        self.round = 0
        self.energy_spent = []
        self.routing_protocol =None
        self.first_depletion = 0
        self.per30_depletion = 0