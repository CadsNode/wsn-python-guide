import math 
import logging, sys
import json
logging.basicConfig(stream=sys.stderr, level=logging.INFO)

distanceArr=[]
node_pos_x=[233,281,534]  #Change this to corresponding X coordinates of nodes
node_pos_y=[138,353,147]  #Change this to corresponding Y coordinates of nodes
BS_POS_X =node_pos_x[0]
BS_POS_Y = node_pos_y[0]
BSID = 0
NB_NODES = len(node_pos_x)
INITIAL_ENERGY = 5 #Joules
ROUTING_TOPOLOGY_NAME = 'MTE'


def calculate_distance(node1,node2):
    x1 = node1.pos_x
    y1 = node1.pos_y
    x2 = node2.pos_x
    y2 = node2.pos_y
    return calculate_distance_point(x1,y1,x2,y2)

def calculate_distance_point(x1,y1,x2,y2):
    return math.sqrt((x1-x2)**2 + (y1-y2)**2)

class EnergySource(object):
    def __init__(self, parent, id):
        self.energy = INITIAL_ENERGY        
        self.node = parent
    def recharge(self,id):
        self.energy = INITIAL_ENERGY

class Battery(EnergySource):
    def consume(self, energy):
        if self.energy >= energy:
            self.energy -= 5
        else:
            self.energy = 0
            self.node.battery_depletion()

class PluggedIn(EnergySource):
    def consume(self, energy):
        pass

class Node(object):
    def __init__(self, id, parent = None):
        self.pos_x = node_pos_x[id]
        self.pos_y = node_pos_y[id]
        if id == BSID:
            self.energy_source = PluggedIn(self,id)
        else:
            self.energy_source = Battery(self,id)
        self.id = id
        self.alive = 1
     
    def battery_depletion(self):
        self.alive = 0

class RoutingProtocol(object):
    def setup_phase(self, network, round_nb=None):
            self._initial_setup(network)

class MTE(RoutingProtocol):
  def _initial_setup(self, network):
    self.calculate_weights(network)

  def calculate_weights(self, network):
    alive_nodes = network.get_alive_nodes()
    alive_nodes_and_BS = alive_nodes + [network.get_BS()]
    G = {}
    for node in alive_nodes_and_BS:
      G[node.id] = {}
      for other in alive_nodes_and_BS:
        if other == node:
          continue
        distance = calculate_distance(node, other) 
        cost = distance
        G[node.id][other.id] = cost
        dist={'u': node.id, 'v': other.id, 'w': cost}
        distanceArr.append(dist)
        
class Network(list):
    def __init__(self, init_nodes=None):
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
        self.routing_protocol = None
        self.initial_energy = self.get_remaining_energy()
    def get_remaining_energy(self,ignore_nodes=None):
        set = self.get_alive_nodes()
        if len(set) == 0:
            return 0
        if ignore_nodes:
            set = [node for node in set if node not in ignore_nodes]
        transform = lambda x: x.energy_source.energy
        energies = [transform(x) for x in set]
        return sum(x for x in energies)
    def get_alive_nodes(self):
        return [node for node in self[0:-1] if node.alive]

    def get_BS(self):
        return self[0]
    def simulate(self):
        self.routing_protocol.setup_phase(self, 0)
def run():
    network = Network()
    routing_protocol_class = eval(ROUTING_TOPOLOGY_NAME)
    network.routing_protocol = routing_protocol_class()
    network.simulate()
    results = {'data': distanceArr } #IMPORTANT: do not delete key 'data'
    print(json.dumps(results))
if __name__ == '__main__':
    run()