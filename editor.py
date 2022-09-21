import dearpygui.dearpygui as dpg
import numpy as np
from scipy.interpolate import splprep, splev
from scipy.spatial import cKDTree


class EditorPlot:
    def __init__(self, **options):

        self._drag_point_tags = []
        self._undo_order = []

        self._p_curve = np.array([[0, 0], [0, 0]])

        self._tree = cKDTree(self._p_curve)

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
                dpg.add_button(label='query', callback=self.closest_point)

        with dpg.item_handler_registry(tag='editor_plot_handler'):
            dpg.add_item_clicked_handler(dpg.mvMouseButton_Left, callback=self.on_left_click)
            dpg.add_item_clicked_handler(dpg.mvMouseButton_Right, callback=self.on_right_click)
            dpg.bind_item_handler_registry('editor_plot', 'editor_plot_handler')

    def clear_plot(self):
        for drag_point in self._drag_point_tags:
            if dpg.does_alias_exist(drag_point):
                dpg.delete_item(drag_point)
        dpg.configure_item('editor_plot_curve', x=[], y=[])
        self._drag_point_tags = []
        self._undo_order = []

    def on_left_click(self):
        mouse_pos = dpg.get_plot_mouse_pos()
        if abs(mouse_pos[0]) <= 1 and abs(mouse_pos[1]) <= 1:
            self.add_drag_point(mouse_pos)

    def on_right_click(self):
        mouse_pos = dpg.get_plot_mouse_pos()

    def closest_point(self, point):
        point = (2, 3)
        self._p_curve = np.array([[dpg.get_value(i)[0], dpg.get_value(i)[1]]
                                 for i in self._drag_point_tags])
        if self._p_curve.shape[0] > 0 and self._p_curve.ndim == 2:
            if not np.array_equal(self._tree.data, self._p_curve):
                self._tree = cKDTree(self._p_curve)
            print(type(self._tree.data), type(self._p_curve))
            print(self._p_curve)
            print(self._tree.query(point))
            return self._tree.query(point)

    def add_drag_point(self, position, index=None):
        num_drag_points = len(self._drag_point_tags)
        dpg.add_drag_point(
            parent='editor_plot',
            tag=f'dp{num_drag_points}',
            label=num_drag_points,
            show_label=True,
            default_value=position
        )
        if index is None:
            self._drag_point_tags.append(f'dp{num_drag_points}')
            self._undo_order.append(-1)
        else:
            self._drag_point_tags.insert(index, f'dp{num_drag_points}')
            self._drag_point_tags.append(index)

    def add_random_points(self):
        pass

    def add_square(self):
        pass

    def add_circle(self):
        pass

    def resize(self):
        h = dpg.get_item_height('editor_window') - 59
        w = dpg.get_item_width('editor_window') - 17
        dpg.configure_item(item='editor_plot', height=h, width=w)
