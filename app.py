import dearpygui.dearpygui as dpg

from editor import EditorPlot
from viewer import Viewer3D

dpg.create_context()


with dpg.window(tag='primary_window'):
    editor = EditorPlot(**{'label': 'Editor'})
    viewer = Viewer3D(**{'label': '3D Viewer'})


dpg.configure_app(init_file='layout.ini', docking=True, docking_space=True)
dpg.create_viewport(vsync=True)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window('primary_window', True)


while dpg.is_dearpygui_running():
    try:
        if editor.dirty:
            if editor.n_drag >= 3:
                if not dpg.is_mouse_button_down(dpg.mvMouseButton_Left):
                    p_curve = editor.compute_p_curve()
                    vertices = editor.compute_3D_spline(p_curve)
                    viewer.update(vertices, 10)
                    # polygons = editor.compute_cam()
                    # viewer.draw_polygons(polygons, 100)
                    # viewer.update(vertices)
                    editor.dirty = False

        if viewer.rotating:
            viewer.rotate(0.20)

    except Exception as e:
        print(e)

    dpg.render_dearpygui_frame()

dpg.destroy_context()
