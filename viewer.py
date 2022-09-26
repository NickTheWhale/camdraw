import math
import time

import dearpygui.dearpygui as dpg


class Viewer3D:
    def __init__(self, **options):

        self._initial_rot_x = 75
        self._initial_rot_y = 0
        self._initial_rot_z = 45
        self._initial_scale = 1

        self._rot_x = self._initial_rot_x
        self._rot_y = self._initial_rot_y
        self._rot_z = self._initial_rot_z

        self._scale = self._initial_scale

        self._height = 0
        self._width = 0

        self._rotate = False

        with dpg.window(tag='3d_viewer_window', **options):
            with dpg.drawlist(width=1, height=1, tag='3d_drawlist'):
                with dpg.draw_layer(tag='3d_draw_layer', depth_clipping=False, perspective_divide=True, cull_mode=dpg.mvCullMode_Back):
                    with dpg.draw_node(tag='3d_cam_node'):
                        pass

            with dpg.group(horizontal=True):
                dpg.add_slider_int(
                    callback=self.slider_callback,
                    min_value=0,
                    max_value=360,
                    default_value=self._rot_x,
                    tag='x_slider'
                )
                dpg.add_slider_int(
                    callback=self.slider_callback,
                    min_value=0,
                    max_value=360,
                    default_value=self._rot_y,
                    tag='y_slider'
                )
                dpg.add_slider_int(
                    callback=self.slider_callback,
                    min_value=0,
                    max_value=360,
                    default_value=self._rot_z,
                    tag='z_slider'
                )
                dpg.add_slider_float(
                    callback=self.slider_callback,
                    min_value=0.1,
                    max_value=2.5,
                    default_value=self._scale,
                    tag='s_slider'
                )
                dpg.add_button(label='Rotate', tag='rotate_button', callback=self.toggle_rotation)
                dpg.add_button(label='Reset', tag='reset_button', callback=self.reset)

        with dpg.item_handler_registry(tag='3d_viewer_window_handler'):
            dpg.add_item_resize_handler(callback=self.resize)
            dpg.bind_item_handler_registry('3d_viewer_window', '3d_viewer_window_handler')

        self._view = dpg.create_fps_matrix([0, 0, 15], 0.0, 0.0)
        self._projection = dpg.create_perspective_matrix(math.pi*45.0/180.0, 1.0, 0.1, 100)

    def slider_callback(self, sender, app_data):
        if sender == 'x_slider':
            self._rot_x = app_data
        elif sender == 'y_slider':
            self._rot_y = app_data
        elif sender == 'z_slider':
            self._rot_z = app_data
        elif sender == 's_slider':
            self._scale = app_data

        self.apply_transforms()

    def toggle_rotation(self):
        self._rotate = not self._rotate

    def rotate(self, theta=1):
        self._rot_z += theta
        self._rot_z %= 360

        dpg.set_value(item='z_slider', value=self._rot_z)
        self.apply_transforms()

    def reset(self):
        self._rot_x = self._initial_rot_x
        self._rot_y = self._initial_rot_y
        self._rot_z = self._initial_rot_z

        self._scale = self._initial_scale
        
        dpg.set_value(item='x_slider', value=self._rot_x)
        dpg.set_value(item='y_slider', value=self._rot_y)
        dpg.set_value(item='z_slider', value=self._rot_z)
        dpg.set_value(item='s_slider', value=self._scale)

        self.apply_transforms()

    def update(self, vertices: list[list | tuple], decimation_factor=1):
        decimated_vertices = []
        if decimation_factor > 1:
            decimated_vertices = [vertices[i] for i in range(0, len(vertices), decimation_factor)]
            decimated_vertices.append(vertices[-1])
        else:
            decimated_vertices = vertices

        with dpg.mutex():
            if dpg.does_alias_exist('cam_polygon'):
                dpg.delete_item('cam_polygon')

            dpg.draw_polygon(
                points=decimated_vertices,
                tag='cam_polygon',
                parent='3d_cam_node',
                color=(255, 255, 255)
            )
            dpg.draw_line((1, 0, 0), (-1, 0, 0), parent='3d_cam_node', color=(255, 0, 0))  # red
            dpg.draw_line((0, 1, 0), (0, -1, 0), parent='3d_cam_node', color=(0, 255, 0))  # green
            dpg.draw_line((0, 0, 1), (0, 0, -1), parent='3d_cam_node', color=(0, 0, 255))  # blue
        
            if self._rotate:
                self.rotate()

            self.apply_transforms()
            
    def draw_polygons(self, polygons, decimation_factor=1):
        try:
            decimated_polygons = []
            if decimation_factor > 1:
                for i in range(len(polygons)):
                    decimated_polygon = [polygons[i][j] for j in range(0, len(polygons[i]), decimation_factor)]
                    decimated_polygons.append(decimated_polygon)
            else:
                decimated_polygons = polygons
                
            for i in range(len(decimated_polygons)):
                if dpg.does_alias_exist(f'cam_polygon{i}'):
                    dpg.delete_item(f'cam_polygon{i}')
                dpg.draw_polygon(
                    points=decimated_polygons[i],
                    tag=f'cam_polygon{i}',
                    parent='3d_cam_node',
                    color=(255, 255, 255)
                )
        except Exception as e:
            print(e)

    def apply_transforms(self) -> None:
        model = dpg.create_rotation_matrix(math.pi*self._rot_x/180.0, [1, 0, 0]) *\
            dpg.create_rotation_matrix(math.pi*self._rot_y/180.0, [0, 1, 0]) *\
            dpg.create_rotation_matrix(math.pi*self._rot_z/180.0, [0, 0, 1])

        scale_matrix = dpg.create_scale_matrix((self._scale, self._scale, self._scale))

        dpg.apply_transform('3d_cam_node', self._projection*self._view*model*scale_matrix)

    def resize(self):
        height = dpg.get_item_height('3d_viewer_window') - 59
        width = dpg.get_item_width('3d_viewer_window') - 17

        if height != self._height or width != self._width:
            dpg.configure_item(item='3d_drawlist', height=height, width=width)
            self._height = height
            self._width = width

        dpg.configure_item(item='x_slider', width=width // 6)
        dpg.configure_item(item='y_slider', width=width // 6)
        dpg.configure_item(item='z_slider', width=width // 6)
        dpg.configure_item(item='s_slider', width=width // 6)

        dpg.set_clip_space('3d_draw_layer', 0, 0, width, height//1.1, -1.0, 1.0)

    @property
    def rotating(self) -> bool:
        return self._rotate
