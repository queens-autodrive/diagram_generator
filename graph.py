import graphviz
import markdown_to_json
import ast
from collections import OrderedDict

# Read the file and create the tree
with open('README.md', 'r') as file:
    tree = markdown_to_json.dictify(file.read())

nodes = OrderedDict()
for key in tree['ROS2 Interactions'].keys():
    if key.startswith("Node: "):
        nodes[key.split('Node: ')[1]] = tree['ROS2 Interactions'][key]


def add_edge(graph, start, end, label, pub=True):
    if pub:
        graph.edge(start, end, label=label)
    else:
        graph.edge(end, start, label=label)


def check_interaction(graph, node, name, pub, prefix=''):
    if name not in node.keys():
        print("Warning! Interaction name not found")
        return
    if node[name] == '':
        return
    for pubkey in node[name].keys():
        subnodes = ast.literal_eval("["+node[name][pubkey].split("[")[-1])
        for subnode in subnodes:
            subnode = subnode.split(": ")[-1].split("'")[0]
            for subsubnode in subnode.split(', '):
                add_edge(dot, key, subsubnode, f"{prefix}{pubkey.split('/')[-1]}", pub)


dot = graphviz.Digraph(comment='System Architecture', strict=True)
for key in nodes.keys():
    dot.node(key, key, shape="ellipse", penwidth='3.0', fontsize="24pt")
    node = nodes[key]
    check_interaction(dot, node, 'Publishers', True)
    check_interaction(dot, node, 'Subscriptions', False)
    check_interaction(dot, node, 'Service Clients', True, 'Request ')
    check_interaction(dot, node, 'Service Clients', False, 'Response ')
    check_interaction(dot, node, 'Service Servers', True, 'Request ')
    check_interaction(dot, node, 'Service Servers', False, 'Response ')
    check_interaction(dot, node, 'Action Clients', True, 'Goal ')
    check_interaction(dot, node, 'Action Clients', False, 'Result ')
    check_interaction(dot, node, 'Action Servers', True, 'Goal ')
    check_interaction(dot, node, 'Action Servers', False, 'Result ')


dot.render(format='svg', filename='diagram_generator/system_architecture', engine='dot')
