import math
import random
import time
import dearpygui.dearpygui as dpg
from scipy.interpolate import splprep, splev
import numpy as np
from editor import EditorPlot

dpg.create_context()

NUM_PARAMETRIC_CURVE_POINTS = 10000
CIRCLE_RADIUS = 2
cam_scale = 1


CIRCLE_POINTS = []
for t in range(NUM_PARAMETRIC_CURVE_POINTS):
    y = CIRCLE_RADIUS * math.cos((2 * math.pi * t) / NUM_PARAMETRIC_CURVE_POINTS)
    z = CIRCLE_RADIUS * math.sin((2 * math.pi * t) / NUM_PARAMETRIC_CURVE_POINTS)
    CIRCLE_POINTS.append((y, z))

drag_points = []
editor_curve_x = []
editor_curve_y = []
last_drag_index = -1
undo_order = []


def editor_clear_plot():
    global drag_points
    global undo_order

    x, y = [], []
    dpg.configure_item('editor_curve', x=x, y=y)

    for drag_point in drag_points:
        dpg.delete_item(drag_point)

    try:
        dpg.delete_item('editor_closet_point_circle')
    except SystemError:
        pass
    try:
        dpg.delete_item('first_point_circle')
    except SystemError:
        pass
    try:
        dpg.delete_item('second_point_circle')
    except SystemError:
        pass

    drag_points = []
    undo_order = []


def preview_2d_draw():
    if len(editor_curve_x) > 0:
        index_series = [i for i in range(len(editor_curve_x))]

        dpg.configure_item('2d_preview_x_displacement', x=index_series, y=editor_curve_x)
        dpg.configure_item('2d_preview_y_displacement', x=index_series, y=editor_curve_y)


def editor_add_circle():
    editor_add_drag_point((1, 0))
    editor_add_drag_point((0, 1))
    editor_add_drag_point((-1, 0))
    editor_add_drag_point((0, -1))


def editor_add_square():
    s = 0.9
    editor_add_drag_point((s * 1,   1 * s))
    editor_add_drag_point((s * 0.9, 1 * s))
    editor_add_drag_point((s * 0.8, 1 * s))
    editor_add_drag_point((s * 0.7, 1 * s))

    editor_add_drag_point((s * -0.7, 1 * s))
    editor_add_drag_point((s * -0.8, 1 * s))
    editor_add_drag_point((s * -0.9, 1 * s))
    editor_add_drag_point((s * -1,   1 * s))

    editor_add_drag_point((s * -1,  0.9 * s))
    editor_add_drag_point((s * -1,  0.8 * s))
    editor_add_drag_point((s * -1,  0.7 * s))
    editor_add_drag_point((s * -1, -0.7 * s))

    editor_add_drag_point((s * -1,  -0.8 * s))
    editor_add_drag_point((s * -1,  -0.9 * s))
    editor_add_drag_point((s * -1,    -1 * s))
    editor_add_drag_point((s * -0.9,  -1 * s))

    editor_add_drag_point((s * -0.8, -1 * s))
    editor_add_drag_point((s * -0.7, -1 * s))
    editor_add_drag_point((s * 0.7,  -1 * s))
    editor_add_drag_point((s * 0.8,  -1 * s))

    editor_add_drag_point((s * 0.9, -1 * s))
    editor_add_drag_point((s * 1,   -1 * s))
    editor_add_drag_point((s * 1, -0.9 * s))
    editor_add_drag_point((s * 1, -0.8 * s))

    editor_add_drag_point((s * 1, -0.7 * s))
    editor_add_drag_point((s * 1,  0.7 * s))
    editor_add_drag_point((s * 1,  0.8 * s))
    editor_add_drag_point((s * 1,  0.9 * s))


def scale_cam(sender, data):
    global cam_scale
    cam_scale = data
    preview_3d_draw()


def preview_3d_draw():
    vertices = []
    if len(editor_curve_x) > 0:
        index_t = 0
        while index_t < len(editor_curve_x):

            dx = editor_curve_x[index_t]
            dy = editor_curve_y[index_t]

            y = CIRCLE_POINTS[index_t][0]
            z = CIRCLE_POINTS[index_t][1]

            V = (dx, y + ((dy * y) / CIRCLE_RADIUS), z + ((dy * z) / CIRCLE_RADIUS))

            V = (V[0] * cam_scale, V[1] * cam_scale, V[2] * cam_scale)

            vertices.append(V)

            index_t += 1

        index_series = [i for i in range(len(editor_curve_x))]

        x_series = [p[0] for p in vertices]
        y_series = [p[1] for p in vertices]
        z_series = [p[2] for p in vertices]

        dpg.configure_item('2d_preview_x_position', x=index_series, y=x_series)
        dpg.configure_item('2d_preview_y_position', x=index_series, y=y_series)
        dpg.configure_item('2d_preview_z_position', x=index_series, y=z_series)

        if dpg.does_alias_exist('x_line'):
            dpg.delete_item('x_line')
        if dpg.does_alias_exist('y_line'):
            dpg.delete_item('y_line')
        if dpg.does_alias_exist('z_line'):
            dpg.delete_item('z_line')

        dpg.draw_line((1, 0, 0), (-1, 0, 0), tag='x_line', parent='cam', color=(255, 0, 0))  # red
        dpg.draw_line((0, 1, 0), (0, -1, 0), tag='y_line', parent='cam', color=(0, 255, 0))  # green
        dpg.draw_line((0, 0, 1), (0, 0, -1), tag='z_line', parent='cam', color=(0, 0, 255))  # blue

        if dpg.does_alias_exist('cam_lines'):
            dpg.delete_item('cam_lines')
        dpg.draw_polygon(points=vertices, tag='cam_lines', parent='cam', color=(255, 255, 255))


def editor_add_drag_point(position, index=None):
    global drag_points
    global undo_order
    num_drag_points = len(drag_points)

    dpg.add_drag_point(
        parent='editor_plot',
        tag=f'dp{num_drag_points}',
        label=num_drag_points,
        show_label=True,
        default_value=position
    )
    if index is None:
        drag_points.append(f'dp{num_drag_points}')
        undo_order.append(-1)
    else:
        drag_points.insert(index, f'dp{num_drag_points}')
        undo_order.append(index)


def editor_plot_click_left():
    position = dpg.get_plot_mouse_pos()
    if abs(position[0]) <= 1:
        if abs(position[1]) <= 1:
            editor_add_drag_point(position)


def editor_plot_click_right():
    position = dpg.get_plot_mouse_pos()
    point, _, _ = editor_closest_point(position, editor_parametric_curve())
    if len(drag_points) >= 3:
        if point:
            i1, i2 = editor_two_closest_points(position)

            if i1 is not None and i2 is not None:
                insert_index = max(i1, i2)
                if (insert_index + 1 >= len(drag_points)) and min(i1, i2) == 0:
                    editor_add_drag_point(point)
                else:
                    editor_add_drag_point(point, insert_index)


def editor_undo_last_click():
    global drag_points
    global undo_order
    try:
        dpg.delete_item('editor_closet_point_circle')
    except SystemError:
        pass
    try:
        dpg.delete_item('first_point_circle')
    except SystemError:
        pass
    try:
        dpg.delete_item('second_point_circle')
    except SystemError:
        pass
    if len(drag_points) > 1:
        dpg.delete_item(drag_points[undo_order[-1]])
        drag_points.pop(undo_order.pop())


points = []


def editor_draw_curve():
    global drag_points

    if len(drag_points) >= 3:
        global editor_curve_x
        global editor_curve_y

        a = [np.asanyarray([dpg.get_value(i)[0], dpg.get_value(i)[1]]) for i in drag_points]
        a.append(np.asanyarray([dpg.get_value(drag_points[0])[0], dpg.get_value(drag_points[0])[1]]))
        arr = np.asanyarray(a)

        tck, u = splprep(arr.T, per=True, s=0)
        u_new = np.linspace(u.min(), u.max(), NUM_PARAMETRIC_CURVE_POINTS)

        editor_curve_x, editor_curve_y = splev(u_new, tck, der=0)

        dpg.configure_item('editor_curve', x=editor_curve_x, y=editor_curve_y)

        # for point in points:
        #     if dpg.does_alias_exist(point):
        #         dpg.delete_item(point)
        # for i in range(len(editor_curve_x)):
        #     dpg.draw_circle((editor_curve_x[i], editor_curve_y[i]), radius=0.01, parent='editor_plot', tag=f'circle{i}', color=(255, 0, 0))
        #     points.append(f'circle{i}')

    else:
        dpg.configure_item('editor_curve', x=[], y=[])


def editor_parametric_curve():
    global editor_curve_x
    global editor_curve_y

    if len(editor_curve_x) > 0:
        if len(editor_curve_y) > 0:
            return [(editor_curve_x[i], editor_curve_y[i]) for i in range(len(editor_curve_x))]


def editor_closest_point(position, curve):
    if curve is not None:
        number_of_points = len(curve)
        dx = position[0] - curve[0][0]
        dy = position[1] - curve[0][1]
        current_distance = (dx * dx) + (dy * dy)
        min_distance = current_distance
        min_distance_index = 0
        index = 1
        while index < number_of_points:
            dx = position[0] - curve[index][0]
            dy = position[1] - curve[index][1]
            current_distance = (dx * dx) + (dy * dy)
            if current_distance < min_distance:
                min_distance = current_distance
                min_distance_index = index
            index += 1
        closet_position = (curve[min_distance_index][0], curve[min_distance_index][1])
        return closet_position, min_distance, min_distance_index
    return None, None, None


def editor_random_drag_points():
    global drag_points
    for _ in range(10):
        x = random.random() * 2 - 1
        y = random.random() * 2 - 1
        editor_add_drag_point((x, y))


def editor_two_closest_points(point):
    global drag_points

    step_size = 1
    found_threshold = 1e-4

    first_point_index = None
    second_point_index = None

    parametric_curve = editor_parametric_curve()
    _, _, curve_point_index = editor_closest_point(point, parametric_curve)
    drag_point_coordinates = [(dpg.get_value(i)[0], dpg.get_value(i)[1]) for i in drag_points]
    if curve_point_index is not None:
        search_index = curve_point_index
        parametric_curve_length = len(parametric_curve)
        first_drag_point_found = False
        while search_index < parametric_curve_length and not first_drag_point_found:
            curve_test_point = parametric_curve[search_index]
            current_distances = distances_between_point_and_points(
                curve_test_point, drag_point_coordinates)
            if len(current_distances) > 0:
                min_distance = min(current_distances)
                if min_distance <= found_threshold:
                    first_point_index = current_distances.index(min_distance)
                    first_drag_point_found = True

            search_index += step_size

        if first_drag_point_found:
            search_index = curve_point_index
            second_drag_point_found = False
            while search_index > 0 and not second_drag_point_found:
                curve_test_point = parametric_curve[search_index]
                current_distances = distances_between_point_and_points(
                    curve_test_point, drag_point_coordinates)
                if len(current_distances) > 0:
                    min_distance = min(current_distances)
                    if min_distance <= found_threshold and current_distances.index(min_distance) != first_point_index:
                        second_point_index = current_distances.index(min_distance)
                        second_drag_point_found = True

                search_index -= step_size
    return first_point_index, second_point_index


def distances_between_point_and_points(point, points):
    number_of_points = len(points)
    index = 0
    distances = []
    while index < number_of_points:
        dx = point[0] - points[index][0]
        dy = point[1] - points[index][1]
        distance = (dx * dx) + (dy * dy)
        distances.append(distance)
        index += 1
    return distances


def editor_draw_closest_point():
    global drag_points
    closest_point, _, _ = editor_closest_point(dpg.get_plot_mouse_pos(), editor_parametric_curve())
    if closest_point:
        if len(drag_points) >= 3:
            try:
                dpg.delete_item('editor_closet_point_circle')
            except SystemError:
                pass

            dpg.draw_circle(
                center=closest_point, radius=0.025, tag='editor_closet_point_circle',
                parent='editor_plot', color=(0, 255, 0))


def editor_draw_closest_points():
    global drag_points
    drag_point_coordinates = [(dpg.get_value(i)[0], dpg.get_value(i)[1]) for i in drag_points]
    mouse_pos = dpg.get_plot_mouse_pos()
    i1, i2 = editor_two_closest_points(mouse_pos)
    if i1 is not None and i2 is not None:
        if len(drag_points) >= 3:
            try:
                dpg.delete_item('first_point_circle')
            except SystemError:
                pass
            try:
                dpg.delete_item('second_point_circle')
            except SystemError:
                pass

            dpg.draw_circle(drag_point_coordinates[i1], 0.03, color=(255, 0, 0),
                            parent='editor_plot', tag='first_point_circle')

            dpg.draw_circle(drag_point_coordinates[i2], 0.03, color=(255, 0, 0),
                            parent='editor_plot', tag='second_point_circle')


with dpg.window(tag='primary_window'):
    with dpg.window(tag='editor', label='Editor', horizontal_scrollbar=True):
        with dpg.plot(tag='editor_plot', pan_button=dpg.mvMouseButton_Middle, fit_button=dpg.mvMouseButton_Middle, no_menus=True, no_box_select=True, anti_aliased=True):
            dpg.add_plot_legend()
            dpg.add_plot_annotation()

            dpg.add_plot_axis(dpg.mvXAxis, tag='editor_x_axis')
            dpg.add_plot_axis(dpg.mvYAxis, tag='editor_y_axis')
            dpg.add_line_series(x=[], y=[], tag='editor_curve',
                                parent='editor_y_axis', label='curve')
            dpg.add_line_series(x=[-1, 1, 1, -1, -1], y=[1, 1, -1, -1, 1], parent='editor_y_axis')

            with dpg.item_handler_registry(tag='editor_plot_handler'):
                dpg.add_item_clicked_handler(dpg.mvMouseButton_Left,
                                             callback=editor_plot_click_left)
                dpg.add_item_clicked_handler(dpg.mvMouseButton_Right,
                                             callback=editor_plot_click_right)
                dpg.bind_item_handler_registry('editor_plot', 'editor_plot_handler')

        with dpg.group(horizontal=True):
            dpg.add_button(label='Clear', callback=editor_clear_plot)
            dpg.add_button(label='Undo', callback=editor_undo_last_click)
            dpg.add_button(label='Compute', callback=preview_3d_draw)
            dpg.add_button(label='Random Points', callback=editor_random_drag_points)
            dpg.add_button(label='Add Circle', callback=editor_add_circle)
            dpg.add_button(label='Add Square', callback=editor_add_square)

    with dpg.window(tag='2d_preview', label='2D Preview'):
        with dpg.plot(tag='2d_preview_plot', pan_button=dpg.mvMouseButton_Middle, fit_button=dpg.mvMouseButton_Middle):
            dpg.add_plot_legend()
            dpg.add_plot_annotation()

            dpg.add_plot_axis(dpg.mvXAxis, tag='2d_preview_x_axis')
            dpg.add_plot_axis(dpg.mvYAxis, tag='2d_preview_y_axis')

            dpg.add_line_series(x=[], y=[], tag='2d_preview_x_displacement',
                                parent='2d_preview_y_axis', label='x displacement')

            dpg.add_line_series(x=[], y=[], tag='2d_preview_y_displacement',
                                parent='2d_preview_y_axis', label='y displacement')

            dpg.add_line_series(x=[], y=[], tag='2d_preview_x_position',
                                parent='2d_preview_y_axis', label='x position')

            dpg.add_line_series(x=[], y=[], tag='2d_preview_y_position',
                                parent='2d_preview_y_axis', label='y position')

            dpg.add_line_series(x=[], y=[], tag='2d_preview_z_position',
                                parent='2d_preview_y_axis', label='z position')

    with dpg.window(tag='3d_preview', label='3D Preview'):
        dpg.add_slider_float(label='Scale', min_value=0, max_value=5,
                             default_value=cam_scale, callback=scale_cam)
        with dpg.drawlist(width=1, height=1, tag='3d_preview_drawlist'):

            with dpg.draw_layer(tag="main pass", depth_clipping=False, perspective_divide=True, cull_mode=dpg.mvCullMode_Back):

                with dpg.draw_node(tag="cam"):
                    pass

def resize():
    dpg.configure_item(
        item='editor_plot',
        height=dpg.get_item_height('editor') - 59,
        width=dpg.get_item_width('editor') - 17
    )
    dpg.configure_item(
        item='2d_preview_plot',
        height=dpg.get_item_height('2d_preview') - 59,
        width=dpg.get_item_width('2d_preview') - 17
    )
    dpg.configure_item(
        item='3d_preview_drawlist',
        height=dpg.get_item_height('3d_preview') - 59,
        width=dpg.get_item_width('3d_preview') - 17
    )

    w = dpg.get_item_width('3d_preview')
    h = dpg.get_item_height('3d_preview')

    dpg.set_clip_space("main pass", 0, -h//8, w, h//1.2, -1.0, 1.0)


dpg.configure_app(init_file='dpg.ini', docking=True, docking_space=True)
dpg.create_viewport()
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window('primary_window', True)

view = dpg.create_fps_matrix([0, 0, 15], 0.0, 0.0)
proj = dpg.create_perspective_matrix(math.pi*45.0/180.0, 1.0, 0.1, 100)

z_rot = 0
x_rot = 70
y_rot = 0

start = time.time()
fpss = []
while dpg.is_dearpygui_running():
    resize()

    editor_draw_curve()

    # editor_draw_closest_point()
    # editor_draw_closest_points()

    preview_2d_draw()
    preview_3d_draw()

    model = dpg.create_rotation_matrix(math.pi*x_rot/180.0, [1, 0, 0]) *\
        dpg.create_rotation_matrix(math.pi*y_rot/180.0, [0, 1, 0]) *\
        dpg.create_rotation_matrix(math.pi*z_rot/180.0, [0, 0, 1])

    z_rot += 1
    if z_rot > 360:
        z_rot = 0

    dpg.apply_transform("cam", proj*view*model)

    dpg.render_dearpygui_frame()

    delta = time.time() - start
    if delta > 0:
        fps = 1 / (time.time() - start)

        fpss.append(fps)
        if len(fpss) > 20:
            fpss.pop(0)

        fps_sum = 0
        for fps in fpss:
            fps_sum += fps

        fps_average = fps_sum / len(fpss)

        dpg.set_viewport_title(f'Cam Draw {fps_average:0.1f}')

    start = time.time()

dpg.destroy_context()
