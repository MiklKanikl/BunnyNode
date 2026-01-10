# Bunnynode

Bunnynode is a lightweight, interactive graph editor for building, analysing and exporting graphs.

## Features
- Node and Edge editing
- Shortest path (Dijkstra) calculation
- Save/Load
- PNG Export
- Multi selection, zoom & pan
- custom file format

## Dependencies
- Python 3.10+
- PyQt6
- pytest (for testing)

## Installation

Clone the repository and install dependencies:

pip install -r requirements.txt

## Run
python main.py

## Usage

### Nodes and Edges

You can create ellipse nodes with E and rectangle nodes with R or via the toolbar. You can move them around or change their propreties via the contextmenu by rightclicking them. Select two nodes and then click L to create an edge between them.

### File manipulation

You can save your graph with ctrl+s, load an existing one with ctrl+o or alternatively do these actions via the toolbar. You also can export your graph as a PNG picture via the toolbar.

### Other

With DEL you can delete multiple Nodes at a time, which you have selected
