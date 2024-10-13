#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests classes in modules"""

import unittest
import osmnx as ox
import pandas as pd
import geopandas as gpd
import shapely
from src.mypackage import mymodule1


class TestMethods(unittest.TestCase):
    """This classes tests functions in class BetweennessCentrality"""

    def setUp(self):
        """This function is used to share setup"""
        self.graph = ox.graph_from_bbox(
            north=49.793744, south=49.7936051, east=9.9481363, west=9.9481324
        )
        self.type = "shortest"
        self.networkx = mymodule1.Networkx(
            "Test Graph", self.graph, "shortest", r".\output"
        )
        self.geo = mymodule1.Geo("Test Graph", self.graph, "fastest", 1, r".\output")

    def test_networkx_centrality(self):
        """This function tests centrality function in class Networkx"""
        index = pd.MultiIndex.from_tuples(
            zip([43632295, 43632312], [43632312, 43632295], [0, 0]),
            names=["u", "v", "key"],
        )
        expected_df = pd.DataFrame([0.5, 0.5], index=index, columns=["centrality"])
        pd.testing.assert_frame_equal(self.networkx.centrality(), expected_df)

    def test_join_dataframe(self):
        """This function tests join dataframe function in class BetweennessCentrality"""
        self.networkx.centrality()
        index = pd.MultiIndex.from_tuples(
            zip([43632295, 43632312], [43632312, 43632295], [0, 0]),
            names=["u", "v", "key"],
        )
        expected_df = gpd.GeoDataFrame(
            {
                "centrality": [0.5, 0.5],
                "osmid": ["44169102", "44169102"],
                "geometry": [
                    shapely.LineString(
                        [[9.9481363, 49.793744], [9.9481324, 49.7936051]]
                    ),
                    shapely.LineString(
                        [[9.9481324, 49.7936051], [9.9481363, 49.793744]]
                    ),
                ],
            },
            index=index,
        )
        pd.testing.assert_frame_equal(self.networkx.join_dataframe(), expected_df)

    def test_geo_centrality(self):
        """This function tests centrality function in class Geo"""
        index = pd.MultiIndex.from_tuples(
            zip([43632295], [43632312], [0]), names=["u", "v", "key"]
        )
        expected_df = pd.DataFrame(1, index=index, columns=["centrality"])
        pd.testing.assert_frame_equal(self.geo.centrality(), expected_df)


if __name__ == "__main__":
    unittest.main()
