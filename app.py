import time
import dearpygui.dearpygui as dpg
from editor import EditorPlot

dpg.create_context()


with dpg.window(tag='primary_window'):
    editor = EditorPlot()


dpg.configure_app(init_file='layout.ini', docking=True, docking_space=True)
dpg.create_viewport(height=600, width=600, vsync=True)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window('primary_window', True)

while dpg.is_dearpygui_running():
    start = time.time()
    # editor.resize()
    editor.parametric_curve()
    
    
    dpg.render_dearpygui_frame()
    stop = time.time()
    # print(f'loop time (ms) {(stop - start) * 1000:0.3f}')

dpg.destroy_context()
