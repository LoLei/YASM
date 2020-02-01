#!/usr/bin/env python3
"""
YASM - Yet Another Site Mapper

Some elements taken from:
Stack Overflow
https://stackoverflow.com/q/7794489/4644044
Mridang Agarwalla - https://stackoverflow.com/users/304151/mridang-agarwalla
jro - https://stackoverflow.com/users/991521/jro
"""

__license__ = "CC BY-SA 4.0"

import argparse
import json
import os
from blockdiag import parser as blockdiagParser
from blockdiag import builder, drawer
from blockdiag.utils.fontmap import FontMap
from graphviz import Digraph
from six.moves.urllib.parse import urlparse
import colorspace


def add_blockdiag_option(blockdiag_text, option, value):
    """
    Prepend diagram scope attributes
    http://blockdiag.com/en/blockdiag/attributes/diagram.attributes.html

    There's probably a way to do this via the module but I CBA'd to
    comb through its source right now
    """
    if not value:
        return blockdiag_text

    blockdiag_text = blockdiag_text.replace("{",
                                            "{\n\t" + option + " = " + value,
                                            1)
    return blockdiag_text


def traverse_list_and_dict(element):
    if isinstance(element, dict):
        for item in element.values():
            yield item
    if isinstance(element, list):
        for item in element:
            yield item


def delete_empty(node):
    for element in traverse_list_and_dict(node):
        if element in ({}, []):
            node.remove(element)
        delete_empty(element)

def get_max_depth(node, depth=0, max_depth=0):
    for node_name in node:
        if isinstance(node[node_name][0], dict):
            max_depth = get_max_depth(node[node_name][0], depth+1, max_depth)
    if(depth > max_depth):
        max_depth = depth
    return max_depth


def create_nodes(node, graph, max_depth, parent_name=None, depth=0,
                 unique_id=0, color=None, blockdiag=False, calc_max_depth=0):
    if depth > max_depth:
        return
    last = None
    count = 0
    for node_name in node:
        unique_id += 1
        node_id = node_name + str(unique_id)
        last = node_id
        if depth == 1:
            colors = colorspace.qualitative_hcl()(len(node) + 1)
            color = colors[count]
        if not isinstance(node[node_name][0], dict) and depth == 1 and parent_name is not None:
            if blockdiag:
                graph.node(node_id, node_name, style='filled', fillcolor=color)
            else:
                firstlevelgraph = Digraph(name='cluster_' + node_id)
                firstlevelgraph.attr(style="invis")
                firstlevelgraph.node(node_id, node_name, style='filled', fillcolor=color)
                vprint('YASM: Creating node ', node_id)
                vprint('YASM: Creating edge ', parent_name, '->', node_id)
                graph.subgraph(firstlevelgraph)
            graph.edge(parent_name, node_id)
        else:
            if parent_name is not None:
                depth_calc = (1/calc_max_depth)*(depth-0.5)
                node_color = colorspace.desaturate(color, depth_calc)[0]
                graph.node(node_id, node_name, style='filled', fillcolor=node_color)
                vprint('YASM: Creating node ', node_id)
                vprint('YASM: Creating edge ', parent_name, '->', node_id)
                graph.edge(parent_name, node_id)
            if isinstance(node[node_name][0], dict):
                if not blockdiag:
                    subpgraph_cluster = Digraph(name='cluster_' + str(unique_id))
                    subpgraph_cluster.attr(style="invis")
                    subpgraph_cluster.node(node_id, node_name, style='filled')
                    last_ret = create_nodes(node[node_name][0], subpgraph_cluster, max_depth, node_id, depth + 1, unique_id, color, blockdiag,calc_max_depth)
                    graph.subgraph(subpgraph_cluster)
                else:
                    graph.node(node_id, node_name, style='filled')
                    last_ret = create_nodes(node[node_name][0], graph, max_depth, node_id, depth + 1, unique_id, color, blockdiag, calc_max_depth)
                if last_ret is not None:
                    last = last_ret
        count += 1
    return last


def rewrite_subdomains_as_slash(data):
    """
    Insert subdomain parts in reverse order after TLD as slash parts
    """
    for page in data:
        url = page['url']
        url_parsed = urlparse(url)

        # Check if URL contains subdomain
        hostname_parts = url_parsed.hostname.split('.')
        tld = hostname_parts[-1]
        if not len(hostname_parts) > 2:
            page['subdomain'] = False
            continue

        # Build slash string and remove parts in front of URL at the same time
        subdomains_as_slash = ""
        hostname_parts = hostname_parts[:-2]
        for part in reversed(hostname_parts):
            subdomains_as_slash += part
            subdomains_as_slash += "/"
            url = url.replace(part + ".", "", 1)

        # Insert slashed subdomains after TLD slash
        pos_of_slash = url.find("." + tld + "/") + len(tld) + 2
        url = url[:pos_of_slash] + subdomains_as_slash + url[pos_of_slash:]
        page['url'] = url

        # Indicate that this node stems from a subdomain
        # In case we want to differentiate regular pages and subdomains
        # in the output
        page['subdomain'] = True

    return data


def graphviz_legend(last_node, dot):
    legend = Digraph(name='cluster_01')
    legend.attr('graph', label = '<<font point-size=\'42\'>Legend</font>>')

    legend2 = Digraph()
    legend2.attr(rank='same')

    legend2.node('key', label='<<table border=\"0\" cellpadding=\"2\" cellspacing=\"5\" cellborder=\"0\"> <tr><td align=\"right\" port=\"i1\">Parent</td></tr></table>>')

    legend2.node('key2', label='<<table border=\"0\" cellpadding=\"2\" cellspacing=\"5\" cellborder=\"0\"> <tr><td align=\"center\" port=\"i1\">Child</td></tr></table>>')

    legend2.edge('key:i1:e', 'key2:i1:w', arrowhead='normal')
    legend2.node('DUMMY_0',  shape='point', style='invis')
    legend.subgraph(legend2)
    dot.subgraph(legend)
    dot.node('DUMMY_1', style='invis', shape='point')
    dot.node('DUMMY_2', style='invis', shape='point')
    dot.edge(last_node, 'DUMMY_2', style='invis')
    dot.edge('DUMMY_2', 'DUMMY_1', style='invis')
    dot.edge('DUMMY_1', 'DUMMY_0', style='invis')


def main(args):
    print("YASM: Starting...")

    url_paths = []
    root = {}
    with open(args.file) as json_file:
        data = json.load(json_file)

        if args.sdsp:
            data = rewrite_subdomains_as_slash(data)

        # Split URL paths into elements along /
        for item in data:
            split = item['url'].rstrip("/").split('/')
            url_paths.append(split[2:])
            if args.sdsp:
                url_paths[-1].append({'title': item['title'], 'url': split[-1],
                                      'subdomain': item['subdomain']})
            else:
                url_paths[-1].append({'title': item['title'], 'url': split[-1]})

        # Build tree structure from elements
        for path in url_paths:
            # Get element if it exists, set to empty if not
            branch = root.setdefault(path[0], [{}, []])
            for i in path[1:-1]:
                branch = branch[0].setdefault(i, [{}, []])
            branch[1].append(path[-1])

    # Delete empty elements
    delete_empty(root)

    # Output JSON file (Maybe move to util file)
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_file_json = os.path.join(output_dir, os.path.split(args.file)[-1])
    with open(output_file_json, 'w') as outfile:
        json.dump(root, outfile, indent=2, ensure_ascii=False)

    # To append .gv, .pdf/.png/.svg later
    output_name = output_file_json[:-len(".json")]
    if args.depth == 694201337:
        calc_max_depth = get_max_depth(root)
    else:
        calc_max_depth = args.depth
    # Sitemap via dot or blockdiag
    if args.engine == "dot":
        dot = Digraph()
        dot.graph_attr['rankdir'] = 'TB'
        dot.graph_attr['splines'] = 'ortho'
        dot.graph_attr['concentrate'] = 'true'

        # User formatting options
        dot.graph_attr['nodesep'] = args.widthpadding
        dot.graph_attr['ranksep'] = args.heightpadding

        dot.node_attr['shape'] = 'rect'
        dot.node_attr['style'] = 'filled'
        last = create_nodes(root, dot, args.depth, calc_max_depth=calc_max_depth)
        graphviz_legend(last, dot)
        # Save to file
        # GV creates a PDF/SVG and .gv at the same time, need to rename one
        dot.format = args.type
        output_file_gv = output_name + ".gv"
        dot.render(output_name, view=args.instant)
        os.rename(output_name, output_file_gv)

    elif args.engine == "blockdiag":
        dotDiag = Digraph()
        create_nodes(root, dotDiag, args.depth, blockdiag=True, calc_max_depth=calc_max_depth)
        source = dotDiag.source
        source = source.replace("digraph", "blockdiag")

        # Legend/Key
        blockdiag_legend = """group {
        label = "Legend";
        color="#808080";
        Parent -> Child;
        }
        }"""
        source = source.replace("}", blockdiag_legend)

        # Colors
        source = source.replace("subgraph", "group")
        source = source.replace("fillcolor", ",color")
        source = source.replace("style=filled", "")

        # User formatting options
        source = add_blockdiag_option(source,
                                      "orientation", args.orientation)
        source = add_blockdiag_option(source,
                                      "span_width", args.widthpadding)
        source = add_blockdiag_option(source,
                                      "span_height", args.heightpadding)

        tree = blockdiagParser.parse_string(source)
        diagram = builder.ScreenNodeBuilder.build(tree)

        # Font only needed for PDF output
        # use project specific font file
        fontname = "DejaVuSans.ttf"
        fontpath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "util", fontname)
        fontmap = FontMap()
        fontmap.set_default_font(fontpath)

        draw = drawer.DiagramDraw(args.type, diagram,
                                  filename=output_name + '.' + args.type,
                                  fontmap=fontmap)

        draw.draw()
        draw.save()

    print("YASM: Finished.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Input file - YACA JSON")
    parser.add_argument("-v", "--verbose", action="store_true", default=False,
                        help="Verbosity of the output")
    parser.add_argument("-i", "--instant", action="store_true", default=False,
                        help="View the output file immediately")
    parser.add_argument("-d", "--depth", action="store", type=int, default=694201337,
                        help="Maximum depth of the sitemap (default unlimited)")
    parser.add_argument("-wp", "--widthpadding", action="store", type=str,
                        help="Padding width between adjacent nodes")
    parser.add_argument("-hp", "--heightpadding", action="store", type=str,
                        help="Padding height between adjacent nodes")
    parser.add_argument("-e", "--engine", action="store", default="dot",
                        choices=["dot", "blockdiag"], help="Engine for output")
    parser.add_argument("-o", "--orientation", action="store",
                        default="portrait", choices=["landscape", "portrait"],
                        help="Orientation for blockdiag output")
    parser.add_argument("-t", "--type", action="store", default="pdf",
                        choices=["pdf", "svg"], help="Output file type")
    parser.add_argument("-s", "--sdsp", action="store_true", default=False,
                        help="Treat subdomains same as slash path URL parts")
    args = parser.parse_args()

    # Use vprint to print only when --verbose is specified
    if args.verbose:
        def vprint(*va):
            for v in va:
                print(v, end=''),
            print()
    else:
        vprint = lambda *va: None

    main(args)
