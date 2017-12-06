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


def link_shader(shaders):
    """Create a shader program with from compiled shaders."""
    # from http://cyrille.rossant.net/shaders-opengl/
    program = gl.glCreateProgram()
    for shader in shaders:
        gl.glAttachShader(program, shader)
    gl.glLinkProgram(program)
    # check linking error
    result = gl.glGetProgramiv(program, gl.GL_LINK_STATUS)
    if not result:
        raise RuntimeError(gl.glGetProgramInfoLog(program))
    return program


def make_shader_program(vertex, fragment, geometry=""):
    shaders = []
    shaders.append(compile_shader(vertex, gl.glCreateShader(gl.GL_VERTEX_SHADER)))
    shaders.append(compile_shader(fragment, gl.glCreateShader(gl.GL_FRAGMENT_SHADER)))
    # compile the vertex shader
    if geometry != "":
        shaders.append(compile_shader(geometry, gl.glCreateShader(gl.GL_GEOMETRY_SHADER)))
    return link_shader(shaders)


def parse_array_size(src_line):
    lbracket = src_line.find("[")
    if lbracket == -1:
        return src_line, 1
    else:
        return src_line[:lbracket], src_line[lbracket+1:src_line.find("]")]


def parse_shader(source):
    in_var = {'in': [],
              'uniform': []}

    for line in source.splitlines():
        lsplit = (line.split(";"))[0]
        lsplit, array_size = parse_array_size(lsplit)
        lsplit = lsplit.split()
        if len(lsplit) > 0 and lsplit[0] in in_var:
            new_var = tuple(lsplit[1:]) + (int(array_size),)
            in_var[lsplit[0]].append(new_var)
    return in_var


def in_size(v):
    if v == 'float':
        return 1, gl.GL_FLOAT
    if v[:3] == 'vec':
        return int(v[3]), gl.GL_FLOAT
    if v == 'int':
        return 1, gl.GL_INT


def uniform_setter(utype, uname, usize):
    if usize > 1:
        if utype == 'float':
            return lambda loc, val: gl.glUniform1fv(loc, usize, val)
    else:
        if utype == 'float':
            return lambda loc, val: gl.glUniform1f(loc, val)
        if utype[:3] == 'vec':
            return lambda loc, val: gl.glUniform3fv(loc, 1, val)
        if utype[:3] == 'mat':
            return lambda loc, val: gl.glUniformMatrix3fv(loc, 1,
                                                          gl.GL_FALSE, val)
    raise RuntimeError("cannot treat uniform ", utype, uname)


class ChochinPrimitiveArray:
    def __init__(self, shaders, gl_primitive):
        self.shaders_program = make_shader_program(**shaders)

        self.ins_loc = {}
        self.ins_size = {}
        self.ins_type = {}
        self.uniforms_loc = {}
        self.uniforms_setters = {}
        self.uniforms_val = {}
        self.parse_shader_var(shaders['vertex'])
        self.gl_primitive = gl_primitive
    
    def parse_shader_var(self, vertex_code):
        in_var = parse_shader(vertex_code)
        for a in in_var['in']:
            a_type, a_name, a_size = a
            self.ins_loc[a_name] =\
                gl.glGetAttribLocation(self.shaders_program, a_name)
            self.ins_size[a_name],\
                self.ins_type[a_name] = in_size(a_type)
        self.in_stride = 4*sum(self.ins_size.values())

        for u in in_var['uniform']:
            u_type, u_name, u_size = u
            self.uniforms_loc[u_name] =\
                gl.glGetUniformLocation(self.shaders_program, u_name)
            self.uniforms_setters[u_name] =\
                uniform_setter(u_type, u_name, u_size)

    def set_vbo(self, data):
        self.vbo = glvbo.VBO(data, usage='GL_STATIC_DRAW_ARB')

    def set_uniform(self, name, value):
        if name not in self.uniforms_loc:
            raise RuntimeError("unknown uniform")
        self.uniforms_val[name] = value

    def draw(self):
        self.vbo.bind()
        for a in self.ins_loc:
            gl.glEnableVertexAttribArray(self.ins_loc[a])
        offset = 0
        for a in self.ins_loc:
            gl.glVertexAttribPointer(self.ins_loc[a],
                                     self.ins_size[a],
                                     self.ins_type[a],
                                     gl.GL_FALSE,
                                     self.in_stride,
                                     self.vbo + offset)
            offset += 4*self.ins_size[a]

        gl.glUseProgram(self.shaders_program)
        for u in self.uniforms_loc:
            self.uniforms_setters[u](self.uniforms_loc[u],
                                     self.uniforms_val[u])

        gl.glDrawArrays(self.gl_primitive, 0, len(self.vbo.data))
        self.vbo.unbind()


class Sticks(ChochinPrimitiveArray):
    s_vert = """
    #version 150 core

    // Uniforms
    uniform float u_scale;
    uniform vec3 u_push;
    uniform float u_active_layers[12];
    uniform mat3 u_rotation;

    in vec3 a_position;
    in float a_layer;
    in vec4 a_color;
    in float a_thickness;

    out vec4 color;
    out float v_discard;
    out float v_thickness;

    void main (void) {
        v_discard = u_active_layers[int(a_layer)];
        color  = a_color;
        gl_Position = vec4((u_rotation*a_position+u_push)*u_scale,1.0);
        v_thickness = u_scale*a_thickness;
    }
    """

    s_geom = """
    #version 150 core

    layout(lines) in;
    layout(triangle_strip, max_vertices = 4) out;

    in vec4 color[];
    in float v_discard[];
    in float v_thickness[];

    out vec4 fcolor;

    void main()
    {
        if (v_discard[0] > 0.1) {
            fcolor = color[0];
            vec4 n = gl_in[1].gl_Position-gl_in[0].gl_Position;
            vec4 u = vec4(n.y, -n.x, 0, 0);
            float lu = length(u);
            if (lu > 0) {
                u = (0.5*v_thickness[0]/lu)*u;
                gl_Position = gl_in[0].gl_Position + u;
                EmitVertex();
                gl_Position = gl_in[0].gl_Position - u;
                EmitVertex();
                gl_Position = gl_in[1].gl_Position + u;
                EmitVertex();
                gl_Position = gl_in[1].gl_Position - u;
                EmitVertex();
                EndPrimitive();
            }
        }
    }
    """

    s_frag = """
    #version 150 core

    in vec4 fcolor;

    void main()
    {
        gl_FragColor = fcolor;
    }
    """

    def __init__(self):
        shaders = {'vertex': self.s_vert,
                   'fragment': self.s_frag,
                   'geometry': self.s_geom}
        ChochinPrimitiveArray.__init__(self,
                                       shaders,
                                       gl.GL_LINES)

    def set_data(self, line_ends, thicknesses, colors, layers):
        line_ends = line_ends.reshape((-1, 3))
        colors = np.repeat(colors, 2, axis=0)
        layers = np.repeat(layers, 2, axis=0)
        thicknesses = np.repeat(thicknesses, 2, axis=0)
        vbo_data = np.column_stack((line_ends,
                                    colors,
                                    layers,
                                    thicknesses)).astype(np.float32)
        self.set_vbo(vbo_data)
        self.ins = ['a_position', 'a_color', 'a_layer', 'a_thickness']




class Circles(ChochinPrimitiveArray):
    # shaders credit VisPy https://github.com/vispy/vispy (cloud.py example)
    c_vert = """
    #version 150 core

    // Uniforms
    // ------------------------------------
    uniform float u_linewidth;
    uniform float u_antialias;
    uniform float u_scale;
    uniform float u_rad_scale;
    uniform mat3 u_rotation;
    uniform vec3 u_push;
    uniform float u_reality;
    uniform float u_active_layers[12];

    // ins
    // ------------------------------------
    in vec3  a_position;
    in vec4  a_color;
    in float a_size;
    in float a_layer;

    // Varyings
    // ------------------------------------
    out vec4 v_fg_color;
    out vec4 v_bg_color;
    out float v_size;
    out float v_linewidth;
    out float v_antialias;
    out float v_discard;

    void main (void) {
        v_size = a_size*u_rad_scale*u_scale;
        v_linewidth = u_linewidth;
        v_antialias = u_antialias;
        if (u_reality == 1.) {
            v_fg_color  = vec4(0, 0, 0, 1);
        } else {
            v_fg_color  = a_color;
        }
        v_bg_color  = a_color;
        v_discard = u_active_layers[int(a_layer)];
        gl_Position = vec4((u_rotation*a_position+u_push)*u_scale,1.0);
        gl_PointSize = v_size + 2*(v_linewidth + 1.5*v_antialias);
    }
    """

    c_frag = """
    #version 150 core

    // Constants
    // ------------------------------------


    // Varyings
    // ------------------------------------
    in vec4 v_fg_color;
    in vec4 v_bg_color;
    in float v_size;
    in float v_linewidth;
    in float v_antialias;
    in float v_discard;

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
        if (v_discard < 0.1) {
            discard;
        }
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
        shaders = {'vertex': self.c_vert,
                   'fragment': self.c_frag}
        ChochinPrimitiveArray.__init__(self,
                                       shaders,
                                       gl.GL_POINTS)

    def set_data(self, centers, radii, colors, layers):
        n = centers.shape[0]
        data_c = np.zeros((n, 9), dtype=np.float32)
        data_c[:, :3] = centers
        data_c[:, 3:7] = colors
        data_c[:, 7] = radii
        data_c[:, 8] = layers
        self.set_vbo(data_c)
        self.ins = ['a_position',
                           'a_color',
                           'a_size',
                           'a_layer']


class Lines(ChochinPrimitiveArray):
    vert = """
    #version 150 core

    // Uniforms
    uniform float u_scale;
    uniform vec3 u_push;
    uniform float u_active_layers[12];
    uniform mat3 u_rotation;

    // ins
    in vec3  a_position;
    in vec4  a_fg_color;
    in float a_layer;

    out vec4 v_fg_color;
    out float v_discard;

    void main (void) {
        v_discard = u_active_layers[int(a_layer)];
        v_fg_color  = a_fg_color;
        gl_Position = vec4((u_rotation*a_position+u_push)*u_scale,1.0);
    }
    """

    frag = """
    #version 150 core

    in vec4 v_fg_color;
    in float v_discard;

    void main()
    {
        if (v_discard < 0.1) {
            discard;
        }
       gl_FragColor = v_fg_color;
    }
    """

    def __init__(self):
        shaders = {'vertex': self.vert,
                   'fragment': self.frag}
        ChochinPrimitiveArray.__init__(self,
                                       shaders,
                                       gl.GL_LINES)

    def set_data(self, line_ends, colors, layers):
        line_ends = line_ends.reshape((-1, 3))
        colors = np.repeat(colors, 2, axis=0)
        layers = np.repeat(layers, 2, axis=0)
        vbo_data = np.column_stack((line_ends,
                                    colors,
                                    layers)).astype(np.float32)
        self.set_vbo(vbo_data)
        self.ins = ['a_position', 'a_fg_color', 'a_layer']
