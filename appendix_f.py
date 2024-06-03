from __future__ import generators
import math
import numpy as np
import logging, sys
import matplotlib.pyplot as plt
import sys 

logging.basicConfig(stream=sys.stderr, level=logging.INFO)

######## GLOBAL PARAMETERS ########

NB_NODES=10 # Number of nodes
TX_RANGE = 100 #meters
AREA_WIDTH =500.0 
AREA_LENGTH =500.0 #meters  
MAX_ROUNDS= 15000
TRACE_ENERGY=1
MAX_TX_PER_ROUND =1 #Number of transmissions of sensed information to BS per round
NOTIFY_POSITION =1
BSID = -1
BS_POS_X =250.0
BS_POS_Y = 250.0
MSG_LENGTH = 4000 #bits 
HEADER_LENGTH = 150 #bits
INITIAL_ENERGY = 2 #Joules   

E_ELEC = 50e-9 #Joules ###Energy dissipated at the transceiver (/bit)
E_DA = 5e-9 #Joules ####Energy dissipated at the data aggregation (/bit)
E_MP = 0.0013e-12 #Joules ###Energy dissipated at the power amplifier (supposing a multipath fading channel(/bin/m^4)
E_FS = 10e-12 #Joules  ###Energy dissipated at the power amplifier (supposing a LOS free space channel (/bin/m^2)
THRESHOLD_DIST = math.sqrt(E_FS/E_MP)

INFINITY = float('inf')
MINUS_INFINITY =float('-inf')

logger = logging.getLogger(__name__)
def plot_nodes():
    network = Network()
    heads = network.get_heads(only_alives=0)
    X = [node.pos_x for node in heads]
    Y = [node.pos_y for node in heads]
    plt.scatter(X, Y, color='r', marker='^', s=80)
    X = [network.get_BS().pos_x]
    Y = [network.get_BS().pos_y]
    plt.scatter(X, Y, color='b', marker='x', s=80)
    plt.show()

def plot_traces(traces, name):
    first_tracer = next(iter(traces.items()))
    nb_columns   = len([1 for v in first_tracer if v[3]])
    fig, ax      = plt.subplots(nrows=1, ncols=nb_columns)

    colors = ['b', 'r', 'k', 'y', 'g', 'c', 'm']
    line_style = ['-', '--', '-.', ':']

    color_idx = 0
    line_idx  = 0
    subplot_idx = 1
    for trace_name, trace in traces.items():
        if not trace[3]:
            continue
        ax = plt.subplot(1, nb_columns, subplot_idx)
        ax.set_title(trace_name)
        X = range(0, len(trace[2]))
        color_n_line = colors[color_idx] + line_style[line_idx]
        plt.plot(X, trace[2], color_n_line, label=name)
        plt.xlabel(trace[1])
        plt.ylabel(trace[0])
        plt.legend(fontsize=11)
        subplot_idx += 1
    color_idx = (color_idx+1)%len(colors)
    line_idx  = (line_idx+1)%len(line_style)
    plt.xlim(xmin=0)
    plt.ylim(ymin=0)
    plt.show()



def run_program():
    ROUTING_TOPOLOGY_NAME = 'DC'  # another option ---> MTE
    AGGREGATION_NAME = 'total' 
    network = Network()
    remaining_energies = []
    average_energies = []    
    routing_protocol_class = eval(ROUTING_TOPOLOGY_NAME)
    network.routing_protocol = routing_protocol_class()      
    aggregation_function = AGGREGATION_NAME + '_cost_aggregation'
    network.set_aggregation_function(eval(aggregation_function))
    simulation_results=network.simulate()
    remaining_energies.append(600 - network.get_remaining_energy())
    average_energies.append(network.get_average_energy()) 

    print('Remaining energies: ')
    print(remaining_energies)
    print('Average energies: ')
    print(average_energies) 
    plot_traces(simulation_results, ROUTING_TOPOLOGY_NAME)  


if __name__ == '__main__':
  plot_nodes()
  run_program()