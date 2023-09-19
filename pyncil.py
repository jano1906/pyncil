import sys
import PyQt6.QtWidgets as qtw
import PyQt6.QtGui as qtg
import PyQt6.QtCore as qtc
import PIL.Image
import os
import numpy as np
import traceback
from time import time
from importlib import reload, import_module
from argparse import ArgumentParser

app = qtw.QApplication(sys.argv)

class MainWindow(qtw.QMainWindow):
    def __init__(self, script_path, canvas_name, refresh_delta=0.2):
        super().__init__()
        self.canvas = None
        self.script_path = script_path
        self.canvas_name = canvas_name
        self.script = import_module(os.path.splitext(script_path)[0])
        self.watcher = qtc.QFileSystemWatcher([self.script_path])
        self.watcher.fileChanged.connect(self.refresh)
        self.scene = qtw.QGraphicsScene()        
        self.setCentralWidget(qtw.QGraphicsView(self.scene))
        self.refresh_delta = refresh_delta
        self.refresh()

    def refresh(self):
        if hasattr(self, "_last_refresh") and time() - self._last_refresh < self.refresh_delta:
            return
        self.reload_script()
        self.save_canvas()
        self.refresh_canvas()
        self._last_refresh = time()

    @property
    def canvas_name_png(self):
        return f"_{self.canvas_name}.png"

    def save_canvas(self):
        self.canvas_not_none_check()
        PIL.Image.fromarray((np.uint8(self.canvas*255))).convert('RGB').save(self.canvas_name_png)
    
    def refresh_canvas(self):
        if hasattr(self, "_item"):
            self.scene.removeItem(self._item)
        self._item = self.scene.addPixmap(qtg.QPixmap(self.canvas_name_png))

    def reload_script(self):
        try:
            _script = self.script
            self.script = reload(self.script)
            self.canvas = getattr(self.script, self.canvas_name)
            self.canvas_not_none_check()
        except Exception as e:
            self.script = _script
            traceback.print_exception(e)
    
    def cleanup(self):
        os.remove(self.canvas_name_png)

    def canvas_not_none_check(self):
        if self.canvas is None:
            raise Exception(f"Couldn't find '{self.canvas_name}' variable!")

parser = ArgumentParser("pyncil",
                        "Provide script path, canvas name and draw!")

parser.add_argument("-f", "--file", type=str, required=True, help="Path to script file.")
parser.add_argument("-c", "--canvas", type=str, required=True, help="Canvas variable name in the script.")
args = parser.parse_args()

main_window = MainWindow(args.file, args.canvas)
main_window.show()

app.exec()

main_window.cleanup()