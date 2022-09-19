import math
import random
import traceback
import dearpygui.dearpygui as dpg
from scipy.interpolate import splprep, splev
import numpy as np

dpg.create_context()

NUM_PARAMETRIC_CURVE_POINTS = 10000

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
    try:
        dpg.delete_item('compute_circle')
    except SystemError:
        pass
    try:
        dpg.delete_item('compute_line')
    except SystemError:
        pass
    drag_points = []
    undo_order = []
    draw_plot_limits()


def editor_compute():
    i_x_y_theta = compute()
    if len(i_x_y_theta) > 0:
        index_series = [data[0] for data in i_x_y_theta]
        x_series = [data[1] for data in i_x_y_theta]
        y_series = [data[2] for data in i_x_y_theta]
        # theta_series = [data[3] for data in i_x_y_theta]

        dpg.configure_item('2d_preview_x_curve', x=index_series, y=x_series)
        dpg.configure_item('2d_preview_y_curve', x=index_series, y=y_series)


def compute():
    global editor_curve_x
    global editor_curve_y

    step_size = 1

    data = []
    if len(editor_curve_x):
        if len(editor_curve_y):
            index_t = 0
            while index_t < NUM_PARAMETRIC_CURVE_POINTS:
                x = editor_curve_x[index_t]
                y = editor_curve_y[index_t]
                theta = math.degrees(math.atan(y/x))
                quadrant = point_quadrant((x, y))
                if quadrant == 2 or quadrant == 3:
                    theta += 180
                elif quadrant == 4:
                    theta += 360
                data.append((index_t, x, y, theta))

                index_t += step_size
    return data


def point_quadrant(point):
    x = point[0]
    y = point[1]
    if x >= 0 and y >= 0:
        quadrant = 1
    elif x < 0 and y >= 0:
        quadrant = 2
    elif x < 0 and y < 0:
        quadrant = 3
    else:
        quadrant = 4
    return quadrant


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
    if len(drag_points) > 1:
        dpg.delete_item(drag_points[undo_order[-1]])
        drag_points.pop(undo_order.pop())


def editor_draw_curve():
    global drag_points

    if len(drag_points) >= 3:
        global editor_curve_x
        global editor_curve_y

        a = [np.asanyarray([dpg.get_value(i)[0], dpg.get_value(i)[1]]) for i in drag_points]
        a.append(np.asanyarray(
            [dpg.get_value(drag_points[0])[0], dpg.get_value(drag_points[0])[1]]))
        arr = np.asanyarray(a)

        tck, u = splprep(arr.T, per=True, s=0)
        u_new = np.linspace(u.min(), u.max(), NUM_PARAMETRIC_CURVE_POINTS)

        editor_curve_x, editor_curve_y = splev(u_new, tck, der=0)

        dpg.configure_item('editor_curve', x=editor_curve_x, y=editor_curve_y)
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


def draw_plot_limits():
    x = (-1, 1, 1, -1, -1)
    y = (1, 1, -1, -1, 1)
    dpg.configure_item('editor_curve', x=x, y=y)


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
            dpg.add_button(label='Compute', callback=editor_compute)
            dpg.add_button(label='Random Points', callback=editor_random_drag_points)

    with dpg.window(tag='2d_preview', label='2D Preview'):
        with dpg.plot(tag='2d_preview_plot', pan_button=dpg.mvMouseButton_Middle, fit_button=dpg.mvMouseButton_Middle):
            dpg.add_plot_legend()
            dpg.add_plot_annotation()

            dpg.add_plot_axis(dpg.mvXAxis, tag='2d_preview_x_axis')
            dpg.add_plot_axis(dpg.mvYAxis, tag='2d_preview_y_axis')
            dpg.add_line_series(x=[], y=[], tag='2d_preview_x_curve',
                                parent='2d_preview_y_axis', label='x displacement')
            dpg.add_line_series(x=[], y=[], tag='2d_preview_y_curve',
                                parent='2d_preview_y_axis', label='y displacement')

    with dpg.window(tag='3d_preview', label='3D Preview'):
        pass


def resize_plots():
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


dpg.configure_app(init_file='dpg.ini', docking=True, docking_space=True)
dpg.create_viewport(title='Cam Draw')
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window('primary_window', True)

draw_count = 0
while dpg.is_dearpygui_running():
    resize_plots()

    editor_draw_curve()
    editor_draw_closest_point()
    try:
        editor_draw_closest_points()
    except Exception as e:
        print(traceback.format_exc())

    editor_compute()

    dpg.render_dearpygui_frame()

dpg.destroy_context()
