# Bunnynode

Bunnynode is a lightweight, interactive graph editor desktop app for building, analysing and exporting graphs.
It's written in python using PyQt6

## Features
- Node and Edge editing
- Shortest path (Dijkstra) calculation
- undo/redo commands
- copy/paste/cut/duplicate
- Save/Load
- PNG Export
- Multi selection, zoom & pan
- custom file format

## Installation

install Python 3.12 or newer

https://www.python.org/downloads/

install uv

https://docs.astral.sh/uv/getting-started/installation/

Clone the repository

## Run
if you want to use the publicly hosted version:

```bash
uv run main.py
```

if you want to use a self hosted version:

```bash
uv run main.py http://your-self-hosted-bunnynode/
```

## Exe File
you can download the newest BunnyNode.exe file on:

[BunnyNode/releases](https://github.com/MiklKanikl/BunnyNode/releases)

## Backend
the backend is open-source on:

[BunnyNode-backend](https://github.com/MiklKanikl/BunnyNode-backend)

## Usage

### Nodes and Edges

You can create ellipse nodes with E, rectangle nodes with R and image nodes with i or via the menubar. You can move them around or change their propreties via the contextmenu by rightclicking them. To create an edge between nodes press L or for a directed edge shift+L and then click on the first and then on the second node. To leave edge creation, press ESC.
With DEL you can delete all selected items at once. For easier creating of same items over and over you can: copy (Ctrl+C), paste (Ctrl+V), cut (Ctrl+X) and duplicate (Ctrl+D).

### File manipulation

You can save your graph with ctrl+s, load an existing one with ctrl+o or alternatively do these actions via the toolbar. You also can export your graph as a PNG picture via the toolbar.

### Real Time Colab mode

You can now work in real time with another people. You can either create a room and share the access token or you can join the others' room via the token. To access your room token just press 'show token' on the toolbar and a messagebox telling you your token will appear.

### Other

You can compute the path distance between two selected nodes that are connected. For that you can right click on the nodes and choose one as the start node and one as the endnode.
