# PyQt4 imports
from PyQt4 import QtGui, QtCore, QtOpenGL
from PyQt4.QtOpenGL import QGLWidget
# PyOpenGL imports
import OpenGL.GL as gl
import OpenGL.arrays.vbo as glvbo

VS = """
attribute vec3 a_position;
attribute vec4 a_fg_color;

varying vec4 v_fg_color;

void main (void) {
    gl_Position = vec4(a_position,1.0);
    v_fg_color  = a_fg_color;
}
"""

FS = """
varying vec4 v_fg_color;

void main()
{
    gl_FragColor = v_fg_color;
}
"""


def compile_vertex_shader(source):
    """Compile a vertex shader from source."""
    vertex_shader = gl.glCreateShader(gl.GL_VERTEX_SHADER)
    gl.glShaderSource(vertex_shader, source)
    gl.glCompileShader(vertex_shader)
    # check compilation error
    result = gl.glGetShaderiv(vertex_shader, gl.GL_COMPILE_STATUS)
    if not(result):
        raise RuntimeError(gl.glGetShaderInfoLog(vertex_shader))
    return vertex_shader


def compile_fragment_shader(source):
    """Compile a fragment shader from source."""
    fragment_shader = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)
    gl.glShaderSource(fragment_shader, source)
    gl.glCompileShader(fragment_shader)
    # check compilation error
    result = gl.glGetShaderiv(fragment_shader, gl.GL_COMPILE_STATUS)
    if not(result):
        raise RuntimeError(gl.glGetShaderInfoLog(fragment_shader))
    return fragment_shader


def link_shader_program(vertex_shader, fragment_shader):
    """Create a shader program with from compiled shaders."""
    program = gl.glCreateProgram()
    gl.glAttachShader(program, vertex_shader)
    gl.glAttachShader(program, fragment_shader)
    gl.glLinkProgram(program)
    # check linking error
    result = gl.glGetProgramiv(program, gl.GL_LINK_STATUS)
    if not(result):
        raise RuntimeError(gl.glGetProgramInfoLog(program))
    return program


class GLPlotWidget(QGLWidget):
    # default window size
    width, height = 600, 600

    def __init__(self, parent=None):
        QtOpenGL.QGLWidget.__init__(
            self, QtOpenGL.QGLFormat(QtOpenGL.QGL.SampleBuffers), parent)
        self.installEventFilter(self)
        self.set_data()

    def keyPressEvent(self, event):
        e = event.key()
        # if e == QtCore.Qt.Key_Return:  # repeat previous action
        self.set_data()
        # self.vbo = glvbo.VBO(self.data, usage='GL_STREAM_DRAW_ARB')
        self.vbo.set_array(self.data)

        self.updateGL()

    def set_data(self):
        # generate random data points
        n = 5000
        thicknesses = 0.01*np.random.uniform(0, 1, (n, 1))
        line_ends = np.random.uniform(-1, 1, size=(n, 6))
        normals = np.empty(shape=(n, 3))
        normals[:, 0] = line_ends[:, 4] - line_ends[:, 1]
        normals[:, 1] = line_ends[:, 0] - line_ends[:, 3]
        normals[:, 2] = 0
        normals /= np.linalg.norm(normals, axis=1)[:, np.newaxis]
        a_position = np.empty(shape=(6*n, 3))
        a_position[::6] = line_ends[:, :3]+thicknesses*normals
        a_position[1::6] = line_ends[:,:3]-thicknesses*normals
        a_position[2::6] = line_ends[:,3:]+thicknesses*normals
        a_position[3::6] = a_position[1::6]
        a_position[4::6] = a_position[2::6]
        a_position[5::6] = line_ends[:, 3:]-thicknesses*normals
        colors = np.repeat(np.random.uniform(0.85, 1.00, (n, 4)),6, axis=0)
        self.data = np.hstack((a_position, colors)).astype(np.float32)
        self.count = self.data.shape[0]

    def initializeGL(self):
        """Initialize OpenGL, VBOs, upload data on the GPU, etc.
        """
        # background color
        gl.glClearColor(0, 0, 0, 0)
        # create a Vertex Buffer Object with the specified data
        self.vbo = glvbo.VBO(self.data, usage='GL_STREAM_DRAW_ARB')
        # compile the vertex shader
        vs = compile_vertex_shader(VS)
        # compile the fragment shader
        fs = compile_fragment_shader(FS)
        # compile the vertex shader
        self.shaders_program = link_shader_program(vs, fs)
        self.position_location = gl.glGetAttribLocation(self.shaders_program,
                                                        'a_position')
        self.color_location = gl.glGetAttribLocation(self.shaders_program,
                                                     'a_fg_color')

    def paintGL(self):
        """Paint the scene.
        """
        # clear the buffer
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        # bind the VBO
        self.vbo.bind()
        # tell OpenGL that the VBO contains an array of vertices
        gl.glEnableVertexAttribArray(self.position_location)
        gl.glEnableVertexAttribArray(self.color_location)

        stride = 7*4
        # prepare the shader
        # these vertices contain 2 single precision coordinates
        gl.glVertexAttribPointer(self.position_location,
                                 3, gl.GL_FLOAT,
                                 gl.GL_FALSE, stride, self.vbo)
        gl.glVertexAttribPointer(self.color_location,
                                 3, gl.GL_FLOAT,
                                 gl.GL_FALSE, stride, self.vbo+12)
        gl.glUseProgram(self.shaders_program)
        # draw "count" points from the VBO
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, len(self.data))
        self.vbo.unbind()


    def resizeGL(self, width, height):
        """Called upon window resizing: reinitialize the viewport.
        """
        # update the window size
        self.width, self.height = width, height
        # paint within the whole window
        gl.glViewport(0, 0, width, height)
        # set orthographic projection (2D only)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        # the window corner OpenGL coordinates are (-+1, -+1)
        gl.glOrtho(-1, 1, 1, -1, -1, 1)

if __name__ == '__main__':
    # import numpy for generating random data points
    import numpy as np
    import sys

    # define a Qt window with an OpenGL widget inside it
    class TestWindow(QtGui.QMainWindow):
        def __init__(self):
            super(TestWindow, self).__init__()

            # initialize the GL widget
            self.widget = GLPlotWidget()
            # put the window at the screen position (100, 100)
            self.setGeometry(100, 100, self.widget.width, self.widget.height)
            self.setCentralWidget(self.widget)
            self.show()
        def keyPressEvent(self, event):
            self.widget.keyPressEvent(event)
            self.update()
    # create the Qt App and window
    app = QtGui.QApplication(sys.argv)
    window = TestWindow()
    window.show()
    app.exec_()
