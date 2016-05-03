c_vert = """
#version 120

// Uniforms
// ------------------------------------
uniform float u_linewidth;
uniform float u_antialias;
uniform float u_size;

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
    v_size = a_size * u_size;
    v_linewidth = u_linewidth;
    v_antialias = u_antialias;
    v_fg_color  = a_fg_color;
    v_bg_color  = a_bg_color;
    gl_Position = vec4(a_position,1.0);
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

s_vert = """
attribute vec3 a_position;
attribute vec4 a_fg_color;

varying vec4 v_fg_color;

void main (void) {
    gl_Position = vec4(a_position,1.0);
    v_fg_color  = a_fg_color;
}
"""

s_frag = """
varying vec4 v_fg_color;

void main()
{
    gl_FragColor = v_fg_color;
}
"""

c_vert_2 = """
#version 120
attribute vec3 a_position;
attribute vec4 a_fg_color;

varying vec4 v_fg_color;

void main (void) {
    gl_Position = vec4(a_position,1.0);
    gl_PointSize = 100.;
    v_fg_color  = a_fg_color;
}
"""

c_frag_2 = """
#version 120
varying vec4 v_fg_color;

void main()
{
    vec2 pos = gl_PointCoord.xy - vec2(0.5, 0.5);
    float dist_squared = dot(pos, pos);
    //if (dist_squared < 0.2) {
        gl_FragColor = v_fg_color;
//    } else {
//        discard;
//    }
}
"""
