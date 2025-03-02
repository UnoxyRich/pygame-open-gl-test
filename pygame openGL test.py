import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math

vertices = [
    [1, 1, -1],
    [1, -1, -1],
    [-1, -1, -1],
    [-1, 1, -1],
    [1, 1, 1],
    [1, -1, 1],
    [-1, -1, 1],
    [-1, 1, 1]
]

edges = [
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 0),
    (4, 5),
    (5, 6),
    (6, 7),
    (7, 4),
    (0, 4),
    (1, 5),
    (2, 6),
    (3, 7)
]

def Cube():
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

def Torus(inner_radius, outer_radius, sides, rings):
    ring_step = 2 * math.pi / rings
    side_step = 2 * math.pi / sides

    for i in range(rings):
        glBegin(GL_QUAD_STRIP)
        for j in range(sides + 1):
            for k in range(2):
                s = (i + k) % rings + 0.5
                t = j % sides

                x = (outer_radius + inner_radius * math.cos(s * ring_step)) * math.cos(t * side_step)
                y = (outer_radius + inner_radius * math.cos(s * ring_step)) * math.sin(t * side_step)
                z = inner_radius * math.sin(s * ring_step)

                glVertex3f(x, y, z)
        glEnd()

def create_shadow_map():
    shadow_width, shadow_height = 1024, 1024
    depth_map_fbo = glGenFramebuffers(1)
    depth_map = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, depth_map)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT, shadow_width, shadow_height, 0, GL_DEPTH_COMPONENT, GL_FLOAT, None)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
    border_color = [1.0, 1.0, 1.0, 1.0]
    glTexParameterfv(GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, border_color)
    glBindFramebuffer(GL_FRAMEBUFFER, depth_map_fbo)
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, depth_map, 0)
    glDrawBuffer(GL_NONE)
    glReadBuffer(GL_NONE)
    glBindFramebuffer(GL_FRAMEBUFFER, 0)
    return depth_map_fbo, depth_map

def render_scene():
    Cube()
    Torus(0.3, 0.7, 30, 30)

def main():
    pygame.init()
    display = (800, 600)
    
    #attributes for anti-aliasing
    pygame.display.gl_set_attribute(GL_MULTISAMPLEBUFFERS, 1)
    pygame.display.gl_set_attribute(GL_MULTISAMPLESAMPLES, 4)
    
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -5)

    rotation_angle = 0
    rotation_speed = 1
    z_rotation_angle = 0
    z_rotation_speed = 2

    depth_map_fbo, depth_map = create_shadow_map()

    #multi-sampling
    glEnable(GL_MULTISAMPLE)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    rotation_speed += 1
                elif event.key == pygame.K_DOWN:
                    rotation_speed -= 1

        rotation_angle += rotation_speed
        z_rotation_angle += z_rotation_speed

        light_pos = [2.0, 4.0, -2.0]

        #depth map
        glBindFramebuffer(GL_FRAMEBUFFER, depth_map_fbo)
        glViewport(0, 0, 1024, 1024)
        glClear(GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, 1.0, 1.0, 7.5)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(light_pos[0], light_pos[1], light_pos[2], 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)
        render_scene()
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

        # Render from camera
        glViewport(0, 0, display[0], display[1])
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0.0, 0.0, -5)
        glRotatef(rotation_angle, 3, 1, 1)
        glRotatef(z_rotation_angle, 0, 0, 1)
        render_scene()
        pygame.display.flip()
        pygame.time.wait(10)

if __name__ == "__main__":
    main()