#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module includes a function that defines user input"""

import argparse


def input_from_commandline():
    """This function defines user input from CLI"""
    # Store user inputs
    global_parser = argparse.ArgumentParser(
        prog="main.py",
        usage="%(prog)s [study_area] [outfile] [route_types] [method] [--n_routes]",
        description="Calculate centrality based on OSM data",
    )
    # Study area
    global_parser.add_argument(
        "study_area", help="select the study area to download OSM data"
    )

    # Output folder
    global_parser.add_argument("outfile", help="provide output folder")

    # Route types
    global_parser.add_argument(
        "route_types", choices=["shortest", "fastest"], help="choose a route type"
    )

    # Method
    subparsers = global_parser.add_subparsers(
        dest="method", description="methods to calculate centrality", required=True
    )
    subparsers.add_parser(
        "networkx", help="calculate betweenness centrality by networkx method"
    )
    geo = subparsers.add_parser(
        "geographical",
        help="calculate betweenness centrality by geographical adapted method",
    )
    geo.add_argument(
        "n_routes",
        type=int,
        default=1,
        help="provide the number of routes for geographical method",
    )
    args = global_parser.parse_args()
    return args
