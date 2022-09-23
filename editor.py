import random
import dearpygui.dearpygui as dpg
import numpy as np
from scipy.interpolate import splprep, splev

NUM_P = 10000


class EditorPlot:
    def __init__(self, **options):

        self._drag_point_tags = []
        self._undo_order = []

        self._p_curve = []

        self._height = 0
        self._width = 0

        plot_options = {
            'tag': 'editor_plot',
            'pan_button': dpg.mvMouseButton_Middle,
            'fit_button': dpg.mvMouseButton_Middle,
            'no_menus': True,
            'no_box_select': True,
            'anti_aliased': True
        }

        with dpg.window(tag='editor_window', **options):
            with dpg.plot(**plot_options):
                dpg.add_plot_legend()
                dpg.add_plot_annotation()

                dpg.add_plot_axis(dpg.mvXAxis, tag='editor_plot_x_axis')
                dpg.add_plot_axis(dpg.mvYAxis, tag='editor_plot_y_axis')

                dpg.add_line_series(x=[], y=[], tag='editor_plot_curve',
                                    parent='editor_plot_y_axis')

                x, y = [-1, 1, 1, -1, -1], [1, 1, -1, -1, 1]
                dpg.add_line_series(x=x, y=y, parent='editor_plot_y_axis')
            with dpg.group(horizontal=True):
                dpg.add_button(label='Clear', callback=self.clear_plot)
                dpg.add_button(label='Random', callback=self.add_random_points)

        with dpg.item_handler_registry(tag='editor_plot_handler'):
            dpg.add_item_clicked_handler(dpg.mvMouseButton_Left, callback=self.on_left_click)
            dpg.add_item_clicked_handler(dpg.mvMouseButton_Right, callback=self.on_right_click)
            dpg.bind_item_handler_registry('editor_plot', 'editor_plot_handler')

    def clear_plot(self) -> None:
        """clears drag point list and plot"""
        for drag_point in self._drag_point_tags:
            if dpg.does_alias_exist(drag_point):
                dpg.delete_item(drag_point)
        dpg.configure_item('editor_plot_curve', x=[], y=[])
        self._drag_point_tags = []
        self._undo_order = []

    def on_left_click(self) -> None:
        """left mouse button click callback. Adds drag point if cursor is at a valid position"""
        mouse_pos = dpg.get_plot_mouse_pos()
        if abs(mouse_pos[0]) <= 1 and abs(mouse_pos[1]) <= 1:
            self.add_drag_point(mouse_pos)

    def on_right_click(self) -> None:
        """right mouse button click callback. Adds drag point between 
        closest consecutive drag points if cursor is at a valid position"""
        if self.n_drag >= 3:
            mouse_pos = dpg.get_plot_mouse_pos()
            p_curve = self.compute_p_curve()
            closest_index = self.closest_point_index(mouse_pos, p_curve)
            closest_curve_point = (p_curve[0][closest_index], p_curve[1][closest_index])

            i1, i2 = self.closest_points_indexes_along_curve(
                closest_curve_point, self.drag_point_coordinates(), p_curve)

            print(closest_index, i1, i2)

    def update_plot_curve(self) -> None:
        """computes parametric spline and updates plot"""
        if len(self._drag_point_tags) >= 3:
            curve = self.compute_p_curve()
            dpg.configure_item('editor_plot_curve', x=curve[0], y=curve[1])

    def closest_point_index(
            self, point: list | tuple, curve: list[np.ndarray] | list[tuple]) -> int:
        """calculate index of closest point to curve

        :param point: point coordinate
        :type point: list | tuple
        :param curve: curve to calculate from
        :type curve: list[np.ndarray]
        :return: closest point index within curve
        :rtype: int
        """
        min_index = 0
        if isinstance(curve, list):
            if isinstance(curve[0], np.ndarray):
                num_p = curve[0].shape[0]
                if num_p > 0:
                    dx = point[0] - curve[0][0]
                    dy = point[1] - curve[1][0]
                    d = (dx * dx) + (dy * dy)
                    min_d = d
                    index = 1
                    while index < num_p:
                        dx = point[0] - curve[0][index]
                        dy = point[1] - curve[1][index]
                        d = (dx * dx) + (dy * dy)
                        if d < min_d:
                            min_d = d
                            min_index = index
                        index += 1
            else:
                num_p = len(curve)
                if num_p > 0:
                    dx = point[0] - curve[0][0]
                    dy = point[1] - curve[0][1]
                    d = (dx * dx) + (dy * dy)
                    min_d = d
                    index = 1
                    while index < num_p:
                        dx = point[0] - curve[index][0]
                        dy = point[1] - curve[index][1]
                        d = (dx * dx) + (dy * dy)
                        if d < min_d:
                            min_d = d
                            min_index = index
                        index += 1

        return min_index

    def closest_points_indexes_along_curve(
            self, point: list | tuple, points: list | tuple, curve: list[np.ndarray] | list[tuple]):
        step_size = 1
        found_threshold = 1e-4

        i1 = None
        i2 = None

        i1_found = False
        i2_found = False

        if isinstance(curve, list):
            curve_point_index = self.closest_point_index(point, curve)
            if isinstance(curve[0], np.ndarray):
                curve_len = curve[0].shape[0]
                search_index = curve_point_index
                while search_index < curve_len and not i1_found:
                    curve_test_point = (curve[0][search_index], curve[1][search_index])
                    self.animate_circle(curve_test_point, 0.02)
                    drag_point_index = self.closest_point_index(curve_test_point, points)
                    drag_point = points[drag_point_index]
                    self.animate_circle(drag_point, 0.02, (255, 0, 0))
                    dx = curve_test_point[0] - drag_point[0]
                    dy = curve_test_point[1] - drag_point[1]
                    distance = (dx * dx) + (dy * dy)
                    print(curve_test_point, distance, drag_point, search_index)
                    if distance < found_threshold:
                        i1 = drag_point_index
                        i1_found = True
                    search_index += step_size

        return i1, i2

    def animate_circle(self, center, radius, color=(255, 255, 255)):
        with dpg.mutex():
            if dpg.does_alias_exist('animation_circle'):
                dpg.delete_item('animation_circle')
            dpg.draw_circle(center=center, radius=radius, color=color,
                            tag='animation_circle', parent='editor_plot')

    def compute_p_curve(self) -> list[np.ndarray] | None:
        """return list of ndarrays containing coordinates

        ex: curve[0][2] = 3rd x value

        :return: list of coordinates
        :rtype: list[ndarray]
        """
        if len(self._drag_point_tags) >= 3:
            drag_coords = [np.asanyarray([dpg.get_value(i)[0], dpg.get_value(i)[1]])
                           for i in self._drag_point_tags]
            drag_coords.append(drag_coords[0])
            drag_coords = np.asanyarray(drag_coords)

            tck, u = splprep(drag_coords.T, per=True, s=0)
            u_new = np.linspace(u.min(), u.max(), NUM_P)

            self._p_curve = splev(u_new, tck, der=0)
        return self._p_curve

    @property
    def n_drag(self) -> None:
        """return number of drag points"""
        return len(self._drag_point_tags)

    def drag_point_coordinates(self) -> list[tuple]:
        """return list of drag point coordinates"""
        return [(dpg.get_value(i)[0], dpg.get_value(i)[1]) for i in self._drag_point_tags]

    def drag_point_move(self):
        """updates plot curve when any drag point is moved"""
        self.update_plot_curve()

    def add_drag_point(self, position: list | tuple, index=None) -> None:
        """add new drag point to editor plot

        :param position: new drag point coordinate
        :type position: list or tuple
        :param index: index to add new drag point before, defaults to None
        :type index: int, optional
        """
        num_drag_points = len(self._drag_point_tags)
        dpg.add_drag_point(
            parent='editor_plot',
            tag=f'dp{num_drag_points}',
            label=num_drag_points,
            show_label=True,
            default_value=position,
            callback=self.drag_point_move
        )
        if index is None:
            self._drag_point_tags.append(f'dp{num_drag_points}')
            self._undo_order.append(-1)
        else:
            self._drag_point_tags.insert(index, f'dp{num_drag_points}')
            self._drag_point_tags.append(index)
        self.update_plot_curve()

    def add_random_points(self) -> None:
        """add 10 drag points at random positions"""
        for i in range(10):
            x = (random.random() * 2) - 1
            y = (random.random() * 2) - 1
            self.add_drag_point((x, y))

    def add_square(self) -> None:
        pass

    def add_circle(self) -> None:
        pass

    def resize(self) -> None:
        """resize editor plot based on window size"""
        new_height = dpg.get_item_height('editor_window') - 59
        new_width = dpg.get_item_width('editor_window') - 17
        if self._height != new_height or self._width != new_width:
            dpg.configure_item(item='editor_plot', height=new_height, width=new_width)
            self._height = new_height
            self._width = new_width
