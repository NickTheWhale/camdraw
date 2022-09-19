import dearpygui.dearpygui as dpg
import math

dpg.create_context()
dpg.create_viewport()
dpg.setup_dearpygui()

size = 5
verticies = [
        [-size, -size, -size],  # 0 near side
        [ size, -size, -size],  # 1
        [-size,  size, -size],  # 2
        [ size,  size, -size],  # 3
        [-size, -size,  size],  # 4 far side
        [ size, -size,  size],  # 5
        [-size,  size,  size],  # 6
        [ size,  size,  size],  # 7
        [-size, -size, -size],  # 8 left side
        [-size,  size, -size],  # 9
        [-size, -size,  size],  # 10
        [-size,  size,  size],  # 11
        [ size, -size, -size],  # 12 right side
        [ size,  size, -size],  # 13
        [ size, -size,  size],  # 14
        [ size,  size,  size],  # 15
        [-size, -size, -size],  # 16 bottom side
        [ size, -size, -size],  # 17
        [-size, -size,  size],  # 18
        [ size, -size,  size],  # 19
        [-size,  size, -size],  # 20 top side
        [ size,  size, -size],  # 21
        [-size,  size,  size],  # 22
        [ size,  size,  size],  # 23
    ]

colors = [
        [255,   0,   0, 150],
        [255, 255,   0, 150],
        [255, 255, 255, 150],
        [255,   0, 255, 150],
        [  0, 255,   0, 150],
        [  0, 255, 255, 150],
        [  0,   0, 255, 150],
        [  0, 125,   0, 150],
        [128,   0,   0, 150],
        [128,  70,   0, 150],
        [128, 255, 255, 150],
        [128,   0, 128, 150]
    ]

x_rot = 0
y_rot = 0
z_rot = 0

def rotate(sender, data, user_data):
    global x_rot
    global y_rot
    global z_rot
    
    if user_data == 'x':
        x_rot = data
    elif user_data == 'y':
        y_rot = data
    else:
        z_rot = data
    

with dpg.window(label="tutorial", width=550, height=550):
    dpg.add_slider_int(label='x rotation', user_data='x', min_value=-180, max_value=180, callback=rotate)
    dpg.add_slider_int(label='y rotation', user_data='y', min_value=-180, max_value=180, callback=rotate)
    dpg.add_slider_int(label='z rotation', user_data='z', min_value=-180, max_value=180, callback=rotate)
    with dpg.drawlist(width=500, height=500):

        with dpg.draw_layer(tag="main pass", depth_clipping=True, perspective_divide=True, cull_mode=dpg.mvCullMode_Back):

            with dpg.draw_node(tag="cube"):

                # dpg.draw_triangle(verticies[1],  verticies[2],  verticies[0], color=[0,0,0.0],  fill=colors[0])
                # dpg.draw_triangle(verticies[1],  verticies[3],  verticies[2], color=[0,0,0.0],  fill=colors[1])
                # dpg.draw_triangle(verticies[7],  verticies[5],  verticies[4], color=[0,0,0.0],  fill=colors[2])
                # dpg.draw_triangle(verticies[6],  verticies[7],  verticies[4], color=[0,0,0.0],  fill=colors[3])
                # dpg.draw_triangle(verticies[9],  verticies[10], verticies[8], color=[0,0,0.0],  fill=colors[4])
                # dpg.draw_triangle(verticies[9],  verticies[11], verticies[10], color=[0,0,0.0], fill=colors[5])
                # dpg.draw_triangle(verticies[15], verticies[13], verticies[12], color=[0,0,0.0], fill=colors[6])
                # dpg.draw_triangle(verticies[14], verticies[15], verticies[12], color=[0,0,0.0], fill=colors[7])
                # dpg.draw_triangle(verticies[18], verticies[17], verticies[16], color=[0,0,0.0], fill=colors[8])
                # dpg.draw_triangle(verticies[19], verticies[17], verticies[18], color=[0,0,0.0], fill=colors[9])
                # dpg.draw_triangle(verticies[21], verticies[23], verticies[20], color=[0,0,0.0], fill=colors[10])
                # dpg.draw_triangle(verticies[23], verticies[22], verticies[20], color=[0,0,0.0], fill=colors[11])

                # dpg.draw_circle([0, 0, 0], 5)
                dpg.draw_bezier_cubic((0, 0, 0), (3, -3, 5), (4, 5, 2), (5, 6, -8))
                
view = dpg.create_fps_matrix([0, 0, 50], 0.0, 0.0)
proj = dpg.create_perspective_matrix(math.pi*45.0/180.0, 1.0, 0.1, 100)

dpg.set_clip_space("main pass", 0, 0, 500, 500, -1.0, 1.0)

dpg.show_viewport()
while dpg.is_dearpygui_running():
    model = dpg.create_rotation_matrix(math.pi*x_rot/180.0 , [1, 0, 0])*\
                            dpg.create_rotation_matrix(math.pi*y_rot/180.0 , [0, 1, 0])*\
                            dpg.create_rotation_matrix(math.pi*z_rot/180.0 , [0, 0, 1])
    dpg.apply_transform("cube", proj*view*model)
    dpg.render_dearpygui_frame()

dpg.destroy_context()