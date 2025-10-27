import matplotlib
from setuptools import setup
import os

setup(
    name='Traveling Salesman Problem Visualizer',
    version='1.0',
    description='A visualizer for the Traveling Salesman Problem using Panda3D',
    author='Jaxsen Honeycutt',
    options={
        "build_apps": {
            "gui_apps": {
                "tsp_visualizer": "main.py",
            },

            # Log file in the same folder as the executable
            "log_filename": "tsp_visualizer.log",
            "log_append": False,

            # Include source files, data, and matplotlib data
            "include_patterns": [
                "src/**",
                "**/*.mf",
                "**/*.prc",
                "results/.keep",
                "results/GA/.keep",
                f"{matplotlib.get_data_path()}/**"
            ],

            # platforms
            "platforms": ["manylinux2014_x86_64"],

            # Plugins you need
            "plugins": ["pandagl"],
        }
    }
)
