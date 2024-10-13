#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Calculate centrality based on OSM data"""

import osmnx as ox
from mypackage import mymodule1
from mypackage import mymodule2


def main():
    """Choose the study area, calculate betweenness centrality and save output in a new folder"""
    global obj, args

    # User input
    try:
        args = mymodule2.input_from_commandline()
        print("Processing...\nPlease wait...")
    except ValueError:
        print("Please check the input")

    # Access to the graph of study area
    graph = ox.graph_from_place(args.study_area, network_type="drive")
    # Description of the road network in the study area
    print(
        f"""---------------------\n{args.study_area}\nnodes|{len(graph.nodes)}\nroute segments|{len(graph.edges)}\n---------------------"""
    )

    # If the user choose networkx or geographical method, create an object by calling the corresponding class.
    if args.method == "networkx":
        obj = mymodule1.Networkx(args.study_area, graph, args.route_types, args.outfile)
    elif args.method == "geographical":
        obj = mymodule1.Geo(
            args.study_area, graph, args.route_types, args.n_routes, args.outfile
        )

    # Calculate betweenness centrality and inform the user
    print("Calculating betweenness centrality...\nPlease be patient...")
    obj.centrality()
    obj.join_dataframe()

    # Save the network and inform the user
    print("---------------------\nSaving the network...\nPlease wait...")
    obj.create_new_folder()
    obj.save_as_geopackage()
    obj.plot_network()
    obj.save_as_png()

    # Inform the user output
    print(
        f"---------------------\nFinished! Download files to {args.outfile}\nThank you for using."
    )


if __name__ == "__main__":
    main()
