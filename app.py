import dearpygui.dearpygui as dpg
from editor import EditorPlot

dpg.create_context()


with dpg.window(tag='primary_window'):
    editor = EditorPlot()


dpg.configure_app(docking=True, docking_space=True)
dpg.create_viewport()
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window('primary_window', True)

while dpg.is_dearpygui_running():
    editor.resize()
    dpg.render_dearpygui_frame()

dpg.destroy_context()
