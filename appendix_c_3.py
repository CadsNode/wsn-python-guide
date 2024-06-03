class priorityDictionary(dict):
    def __init__(self):
        self.__heap = []
        dict.__init__(self)

    def smallest(self):
        '''Find smallest item after removing deleted items from heap.'''
        if len(self) == 0:
            raise IndexError("smallest of empty priorityDictionary")
        heap = self.__heap
        while heap[0][1] not in self or self[heap[0][1]] != heap[0][0]:
            lastItem = heap.pop()
            insertionPoint = 0
            while 1:
                smallChild = 2*insertionPoint+1
                if smallChild+1 < len(heap) and \
                        heap[smallChild] > heap[smallChild+1]:
                    smallChild += 1
                if smallChild >= len(heap) or lastItem <= heap[smallChild]:
                    heap[insertionPoint] = lastItem
                    break
                heap[insertionPoint] = heap[smallChild]
                insertionPoint = smallChild
        return heap[0][1]
  
    def __iter__(self):
        def iterfn():
            while len(self) > 0:
                x = self.smallest()
                yield x
                del self[x]
        return iterfn()
  
    def __setitem__(self,key,val):
        dict.__setitem__(self,key,val)
        heap = self.__heap
        if len(heap) > 2 * len(self):
            self.__heap = [(v,k) for k,v in self.items()]
            self.__heap.sort()  # builtin sort likely faster than O(n) heapify
        else:
            newPair = (val,key)
            insertionPoint = len(heap)
            heap.append(None)
            while insertionPoint > 0 and \
                    newPair < heap[(insertionPoint-1)//2]:
                heap[insertionPoint] = heap[(insertionPoint-1)//2]
                insertionPoint = (insertionPoint-1)//2
            heap[insertionPoint] = newPair
  
    def setdefault(self,key,val):
        '''Reimplement setdefault to call our customized __setitem__.'''
        if key not in self:
            self[key] = val
        return self[key]


def Dijkstra(G,start,end=None):
  D = {}  # dictionary of final distances
  P = {}  # dictionary of predecessors
  Q = priorityDictionary()  # estimated distances of non-final vertices
  Q[start] = 0
  
  for v in Q:
    D[v] = Q[v]
    if v == end: break
    
    for w in G[v]:
      vwLength = D[v] + G[v][w]
      if w in D:
        if vwLength < D[w]:
          raise ValueError("Dijkstra: found better path to already-final vertex")
      elif w not in Q or vwLength < Q[w]:
        Q[w] = vwLength
        P[w] = v
  
  return (D,P)
      
def shortestPath(G,start,end):
  D,P = Dijkstra(G,start,end)
  Path = []
  while 1:
    Path.append(end)
    if end == start: break
    end = P[end]
  Path.reverse()
  return Path


class MTE(RoutingProtocol):
  def _find_shortest_path(self, network):
    logging.info('MTE: setup phase')
    alive_nodes = network.get_alive_nodes()
    alive_nodes_and_BS = alive_nodes + [network.get_BS()]
    G = {}
    for node in alive_nodes_and_BS:
      G[node.id] = {}
      for other in alive_nodes_and_BS:
        if other == node:
          continue
        distance = calculate_distance(node, other)
        cost = distance**2 if distance < THRESHOLD_DIST else distance**4
        G[node.id][other.id] = cost
    done = []
    while len(alive_nodes) != 0:
      starting_node = alive_nodes[0]
      shortest_path = shortestPath(G, starting_node.id, BSID)
      for i, id in enumerate(shortest_path):
        if id == BSID or id in done:
          break
        network.get_node(id).next_hop = shortest_path[i+1]
        alive_nodes = [node for node in alive_nodes if node.id != id]
        done.append(id)

  def _setup_phase(self, network):
    if network.deaths_this_round != 0:
      self._find_shortest_path(network)
      network.broadcast_next_hop()

  def _initial_setup(self, network):
    network.perform_two_level_comm = 0
    self._find_shortest_path(network)
    network.broadcast_next_hop()