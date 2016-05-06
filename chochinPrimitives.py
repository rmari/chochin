import OpenGL.GL as gl
import OpenGL.arrays.vbo as glvbo
import numpy as np


def compile_shader(source, shader):
    # from http://cyrille.rossant.net/shaders-opengl/
    gl.glShaderSource(shader, source)
    gl.glCompileShader(shader)
    # check compilation error
    result = gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS)
    if not(result):
        raise RuntimeError(gl.glGetShaderInfoLog(shader))
    return shader


def link_shader(vertex_shader, fragment_shader):
    """Create a shader program with from compiled shaders."""
    # from http://cyrille.rossant.net/shaders-opengl/
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
    vs = compile_shader(vertex_source,
                        gl.glCreateShader(gl.GL_VERTEX_SHADER))
    fs = compile_shader(fragment_source,
                        gl.glCreateShader(gl.GL_FRAGMENT_SHADER))
    # compile the vertex shader
    return link_shader(vs, fs)


def parse_shader(source):
    in_var = {'attribute': [],
              'varying': [],
              'uniform': []}

    for line in source.splitlines():
        lsplit = (line.split(";"))[0].split()
        if len(lsplit) > 0 and lsplit[0] in in_var:
            in_var[lsplit[0]].append(lsplit[1:])
    return in_var


def var_size(v):
    if v == 'float':
        return 1
    if v[:3] == 'vec':
        return int(v[3])


class ChochinPrimitiveArray:
    def __init__(self, vertex_code, fragment_code, gl_primitive):
        self.shaders_program = make_shader_program(vertex_code,
                                                   fragment_code)

        self.attributes_loc = {}
        self.attributes_size = {}
        self.uniforms_loc = {}
        self.uniforms_size = {}
        self.uniforms_val = {}
        self.parse_shader_var(vertex_code, fragment_code)
        self.gl_primitive = gl_primitive
        self.vbo = glvbo.VBO(np.zeros(3, dtype=np.float32),
                             usage='GL_STREAM_DRAW_ARB')

    def parse_shader_var(self, vertex_code, fragment_code):
        in_var = parse_shader(vertex_code + fragment_code)
        for a in in_var['attribute']:
            a_type, a_name = a
            self.attributes_loc[a_name] =\
                gl.glGetAttribLocation(self.shaders_program, a_name)
            self.attributes_size[a_name] = var_size(a_type)
        self.attribute_stride = 4*sum(self.attributes_size.values())

        for u in in_var['uniform']:
            u_type, u_name = u
            self.uniforms_loc[u_name] =\
                gl.glGetUniformLocation(self.shaders_program, u_name)
            self.uniforms_size[u_name] = var_size(u_type)

    def set_vbo(self, data):
        self.vbo = glvbo.VBO(data, usage='GL_STREAM_DRAW_ARB')

    def set_uniform(self, name, value):
        if name not in self.uniforms_loc:
            raise RuntimeError("unknown uniform")
        self.uniforms_val[name] = value

    def draw(self):
        self.vbo.bind()
        for a in self.attributes_loc:
            gl.glEnableVertexAttribArray(self.attributes_loc[a])
        offset = 0
        for a in self.attributes:
            gl.glVertexAttribPointer(self.attributes_loc[a],
                                     self.attributes_size[a],
                                     gl.GL_FLOAT,
                                     gl.GL_FALSE,
                                     self.attribute_stride,
                                     self.vbo + offset)
            offset += 4*self.attributes_size[a]

        gl.glUseProgram(self.shaders_program)
        for u in self.uniforms_loc:
            if self.uniforms_size[u] != 1:
                raise RuntimeError("only float uniforms are implemented")
            gl.glUniform1f(self.uniforms_loc[u], self.uniforms_val[u])

        gl.glDrawArrays(self.gl_primitive, 0, len(self.vbo.data))
        self.vbo.unbind()


class Sticks(ChochinPrimitiveArray):
    s_vert = """
    #version 120

    // Uniforms
    uniform float u_scale;

    attribute vec3 a_position;
    attribute vec4 a_fg_color;

    varying vec4 v_fg_color;

    void main (void) {
        gl_Position = vec4(a_position*u_scale,1.0);
        v_fg_color  = a_fg_color;
    }
    """

    s_frag = """
    #version 120

    varying vec4 v_fg_color;

    void main()
    {
        gl_FragColor = v_fg_color;
    }
    """

    def __init__(self):
        super().__init__(self.s_vert, self.s_frag, gl.GL_TRIANGLES)
        # self.set_uniform('u_scale', np.array([1, 1], dtype=np.float32))

    def set_data(self, line_ends, thicknesses, colors):
        n = line_ends.shape[0]
        normals = np.empty(shape=(n, 3))
        normals[:, 0] = np.ravel(line_ends[:, 4] - line_ends[:, 1])
        normals[:, 1] = np.ravel(line_ends[:, 0] - line_ends[:, 3])
        normals[:, 2] = 0
        normals /= np.linalg.norm(normals, axis=1)[:, np.newaxis]
        a_position = np.empty(shape=(6*n, 3))
        thicknesses = thicknesses.reshape((n, 1))
        a_position[::6] = line_ends[:, :3]+thicknesses*normals
        a_position[1::6] = line_ends[:, :3]-thicknesses*normals
        a_position[2::6] = line_ends[:, 3:]+thicknesses*normals
        a_position[3::6] = a_position[1::6]
        a_position[4::6] = a_position[2::6]
        a_position[5::6] = line_ends[:, 3:]-thicknesses*normals
        colors = np.repeat(colors, 6, axis=0)
        self.set_vbo(np.hstack((a_position, colors)).astype(np.float32))
        self.attributes = ['a_position', 'a_fg_color']


class Circles(ChochinPrimitiveArray):
    c_vert = """
    #version 120

    // Uniforms
    // ------------------------------------
    uniform float u_linewidth;
    uniform float u_antialias;
    uniform float u_scale;
    uniform float u_rad_scale;

    // Attributes
    // ------------------------------------
    attribute vec3  a_position;
    attribute vec4  a_fg_color;
    attribute vec4  a_bg_color;
    attribute float a_size;

    // Varyings
    // ------------------------------------
    varying vec4 v_fg_color;
    varying vec4 v_bg_color;
    varying float v_size;
    varying float v_linewidth;
    varying float v_antialias;

    void main (void) {
        v_size = a_size*u_rad_scale*u_scale;
        v_linewidth = u_linewidth;
        v_antialias = u_antialias;
        v_fg_color  = a_fg_color;
        v_bg_color  = a_bg_color;
        gl_Position = vec4(a_position*u_scale,1.0);
        gl_PointSize = v_size + 2*(v_linewidth + 1.5*v_antialias);
    }
    """

    c_frag = """
    #version 120

    // Constants
    // ------------------------------------


    // Varyings
    // ------------------------------------
    varying vec4 v_fg_color;
    varying vec4 v_bg_color;
    varying float v_size;
    varying float v_linewidth;
    varying float v_antialias;

    // Functions
    // ------------------------------------

    // ----------------
    float disc(vec2 P, float size)
    {
        float r = length((P.xy - vec2(0.5,0.5))*size);
        r -= v_size/2;
        return r;
    }

    // Main
    // ------------------------------------
    void main()
    {
        float size = v_size +2*(v_linewidth + 1.5*v_antialias);
        float t = v_linewidth/2.0-v_antialias;

        float r = disc(gl_PointCoord, size);

        float d = abs(r) - t;
        if( r > (v_linewidth/2.0+v_antialias))
        {
            discard;
        }
        else if( d < 0.0 )
        {
           gl_FragColor = v_fg_color;
        }
        else
        {
            float alpha = d/v_antialias;
            alpha = exp(-alpha*alpha);
            if (r > 0)
                gl_FragColor = vec4(v_fg_color.rgb, alpha*v_fg_color.a);
            else
                gl_FragColor = mix(v_bg_color, v_fg_color, alpha);
        }
    }
    """

    def __init__(self):
        super().__init__(self.c_vert, self.c_frag, gl.GL_POINTS)
        # self.set_uniform('u_antialias', np.float32(1))
        # self.set_uniform('u_linewidth', np.float32(1))
        # self.set_uniform('u_scale', np.array([1, 1], dtype=np.float32))

    def set_data(self, centers, radii, colors):
        n = centers.shape[0]
        data_c = np.zeros((n, 12), dtype=np.float32)
        data_c[:, :3] = centers
        data_c[:, 3:7] = colors
        data_c[:, 7:11] = 0, 0, 0, 1
        data_c[:, 11] = radii
        self.set_vbo(data_c)
        self.attributes = ['a_position', 'a_bg_color', 'a_fg_color', 'a_size']


class Lines(ChochinPrimitiveArray):
    vert = """
    #version 120

    // Uniforms
    uniform float u_scale;

    // Attributes
    attribute vec3  a_position;
    attribute vec4  a_fg_color;

    // Varyings
    varying vec4 v_fg_color;

    void main (void) {
        v_fg_color  = a_fg_color;
        gl_Position = vec4(a_position*u_scale,1.0);
    }
    """

    frag = """
    #version 120

    varying vec4 v_fg_color;

    void main()
    {
       gl_FragColor = v_fg_color;
    }
    """

    def __init__(self):
        super().__init__(self.vert, self.frag, gl.GL_LINES)

    def set_data(self, line_ends, colors):
        line_ends = line_ends.reshape((-1, 3))
        colors = np.repeat(colors, 2, axis=0)
        self.set_vbo(np.hstack((line_ends, colors)).astype(np.float32))
        self.attributes = ['a_position', 'a_fg_color']
