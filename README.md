# Bunnynode

Bunnynode is a lightweight, interactive graph editor for building, analysing and exporting graphs.

## Features
- Node and Edge editing
- Shortest path (Dijkstra) calculation
- undo/redo commands
- copy/paste/cut/duplicate
- Save/Load
- PNG Export
- Multi selection, zoom & pan
- custom file format

## Dependencies
- Python 3.14+
- PyQt6
- pytest (for testing)

## Installation

install Python 3.14 or newer

Clone the repository and install dependencies:

pip install -r requirements.txt

## Run
python main.py

## Usage

### Nodes and Edges

You can create ellipse nodes with E and rectangle nodes with R or via the menubar. All other Nodes you can create only via the menubar. You can move them around or change their propreties via the contextmenu by rightclicking them. To create an edge between nodes press L or for a directed edge shift+L and then click on the first and then on the second node. To leave edge creation, press ESC.
With DEL you can delete all selected items at once. For easier creating of same items over and over you can: copy (Ctrl+C), paste (Ctrl+V), cut (Ctrl+X) and duplicate (Ctrl+D).

### File manipulation

You can save your graph with ctrl+s, load an existing one with ctrl+o or alternatively do these actions via the toolbar. You also can export your graph as a PNG picture via the toolbar.

### Real Time Colab mode

You can now work in real time with another people. You can either create a room and share the access token or you can join the others' room via the token. To access your room token just press 'show token' on the toolbar and a messagebox telling you your token will appear.

### Other

You can compute the path distance between two selected nodes that are connected. For that you can right click on the nodes and choose one as the start node and one as the endnode.
