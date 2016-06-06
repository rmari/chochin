<h1> Chōchin </h1>

![Chochin](./chochin.gif)

Chōchin is a program to visualize computer simulations data (typically
Molecular Dynamics data) in an easy manner. Chōchin is mostly a clone of [Yaplot](https://github.com/vitroid/Yaplot), based on
the same idea of a simple set of commands interpreted to render an
intentionally basic representation of 3D data. It is however based on a more modern graphic stack, using shader-based OpenGL for rendering, and PyQt4 for the GUI.
The use of Python for the GUI makes it easy to hack and modify.

So far not all of Yaplot features
are available (and possibly some of them will never be, the goal is not to be 100% Yaplot compatible).
Yaplot-style command files containing lines, sticks, circles and texts are processed by Chōchin.
The layer, color and radius commands are supported.
It is possible, to rotate, translate, zoom in and out, select layers to display, etc.

<h2> Installation and usage </h2>

Chōchin needs a Python 3 interpreter with numpy, PyQt4 and PyOpenGL packages. You can install these packages individually or get them through a Python distribution like [Anaconda](https://store.continuum.io/cshop/anaconda/).
You will also need a C++ compiler.

To install, clone this repository
```
$ git clone https://github.com/rmari/chochin.git
```
and run
```
$ python setup.py build_ext --inplace
```
in the topmost Chōchin directory.

To use, you can simply
```
$ python chochin.py your_data_cmd.txt
```
More probably, you want to make `chochin.py` executable and/or create an alias for it in your shell configuration file, so that you can
```
$ chochin your_data_cmd.txt
```


<h2> Data format </h2>

Currently, Chōchin supports the following subset of Yaplot data format:

| Command | Result |
|---------|--------|
| Empty line | New frame |
| @ [0-9] | Set the color of following objects (see default color palette below) |
| y [1-12] | Set the layer of following objects |
| r x | Set the thickness/radius of following objects to x |
| l x1 y1 z1 x2 y2 z2 | Draw a line from 1 to 2 |
| s x1 y1 z1 x2 y2 z2 | Draw a stick (line with thickness) from 1 to 2 |
| c x y z | Draw a circle centered on x,y,z |
| t x y z s | Print text string s on x,y,z |

Default colors:

| Index | Color |
|-------|-------|
| 0 | Qt.black |
| 1 | Qt.gray |
| 2 | Qt.white |
| 3 | Qt.green |
| 4 | Qt.yellow |
| 5 | Qt.red |
| 6 | Qt.blue |
| 7 | Qt.magenta |
| 8 | Qt.darkGreen |
| 9 | Qt.cyan |

User can override this default palette. Just create a file called
`chochin_palette.py` in the directory where you launch Chōchin. In this
file, you can define a color palette as, for example:
```
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QColor

color_palette = [ Qt.black, Qt.gray, (200,200,200,100), ... ]
```
The number of colors is unlimited. Colors can be [Qt colors](http://qt-project.org/doc/qt-4.8/qcolor.html) or tuples (r,g,b,a).

<h2> Control commands </h2>

| Command | Result without prefix | Result with number i prefix |
|---------|------------------------------|---------------------------|
| Mouse left-button drag  | Rotate field of view | - |
| Shift + Mouse left-button drag  | Translate field of view | - |
| Tab | Reset rotation and translation | - |
| * | Zoom in | - |
| / | Zoom out | - |
| n | Next frame | Move forward by i frames |
| p | Previous frame | Move backward by i frames |
| N | Forward movie | Framerate i |
| P | Backward movie | Framerate i |
| Space | Stop movie | - |
| g | Move to the first frame | Move to frame i |
| G | Move to the last frame | - |
| [F1 - F12] | Switch on/off layer [1-12] | - |
| v | Switch on/off information text | - |
| Up-Down-Left-Right | Rotate field of view | - |
| Shift + Up-Down-Left-Right | Rotate field of view by 90 deg | - |
| Return | Repeat previous command | - |
