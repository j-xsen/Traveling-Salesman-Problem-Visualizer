from setuptools import setup

setup(
    name='Traveling Salesman Problem Visualizer',
    version='1.0',
    description='A visualizer for the Traveling Salesman Problem using Panda3D',
    author='Jaxsen Honeycutt',
    options={
        'build_apps': {
            'gui_apps': {
                'tsp_visualizer': 'main.py',
            },

            'log_filename': '$USER_APPDATA/TravelingSalesmanProblem/logs/tsp_visualizer.log',
            'log_append': False,

            'include_patterns': [
                'src/tsp/**',
                'src/**.tsp',
                '**/*.mf',
                '**/*.prc',
                'results/.keep'
            ],

            'plugins': [
                'pandagl',
            ]
        }
    }
)