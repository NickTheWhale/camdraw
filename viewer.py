import dearpygui.dearpygui as dpg
import math


class Viewer3D:
    def __init__(self, **options):

        self._height = 0
        self._width = 0

        self._rot_x = 0
        self._rot_y = 0
        self._rot_z = 0

        with dpg.window(tag='3d_viewer', **options):
            with dpg.drawlist(width=1, height=1, tag='3d_drawlist'):
                with dpg.draw_layer(tag='3d_draw_layer', depth_clipping=False, perspective_divide=True, cull_mode=dpg.mvCullMode_Back):
                    with dpg.draw_node(tag='3d_cam_node'):
                        pass

        self._view = dpg.create_fps_matrix([0, 0, 15], 0.0, 0.0)
        self._projection = dpg.create_perspective_matrix(math.pi*45.0/180.0, 1.0, 0.1, 100)
        self._model = dpg.create_rotation_matrix(math.pi*self._rot_x/180.0, [1, 0, 0]) *\
            dpg.create_rotation_matrix(math.pi*self._rot_y/180.0, [0, 1, 0]) *\
            dpg.create_rotation_matrix(math.pi*self._rot_z/180.0, [0, 0, 1])

    def set_rotation(self, x, y, z):
        self._rot_x = x % 360
        self._rot_y = y % 360
        self._rot_z = z % 360
        
    def update(self, vertices: list[list | tuple]):
        if dpg.does_alias_exist('cam_polygon'):
            dpg.delete_item('cam_polygon')
        dpg.draw_polygon(points=vertices, tag='cam_polygon', parent='3d_cam_node')
        
        
        self._model = dpg.create_rotation_matrix(math.pi*self._rot_x/180.0, [1, 0, 0]) *\
            dpg.create_rotation_matrix(math.pi*self._rot_y/180.0, [0, 1, 0]) *\
            dpg.create_rotation_matrix(math.pi*self._rot_z/180.0, [0, 0, 1])

        dpg.apply_transform('3d_cam_node', self._projection*self._view*self._model)

    def resize(self):
        height = dpg.get_item_height('3d_viewer') - 57
        width = dpg.get_item_width('3d_viewer') - 17

        if height != self._height or width != self._width:
            dpg.configure_item(item='3d_viewer', height=height, width=width)
            self._height = height
            self._width = width

        dpg.set_clip_space('3d_draw_layer', 0, -height//8, width, height//1.2, -1.0, 1.0)
