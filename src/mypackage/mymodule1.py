#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Classes to calculate betweenness centrality by two methods"""

import os
import numpy as np
import networkx as nx
import osmnx as ox
import pandas as pd
import geopandas as gpd
import random
import matplotlib.pyplot as plt


class BetweennessCentrality:
    """This class initializes basic attributes of the graph and saves the network to output file"""

    def __init__(self, study_area, graph, route_types: str, outfile: str):
        """Initialize graph network based on OSM data"""
        self.area = study_area
        self.type = route_types
        if self.type == "shortest":
            self.graph = graph
            self.weight = "length"
        elif self.type == "fastest":
            self.hwy_speeds = {  # Speed_limits for cars km/h
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
            }
            self.graph_with_speeds = ox.add_edge_speeds(graph, self.hwy_speeds)
            self.graph = ox.add_edge_travel_times(self.graph_with_speeds)
            self.weight = "travel_time"
        self.nodes_df, self.edges_df = ox.graph_to_gdfs(self.graph)
        self.outfile = outfile
        self.method = None
        self.n = None
        self.centrality_df = None
        self.centrality_gdf = None

    def join_dataframe(self):
        """This function joins edge dataframe to centrality dataframe"""
        # Join with edges dataframe
        centrality_df = self.centrality_df.join(self.edges_df[["osmid", "geometry"]])
        centrality_gdf = gpd.GeoDataFrame(centrality_df, geometry="geometry", crs=4326)
        centrality_gdf["osmid"] = centrality_gdf["osmid"].astype("str")
        self.centrality_gdf = centrality_gdf
        return self.centrality_gdf

    def create_new_folder(self):
        """This function creates a new folder whose name contains study area, route types, method and routes number"""
        # Create a new folder
        output_path = os.path.join(
            self.outfile, f"{self.area}_{self.type}_{self.method}_{self.n}"
        )
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        return output_path

    def save_as_geopackage(self):
        """This function saves the network as a geopackage"""
        # Save as a GeoPackage
        self.centrality_gdf.to_file(
            os.path.join(self.create_new_folder(), "centrality.gpkg"), driver="GPKG"
        )

    def plot_network(self):
        """This function plots a map"""
        # Normalize centrality to plot
        self.centrality_gdf["weight"] = (
            self.centrality_gdf["centrality"] - self.centrality_gdf["centrality"].min()
        ) / (
            self.centrality_gdf["centrality"].max()
            - self.centrality_gdf["centrality"].min()
        )
        # Plot the figure
        self.centrality_gdf.plot(
            linewidth=self.centrality_gdf["weight"] * 4,
            column="centrality",
            cmap="magma_r",
            legend=True,
            legend_kwds={"label": "centrality"},
        )
        plt.title(
            f"Routes betweenness centrality in {self.area}, \n"
            f"n={self.n}, type={self.type}"
        )
        plt.xlabel("Easting [m]")
        plt.ylabel("Northing [m]")
        plt.tight_layout()

    def save_as_png(self):
        """This function saves the map in png format"""
        self.plot_network()
        plt.savefig(
            os.path.join(self.create_new_folder(), "centrality.png"), format="png"
        )


class Networkx(BetweennessCentrality):
    """This class calculates betweenness centrality by networkx"""

    def __init__(self, study_area, graph, route_types: str, outfile: str):
        """Initialize method"""
        super().__init__(study_area, graph, route_types, outfile)
        self.method = "networkx"
        self.n = len(self.graph.edges)

    def centrality(self):
        """This function calculates betweenness centrality by networkx"""
        # Calculate the betweenness centrality of the graph
        bc = nx.edge_betweenness_centrality(self.graph, weight=self.weight)
        # Convert value into a pandas dataframe
        centrality_df = pd.DataFrame(index=bc.keys(), data=bc.values())
        # Name the two index columns of the dataframe
        centrality_df.reset_index(inplace=True)
        centrality_df.columns = ["u", "v", "key", "centrality"]
        self.centrality_df = centrality_df.set_index(["u", "v", "key"])
        return self.centrality_df


class Geo(BetweennessCentrality):
    """This class calculates betweenness centrality by geographical adapted method"""

    def __init__(
        self, study_area, graph, route_types: str, n_routes: int, outfile: str
    ):
        """Initialize the number of routes and method"""
        super().__init__(study_area, graph, route_types, outfile)
        self.n = n_routes
        self.method = "geographical"

    def generate_routes(self):
        """This function generates the start and end points of the routes randomly"""
        routes_valid = []
        temp = self.n - len(routes_valid)
        while temp != 0:
            # Caculate n shortest-path routes using random origin-destination paris
            origs = np.random.choice(self.graph.nodes, size=temp, replace=True)
            dests = np.random.choice(self.graph.nodes, size=temp, replace=True)
            # Calculate n shortest-path routes using random origin-destination paris
            routes = ox.shortest_path(self.graph, origs, dests, weight=self.weight)
            # Extract valid routes
            temp_valid = [r for r in routes if r is not None]
            routes_valid.extend(temp_valid)
            # Reselect routes until the number of valid routes meets the user's need
            temp = self.n - len(routes_valid)
        return routes_valid

    def centrality(self):
        """This function calculates betweenness centrality by geographical adapted method"""
        # Merge all route dataframes
        routes_gdf_list = [
            ox.routing.route_to_gdf(self.graph, route)
            for route in self.generate_routes()
        ]
        routes_df = pd.concat(routes_gdf_list)
        routes_gdf = gpd.GeoDataFrame(routes_df, crs=4326)
        # Group routes by unique id and count the number of routes
        centrality_df = routes_gdf.groupby(["u", "v", "key"]).count()["osmid"]
        self.centrality_df = pd.DataFrame(centrality_df)
        self.centrality_df.rename(columns={"osmid": "centrality"}, inplace=True)
        return self.centrality_df
