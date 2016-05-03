# PyQt4 imports
from PyQt4 import QtGui, QtCore, QtOpenGL
from PyQt4.QtOpenGL import QGLWidget
# PyOpenGL imports
import OpenGL.GL as gl
import OpenGL.arrays.vbo as glvbo

import shaders




# from http://cyrille.rossant.net/shaders-opengl/
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


# from http://cyrille.rossant.net/shaders-opengl/
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


# from http://cyrille.rossant.net/shaders-opengl/
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


def make_shader_program(vertex_source, fragment_source):
    # compile the vertex shader
    vs = compile_vertex_shader(vertex_source)
    # compile the fragment shader
    fs = compile_fragment_shader(fragment_source)
    # compile the vertex shader
    return link_shader_program(vs, fs)


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
        if e == QtCore.Qt.Key_Return:  # repeat previous action
            self.set_data()
        self.vbo.set_array(self.data)
        self.vbo_c.set_array(self.data_c)

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
        a_position[1::6] = line_ends[:, :3]-thicknesses*normals
        a_position[2::6] = line_ends[:, 3:]+thicknesses*normals
        a_position[3::6] = a_position[1::6]
        a_position[4::6] = a_position[2::6]
        a_position[5::6] = line_ends[:, 3:]-thicknesses*normals
        colors = np.repeat(np.random.uniform(0.2, 1.00, (n, 4)), 6, axis=0)
        self.data = np.hstack((a_position, colors)).astype(np.float32)

        self.data_c = np.zeros((n, 12), dtype=np.float32)
        self.data_c[:, :3] = 0.45 * np.random.randn(n, 3)
        self.data_c[:, 3:7] = np.random.uniform(0.85, 1.00, (n, 4))
        self.data_c[:, 7:11] = 1, 0, 0, 1
        self.data_c[:, 11] = 10  #np.random.uniform(400, 100, n)

    def initializeGL(self):
        """Initialize OpenGL, VBOs, upload data on the GPU, etc.
        """
        # background color
        gl.glClearColor(1, 1, 1, 1)
        gl.glEnable(gl.GL_VERTEX_PROGRAM_POINT_SIZE)
        gl.glEnable(gl.GL_DEPTH_TEST)

        # create a Vertex Buffer Object with the specified data
        self.vbo = glvbo.VBO(self.data, usage='GL_STREAM_DRAW_ARB')
        self.shaders_program = make_shader_program(shaders.s_vert,
                                                   shaders.s_frag)
        self.position_location = gl.glGetAttribLocation(self.shaders_program,
                                                        'a_position')
        self.color_location = gl.glGetAttribLocation(self.shaders_program,
                                                     'a_fg_color')

        self.vbo_c = glvbo.VBO(self.data_c, usage='GL_STREAM_DRAW_ARB')
        self.shaders_program_c = make_shader_program(shaders.c_vert,
                                                     shaders.c_frag)
        self.c_position_location = gl.glGetAttribLocation(self.shaders_program_c,
                                                          'a_position')
        self.c_bg_color_location = gl.glGetAttribLocation(self.shaders_program_c,
                                                          'a_bg_color')
        self.c_fg_color_location = gl.glGetAttribLocation(self.shaders_program_c,
                                                          'a_fg_color')
        self.c_size_location = gl.glGetAttribLocation(self.shaders_program_c,
                                                      'a_size')
        self.u_size_loc = gl.glGetUniformLocation(self.shaders_program_c,
                                             'u_size')
        self.u_linewidth_loc = gl.glGetUniformLocation(self.shaders_program_c,
                                                  'u_linewidth')
        self.u_antialias_loc = gl.glGetUniformLocation(self.shaders_program_c,
                                                  'u_antialias')


    def paintGL(self):
        """Paint the scene.
        """
        # clear the buffer
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        # # bind the VBO
        self.vbo.bind()
        # tell OpenGL that the VBO contains an array of vertices
        gl.glEnableVertexAttribArray(self.position_location)
        gl.glEnableVertexAttribArray(self.color_location)

        stride = 7*4
        # prepare the shader
        # these vertices contain 3 single precision coordinates
        gl.glVertexAttribPointer(self.position_location,
                                 3, gl.GL_FLOAT,
                                 gl.GL_FALSE, stride, self.vbo)
        gl.glVertexAttribPointer(self.color_location,
                                 4, gl.GL_FLOAT,
                                 gl.GL_FALSE, stride, self.vbo+12)
        gl.glUseProgram(self.shaders_program)
        # draw "count" points from the VBO
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, len(self.data))
        self.vbo.unbind()

        self.vbo_c.bind()
        # tell OpenGL that the VBO contains an array of vertices
        gl.glEnableVertexAttribArray(self.c_position_location)
        gl.glEnableVertexAttribArray(self.c_bg_color_location)
        gl.glEnableVertexAttribArray(self.c_fg_color_location)
        gl.glEnableVertexAttribArray(self.c_size_location)

        stride = 12*4
        # prepare the shader
        # these vertices contain 2 single precision coordinates
        gl.glVertexAttribPointer(self.c_position_location,
                                 3, gl.GL_FLOAT,
                                 gl.GL_FALSE, stride, self.vbo_c)
        gl.glVertexAttribPointer(self.c_bg_color_location,
                                4, gl.GL_FLOAT,
                                gl.GL_FALSE, stride, self.vbo_c+12)
        gl.glVertexAttribPointer(self.c_fg_color_location,
                                 4, gl.GL_FLOAT,
                                 gl.GL_FALSE, stride, self.vbo_c+28)
        gl.glVertexAttribPointer(self.c_size_location,
                                 1, gl.GL_FLOAT,
                                 gl.GL_FALSE, stride, self.vbo_c+44)
        # print(self.vbo_c.data[0])
        gl.glUseProgram(self.shaders_program_c)
        gl.glUniform1f(self.u_size_loc, 1)
        gl.glUniform1f(self.u_antialias_loc, 1)
        gl.glUniform1f(self.u_linewidth_loc, 1)
        # draw "count" points from the VBO
        gl.glDrawArrays(gl.GL_POINTS, 0, len(self.data_c))
        self.vbo_c.unbind()

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
