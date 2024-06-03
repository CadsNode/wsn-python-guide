def calculate_distance(node1,node2):
    x1 = node1.pos_x
    y1 = node1.pos_y
    x2 = node2.pos_x
    y2 = node2.pos_y
    return calculate_distance_point(x1,y1,x2,y2)

def calculate_distance_point(x1,y1,x2,y2):
    return math.sqrt((x1-x2)**2 + (y1-y2)**2)
def zero_cost_aggregation(msg_length):
    return 0
def total_cost_aggregation(msg_length):
    return msg_length
def linear_cost_aggregation(factor):
    return lambda x: int(x*factor)
def log_cost_aggregation(msg_length):
    return int(math.log(msg_length))


class Tracer(dict):
    """docstring fos Tracer"""
    def __init__(self):
        rounds_label = 'Rounds'
        self['alive_nodes'] = ('Number of alive nodes', rounds_label, [], 1,0)
        if TRACE_ENERGY:
            self['energies'] = ('Energy(J)', rounds_label, [], 1,0)
        self['first_depletion'] = ('First depletion', rounds_label, [],0,0)
        self['30per_depletion'] = ('30 percent depletion', rounds_label, [], 0,0)
        self['nb_sleeping']     = ('% of sleeping nodes'  , rounds_label, [], 0, 1)