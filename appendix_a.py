class Node(object):
    def __init__(self, id, parent = None):
        self.pos_x = np.random.uniform(0, AREA_WIDTH)
        self.pos_y = np.random.uniform(0, AREA_LENGTH)
        if id == BSID:
            self.energy_source = PluggedIn(self)
        else:
            self.energy_source = Battery(self)
        self.id = id
        self.network_handler = parent
        self.reactivate()
    def battery_depletion(self):
        self.alive = 0
        self.time_of_death = self.network_handler.round
        self.network_handler.deaths_this_round += 1
    def reactivate(self):
        self.alive = 1
        self.tx_queue_size = 0
        self._next_hop = BSID
        self.distance_to_endpoint = 0
        self.amount_sensed = 0
        self.amount_transmitted = 0
        self.amount_received = 0
        self.aggregation_function = lambda x: 0
        self.time_of_death = INFINITY
    @property
    def next_hop(self):
        return self._next_hop
    @next_hop.setter
    def next_hop(self,value):
        self._next_hop = value
        distance = calculate_distance(self,self.network_handler[value])
        self.distance_to_endpoint =distance
    def _only_active_nodes(func):
        def wrapper(self, *args, **kwargs):
            if self.alive:
                func(self,*args,**kwargs)
                return 1
            else:
                return 0
        return wrapper
    @_only_active_nodes
    def sense(self): 
        self.tx_queue_size = MSG_LENGTH
        self.amount_sensed += MSG_LENGTH        
    @_only_active_nodes
    def transmit(self, msg_length=None, destination=None):        
        logging.debug("node %d transmitting." % (self.id))
        if not msg_length:
            msg_length = self.tx_queue_size
        msg_length += HEADER_LENGTH
        if not destination:
            destination = self.network_handler[self.next_hop]
            distance = self.distance_to_endpoint
        else:
            distance = calculate_distance(self, destination)
        energy = E_ELEC
        if distance > THRESHOLD_DIST:
            energy += E_MP*(distance**4)
        else:
            energy += E_FS * (distance**2)
        energy *= msg_length
        destination.receive(msg_length)
        self.tx_queue_size = 0
        self.amount_transmitted += msg_length
        self.energy_source.consume(energy)
    @_only_active_nodes
    def receive(self,msg_length):
        logging.debug("node %d receiving." % (self.id))
        self._aggregate(msg_length-HEADER_LENGTH)
        self.amount_received +=msg_length
        energy = E_ELEC *msg_length
        self.energy_source.consume(energy)
    @_only_active_nodes
    def _aggregate(self, msg_length):
        logging.debug("node %d aggregating." % (self.id))
        aggregation_cost =self.aggregation_function(msg_length)
        self.tx_queue_size += aggregation_cost
        energy = E_DA * aggregation_cost
        self.energy_source.consume(energy)
    #####
    def is_head(self):
        if self.next_hop == BSID and self.id !=BSID and self.alive:
            return 1
        return 0