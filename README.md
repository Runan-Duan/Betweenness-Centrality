# Betweenness Centrality
This simple Python package provides two methods to compute betweenness centrality of road networks efficiently.

## Description
* The **Betweenness-Centrality/src** directory is the project’s root directory. It consists of the following components:

| Component | Description|
| :---------------- |:---------------- |
| mymodule1.py | It contains the code that supports the main functions and methods of script,  such as a parent class Betweenness Centrality and two child classes Networkx, Geo. |
| mymodule2.py | It provides the script’s command line interface, which is mainly used to process input from the command line and provide help information. |
| test_mypackage.py | It contains unit tests for the components of the modules, especially the core functions in the classes. |
| main.py | It provides the executable file, that you could enter arguments from the command line. |
| betweenness_centrality.ipynb | This Jupyter notebook contains simple usage and examples of two Python packages NetworkX and OSMnx |
| research_questions.ipynb | This Jupyter notebook shows the use of this Python package in road networks research and gives a short introduction to two methods. |

- **environment.yml** provides a conventional file that lists the project’s external dependencies. You could use this file to automatically install the dependencies.
- **README.md** provides the project description and instructions for installing and running the package.

## Getting Started

### Prerequisites
If you are installing from source, you will need:
* Python 3.12 or later
* A compiler that supports Python 3.12

We highly recommend installing on [Anaconda](https://www.anaconda.com/download) environment.

### Dependencies

This Python package depends on other Python libraries such as

- networkx
- osmnx
- numpy
- pandas
- geopandas
- …

### Installation
#### Get the Package

You need go to the Gitlab repository: https://courses.gistools.geog.uni-heidelberg.de/sm330/05_network_analysis.git to get the source package.

```
git clone https://github.com/Runan-Duan/Betweenness-Centrality.git
```
#### Install Dependencies
All required packages are contained in the **environment.yml** file, you can install the Python environment on your computer
```
conda env create -f environment.yml
```

#### Activate the environment
The environment name is **betweenness-centrality**, you can activate this environment to execute the main script.
```
conda activate betweenness-centrality
```

For development and further contributions, please use pre-commit hooks
and the configuration file named  **.pre-commit-config.yaml** is in the root of the repository.


### Executing program
* You can use the following command after activating your environment in Anaconda Prompt.
```
python main.py [study_area] [outfile] [route_types] [method] [--n_routes]
```
* There are some commands that were previously used in **commandline.bat**, such as
```
python main.py "Göttingen, Germany" .\output fastest networkx
```
```
python main.py "Würzburg, Germany" .\output fastest geographical 100
```

## Help
Advice for common problems or issues
* Make sure you are connected to the Internet when you run the main script.
* The main script contains help information. You can find out how to run it by using the following command.
```
python main.py -h
```
* If you choose the geo-adapted method and get an error message "the graph contains no edges" or similar, please check your input arguments [study_area] or [n_routes]. Because the program generates each route based on two randomly selected nodes, the number of routes should not exceed half the number of nodes in the network.

## Authors
Runan Duan, [sm330@stud.uni-heidelberg.de](sm330@stud.uni-heidelberg.de)

## Acknowledgements
This project was inspired by the lecture "[Advanced Geoscripting: Introduction to scientific programming with Python](http://advancedgeoscripting.courses-pages.gistools.geog.uni-heidelberg.de/home/content/intro.html)" at the Geographical Institute of the University of Heidelberg.

## Resources
[1] code: osmnx examples for shortest path https://github.com/gboeing/osmnx-examples/blob/main/notebooks/02-routing-speed-time.ipynb

[2] Ludwig, C., Psotta, J., Buch, A., Kolaxidis, N., Fendrich, S., Zia, M., Fürle, J., Rousell, A., and Zipf, A.: TRAFFIC SPEED MODELLING TO IMPROVE TRAVEL TIME ESTIMATION IN OPENROUTESERVICE, Int. Arch. Photogramm. Remote Sens. Spatial Inf. Sci., XLVIII-4/W7-2023, 109–116, https://doi.org/10.5194/isprs-archives-XLVIII-4-W7-2023-109-2023, 2023.

[3] Kirkley, A., Barbosa, H., Barthelemy, M. et al. From the betweenness centrality in street networks to structural invariants in random planar graphs. Nat Commun 9, 2501 (2018). https://doi.org/10.1038/s41467-018-04978-z
