#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Classes to calculate betweenness centrality by two methods"""

import os
import random
import numpy as np
import networkx as nx
import osmnx as ox
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


class BetweennessCentrality:
    """This class initializes basic attributes of the graph and saves the network to output file"""

    def __init__(self, study_area: str, outfile: str):
        """Initialize graph network based on OSM data"""
        self.area = study_area
        self.graph = ox.graph_from_place(self.area, network_type="drive")
        self.nodes_df, self.edges_df = ox.graph_to_gdfs(self.graph)
        self.route_types = ["shortest", "fastest"]
        # Speed_limits for cars km/h
        self.hwy_speeds = {
            "motorway": 100,
            "motorroad": 90,
            "trunk": 85,
            "primary": 65,
            "secondary": 60,
            "residential": 30,
            "tertiary": 50,
            "living_street": 10,
            "service": 20,
            "road": 20,
            "track": 15,
        }  # etc
        self.outfile = outfile
        self.method = None
        self.type = None
        self.n = None
        self.centrality_df = None
        self.centrality_gdf = None

    def graph_fastest(self):
        """This function returns a graph network with travel time as edge weight"""
        graph_with_speeds = ox.add_edge_speeds(self.graph, self.hwy_speeds)
        # Add edge travel time(seconds) to graph as a new travel_time edge attribute
        graph_with_travel_time = ox.add_edge_travel_times(graph_with_speeds)
        return graph_with_travel_time

    def join_dataframe(self):
        """This function joins edge dataframe to centrality dataframe"""
        # Join with edges dataframe
        centrality_df = self.centrality_df.join(self.edges_df[["osmid", "geometry"]])
        centrality_gdf = gpd.GeoDataFrame(centrality_df, geometry="geometry", crs=4326)
        centrality_gdf["osmid"] = centrality_gdf["osmid"].astype("str")
        self.centrality_gdf = centrality_gdf
        return self.centrality_gdf

    def create_new_folder(self):
        """This function creates a new folder whose name contains study area, method, route types and routes number"""
        # Create a new folder
        output_path = os.path.join(
            self.outfile, f"{self.area}_{self.method}_{self.type}_{self.n}"
        )
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        return output_path

    def save_as_geopackage(self):
        """This function saves network as geopackage from dataframe"""
        # Save as GeoPackage
        self.centrality_gdf.to_file(
            os.path.join(self.create_new_folder(), "centrality.gpkg"), driver="GPKG"
        )

    def plot_network(self):
        """This function plots map"""
        # Normalize centrality to plot
        self.centrality_gdf["weight"] = (
            self.centrality_gdf["centrality"] - self.centrality_gdf["centrality"].min()
        ) / (
            self.centrality_gdf["centrality"].max()
            - self.centrality_gdf["centrality"].min()
        )
        # Plot the figure
        self.centrality_gdf.plot(linewidth=self.centrality_gdf["weight"] * 4)
        plt.title(
            f"Routes betweenness centrality in {self.area}, \n"
            f"n={self.n}, type={self.type}"
        )
        plt.xlabel("Easting [m]")
        plt.ylabel("Northing [m]")
        plt.tight_layout()

    def save_as_png(self):
        """This function saves map as png"""
        self.plot_network()
        plt.savefig(
            os.path.join(self.create_new_folder(), "centrality.png"), format="png"
        )


class Networkx(BetweennessCentrality):
    """This class calculates betweenness centrality by networkx"""

    def __init__(self, study_area: str, types: str, outfile: str):
        """Initialize route types and method"""
        super().__init__(study_area, outfile)
        self.type = types
        self.method = "networkx"
        self.n = "all_routes"

    def centrality(self):
        """This function calculates betweenness centrality with two route types by networkx"""
        if self.type == "shortest":
            bc = nx.edge_betweenness_centrality(self.graph, weight="length")
        elif self.type == "fastest":
            bc = nx.edge_betweenness_centrality(
                BetweennessCentrality.graph_fastest(self), weight="travel_time"
            )
        else:
            raise ValueError(
                "Invalid route type. Expected one of: %s" % self.route_types
            )
        # Convert value into a pandas dataframe
        centrality_df = pd.DataFrame(index=bc.keys(), data=bc.values())
        # Name the two index columns of the dataframe
        centrality_df.reset_index(inplace=True)
        centrality_df.columns = ["u", "v", "key", "centrality"]
        self.centrality_df = centrality_df.set_index(["u", "v", "key"])
        return self.centrality_df


class Geo(BetweennessCentrality):
    """This class calculates betweenness centrality by geographical adapted method"""

    def __init__(self, study_area: str, n_routes: int, outfile: str):
        """Initialize the number of routes, route types and method"""
        super().__init__(study_area, outfile)
        self.n = n_routes
        self.type = "random"
        self.method = "geographical"

    def generate_routes(self, n: int):
        """This function generates the start and end points of the routes based on population distribution"""
        # Boundary
        west, south, east, north = self.edges_df.unary_union.bounds
        # Random longitude and latitude
        lon_id = np.array([random.uniform(west, east) for i in range(2 * n)])
        if abs(north) > abs(south):
            lat_id = np.array([random.uniform(south, north) for j in range(2 * n)])
        else:
            lat_id = np.array([random.uniform(north, south) for j in range(2 * n)])
        # Search nearest nodes in the graph
        origin_node = ox.nearest_nodes(self.graph, lon_id[:n], lat_id[:n])
        destination_node = ox.nearest_nodes(self.graph, lon_id[n:], lat_id[n:])
        # Calculate the shortest path
        routes = [
            ox.shortest_path(self.graph, start, end)
            for start, end in zip(origin_node, destination_node)
        ]
        return routes

    def check_edges(self, routes) -> bool:
        """
        This function checks whether each edge contains only one node or the edge list is None
        :return: True, if routes contain invalid edges, otherwise False
        """
        # Filter None
        routes = list(filter(None, routes))
        # Check the number of routes
        if len(routes) != self.n:
            return True
        # Check the nodes number in each edge list
        else:
            for i in range(self.n):
                if len(routes[i]) == 1:
                    return True
        return False

    def random_routes(self):
        """
        This function replaces invalid routes with valid routes
        :param n: the number of random routes
        :return: a list of lists that contain nodes of each valid edge
        """
        routes = self.generate_routes(self.n)
        while self.check_edges(routes):
            routes = list(filter(None, routes))
            # Filter edges that contain only one node
            nodes_list = [
                routes[i] for i in range(len(routes)) if len(routes[i]) == 1
            ]  # Return the list
            routes = list(filter(lambda x: x not in nodes_list, routes))
            # Count the number of edges to add
            n_add = self.n - len(routes)
            # Add new routes
            routes.extend(self.generate_routes(n_add))
        return routes

    def centrality(self):
        """This function calculates betweenness centrality by geographical adapted method"""
        # Merge all route dataframes
        routes_gdf_list = [
            ox.routing.route_to_gdf(self.graph, route) for route in self.random_routes()
        ]
        routes_df = pd.concat(routes_gdf_list)
        routes_gdf = gpd.GeoDataFrame(routes_df, crs=4326)
        # Group routes by unique id and count the number of routes
        centrality_df = routes_gdf.groupby(["u", "v", "key"]).count()["osmid"]
        self.centrality_df = pd.DataFrame(centrality_df)
        self.centrality_df.rename(columns={"osmid": "centrality"}, inplace=True)
        return self.centrality_df
