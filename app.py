import dearpygui.dearpygui as dpg
from editor import EditorPlot
from viewer import Viewer3D

dpg.create_context()


with dpg.window(tag='primary_window'):
    editor = EditorPlot(**{'label': 'Editor'})
    viewer = Viewer3D(**{'label': '3D Viewer'})


dpg.configure_app(init_file='layout.ini', docking=True, docking_space=True)
dpg.create_viewport(height=500, width=1000, vsync=True)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window('primary_window', True)

while dpg.is_dearpygui_running():

    editor.resize()    
    viewer.resize()
    if editor.n_drag >= 3:
        p_curve = editor.compute_p_curve()
        vertices = editor.compute3D(p_curve)
        viewer.update(vertices)
    
    dpg.render_dearpygui_frame()
    
dpg.destroy_context()
