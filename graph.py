import graphviz
import markdown_to_json
import ast
from collections import OrderedDict

# Read the file and create the tree
with open('README.md', 'r') as file:
    tree = markdown_to_json.dictify(file.read())

if 'Packages' in tree.keys():
    repo_type = 'workspace'
elif 'Workspaces' in tree.keys():
    repo_type = 'package'
else:
    raise Exception


def add_edge(graph, start, end, label, pub=True):
    if pub:
        graph.edge(start, end, label=label)
    else:
        graph.edge(end, start, label=label)


def check_interaction(graph, key, node, name, pub, prefix=''):
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
                add_edge(graph, key, subsubnode, f"{prefix}{pubkey.split('/')[-1]}", pub)


def addPackage(graph, tree):
    nodes = OrderedDict()
    for key in tree['ROS2 Interactions'].keys():
        if key.startswith("Node: "):
            nodes[key.split('Node: ')[1]] = tree['ROS2 Interactions'][key]

    for key in nodes.keys():
        graph.node(key, key, shape="ellipse", penwidth='3.0', fontsize="24pt")
        node = nodes[key]
        check_interaction(dot, key, node, 'Publishers', True)
        check_interaction(dot, key, node, 'Subscriptions', False)
        check_interaction(dot, key, node, 'Service Clients', True, 'Request ')
        check_interaction(dot, key, node, 'Service Clients', False, 'Response ')
        check_interaction(dot, key, node, 'Service Servers', True, 'Request ')
        check_interaction(dot, key, node, 'Service Servers', False, 'Response ')
        check_interaction(dot, key, node, 'Action Clients', True, 'Goal ')
        check_interaction(dot, key, node, 'Action Clients', False, 'Result ')
        check_interaction(dot, key, node, 'Action Servers', True, 'Goal ')
        check_interaction(dot, key, node, 'Action Servers', False, 'Result ')
        check_interaction(dot, key, node, 'Transform Broadcasters', True)
        check_interaction(dot, key, node, 'Transform Listeners', False)


dot = graphviz.Digraph(comment='System Architecture', strict=True)
if repo_type == 'package':
    addPackage(dot, tree)
else:
    print(tree['Packages'])
    for package in tree['Packages'].keys():
        print(package)
        print(tree['Packages'][package])
dot.render(format='svg', filename='system_architecture', engine='dot')
