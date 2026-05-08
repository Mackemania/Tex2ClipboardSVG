# TESTED IN PYTHON 3.12, CANNOT GUARANTEE COMPATIBILITY WITH OLDER VERSIONS
# If anything happens, github.com/SolarBakha is to be blamed, even though the code is my creation
# go blame her, she introduced the eldritch horror that are classes into this program,
# even though they were the most unnecessary thing in the universe after what my ex did to me
import io
import multiprocessing
import os
import re
import sys
import tempfile
from io import StringIO
import xml.etree.ElementTree as ET

import matplotlib.pyplot as plot
from PyQt6.QtCore import QByteArray, Qt, QObject
from PyQt6.QtGui import QPainter, QImage, QBitmap, QRegion
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtSvgWidgets import QGraphicsSvgItem
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QLabel
from PyQt6.QtWidgets import QWidget, QApplication, QMainWindow, QVBoxLayout, QLineEdit

# Declare math text usage for matplotlib
plot.rc('mathtext', fontset='cm')
# plot.rc('text', usetex=True)
# plot.rc('text.latex', preamble=r'\usepackage{steinmetz}')
plot.rc('text.latex', preamble=r'\usepackage{amsmath}')
# plot.rc('mathtext', fontset='stix')


def_color = "#DDDDDD"
# def_color="#000000"

repl = {
    r"\\Var": r"\\text{Var}",
    r"\\Log": r"\\text{Log}\,",
    r"\\bLog": r"\\mathcal{L}\text{og}\,",
    r"\\Arg": r"\\text{Arg}\,",
    r"\\dell": r"\\partial",
    r"\\Re ": r"\\text{Re}\,",
    r"\\Res{([^}]*)}": r"\\underset{\1}{\\text{Res}}",
    r"\\argvar{([^}]*)}": r"\\underset{\1}{\\text{argvar}}",
    r"\\epsilon": r"\\varepsilon",
    r"\\hat": r"\\widehat",
    r"\\matrix§([^§]*)§": r"\\begin{bmatrix}\1\\end{bmatrix}"
}


# Initialize properties class
class Properties(QObject):
    def __init__(self):
        super().__init__()
        # Initialize byte I/O stream for svg data
        self.byteIO = io.BytesIO()

        # Declare defaults
        self.DPI = 300
        self.FontSize = 18
        self.copyFlag = 0
        self.NOCOPY = False
        self.equation = '(x + y)^2 = x^2 + y^2'
        self.svg = None


class MainWindow(QMainWindow):
    changed = False
    temp_path = ''

    # Define updaters
    def updateDPILabel(self, flag):
        # Update DPI value shown on label
        if self.properties.DPI <= 500:
            self.DPILabel.setText(f'Resolution: {self.properties.DPI} DPI')
        elif self.properties.DPI > 500 and self.properties.DPI <= 1000:
            self.DPILabel.setText(f'Resolution: {self.properties.DPI} DPI, you wanna write this in individual atoms or'
                                  f' what?')
        elif self.properties.DPI > 1000 and self.properties.DPI <= 10000:
            self.DPILabel.setText(f'Resolution: {self.properties.DPI} DPI, you wanna write this in individual quarks or'
                                  f' what?')
        elif self.properties.DPI > 10000 and self.properties.DPI <= 100000:
            self.DPILabel.setText(f'Resolution: {self.properties.DPI} DPI, you wanna write this in individual '
                                  f'strings or what?')
        elif self.properties.DPI > 100000 and self.properties.DPI <= 1000000:
            self.DPILabel.setText(f'one day you will answer to a god who will not be as merciful as i am. Resolution:'
                                  f' {self.properties.DPI} DPI')
        else:
            self.properties.DPI = 300
            self.DPILabel.setText(f'you are sick. fuck it. *unsets your resolution*'
                                  f' Resolution: {self.properties.DPI} DPI')
        # If the value change failed, set to red background to indicate defaults were applied
        if flag == 'FAIL':
            self.DPIbox.setStyleSheet("background-color: rgb(255,143,143)")
        # If the value change was successful, set to green background to indicate success
        if flag == 'PASS':
            self.DPIbox.setStyleSheet("background-color: rgb(149,255,171)")
        # Refresh the label to display the new changes
        self.DPILabel.update()

    def updateDPIValue(self):
        # Attempt to update DPI value, if it fails, set to default value and
        # pass the fail flag to the label updater
        try:
            self.properties.DPI = int(self.DPIbox.text())
            self.updateDPILabel('PASS')
        # If the value change fails, set to default value and pass the fail flag to the label updater
        # i dont even know why the fuck it would fail besides invalid values, but hey whatever
        except Exception as DPIChangeError:
            self.properties.DPI = 300
            self.updateDPILabel('FAIL')
            print(f'Failed to update DPI value to {self.DPIbox.text()} \n {DPIChangeError}')

    def updateFontSizeLabel(self, flag):
        # Change font size label text
        if self.properties.FontSize <= 200:
            self.FontSizeLabel.setText(f'Font Size: {self.properties.FontSize} pt')
        elif self.properties.FontSize > 200 and self.properties.FontSize <= 1000:
            self.FontSizeLabel.setText(f'Font Size: {self.properties.FontSize} [COMICALLY LARGE]')
        elif self.properties.FontSize > 1000 and self.properties.FontSize <= 10000:
            self.FontSizeLabel.setText(f'Font Size: [C H O N K]')
        else:
            self.properties.FontSize = 12
            self.FontSizeLabel.setText(f'Okay, enough playing around. Font Size: {self.properties.FontSize} pt')
        # If change had failed, update with failure background
        if flag == 'FAIL':
            self.FontSizeBox.setStyleSheet("background-color: rgb(255,143,143)")
        # If change was successful, update with light green background
        if flag == 'PASS':
            self.FontSizeBox.setStyleSheet("background-color: rgb(149,255,171)")
        self.FontSizeLabel.update()

    def updateFontSizeValue(self):
        # try because idk, what could even make it fail lmao
        try:
            self.properties.FontSize = int(self.FontSizeBox.text())
            # if it passes, update the label with a pass flag
            self.updateFontSizeLabel('PASS')
        except Exception as FontSizeError:
            # if it fails, set to default value and update the label with a fail flag
            self.properties.FontSize = 12
            self.updateFontSizeLabel('FAIL')
            # print the error, because i like complaining
            print(f'Failed to update font size value: {self.FontSizeBox.text()} \n {FontSizeError}')

    # Equation Renderer
    def render_eq(self, launch):
        # Initialize plot
        img = plot.figure(figsize=(1, 1))
        if not launch:
            # Retrieve Equation
            self.properties.equation = self.eq_box.text()
        # Strip spaces after it's done because matplotlib will bitch about a single space ._.
        self.preprocess()
        self.properties.equation = self.properties.equation.rstrip()
        print(self.properties.equation)
        # If it's empty, render empty space to avoid errors
        changed = True
        if self.properties.equation == '':
            self.properties.equation = r'\text{ }'
            changed = False
        try:
            # Render the equation using matplotlib plot labelling
            usetex = r"\begin" in self.properties.equation
            text = img.text(0, 1,
                            fr'${self.properties.equation}$',
                            fontsize=int(self.properties.FontSize),
                            color=def_color,
                            parse_math=True,
                            usetex=usetex)
            # text.ha = "center"
            # Create SVG of plot, save as byte stream instead of file
            img.savefig(self.properties.byteIO,
                        transparent=True,
                        dpi=int(self.properties.DPI),
                        format='svg',
                        pad_inches=1,
                        bbox_extra_artists=[text],
                        bbox_inches='tight')
            self.changed = changed
            return 'SUCCESS'
        except ValueError as e:
            plot.close(img)
            print(e)
            return 'FAILED'
            pass
        except Exception as rendererr:
            plot.close(img)
            print(rendererr)
            return f'FAILED: {rendererr}'
        finally:
            plot.close(img)
            if self.properties.equation == r'\text{ }':
                return 'EMPTY'

    def preprocess(self):
        eq = self.properties.equation
        # print("Before", eq)
        for k, i in repl.items():
            eq = re.sub(k, i, eq)
        # print("After:", eq)
        self.properties.equation = eq
        pass

    # Retrieve SVG byte array and send to clipboard with MIME data
    def createSVG(self, arg):
        if arg == 'SUCCESS' or arg == 'EMPTY':
            # Retrieve SVG byte array
            byte_array = QByteArray(self.properties.byteIO.getvalue())
            # Initialize mime data as qmimedata object, thanks qt
            # mimeData = QMimeData()
            # Set the data type to SVG+xml, with byte array as following data
            # mimeData.setData("image/svg+xml", byte_array)
            # if (not self.properties.NOCOPY) and (arg == 'SUCCESS'):
            # Initialize clipboard
            # clipboard = QGuiApplication.clipboard()
            # Indicate mime type to clipboard
            # clipboard.setMimeData(mimeData)
        if arg == 'FAILED':
            return

        decoded = bytes(byte_array).decode("utf-8")

        self.svgData = decoded.encode("utf-8")
        svgRenderer = QSvgRenderer(QByteArray(self.svgData))

        scale = 10
        size = svgRenderer.defaultSize() * scale

        img = QImage(size, QImage.Format.Format_ARGB32)
        img.fill(0)

        p = QPainter(img)
        svgRenderer.render(p)
        p.end()
        mask = img.createAlphaMask()
        region = QRegion(QBitmap.fromImage(mask))
        s_bbox = region.boundingRect()
        bbox = {
            "x": s_bbox.x() / scale,
            "y": s_bbox.y() / scale,
            "width": s_bbox.width() / scale,
            "height": s_bbox.height() / scale
        }

        ratio = bbox["width"] / (bbox["height"] if bbox["height"] != 0 else 1)

        target_h = 25
        target_w = target_h * ratio

        svg = re.sub(
            r'viewBox="[^"]+"',
            f'viewBox="{bbox["x"] - 1} {bbox["y"] - 1} {bbox["width"] + 2} {bbox["height"] + 2}"',
            decoded,
            count=1
        )

        svg = re.sub(
            r'height\s*=\s*["\'][^"\']*["\']',
            f'height="{target_h}px"',
            svg,
            count=1
        )

        svg = re.sub(
            r'width\s*=\s*["\'][^"\']*["\']',
            f'width="{target_w}px"',
            svg,
            count=1
        )

        self.svgData = svg.encode("utf-8")

        # Remove previous SVG from view
        self.scene.clear()
        # Load the temporary file created earlier
        # into the QGraphicsSvgItem and add it to the viewport
        svgRenderer = QSvgRenderer(QByteArray(self.svgData))
        svgItem = QGraphicsSvgItem()
        svgItem.setSharedRenderer(svgRenderer)

        # Add new SVG
        self.scene.addItem(svgItem)

        # make it fit, duh
        self.view.fitInView(svgItem, Qt.AspectRatioMode.KeepAspectRatio)
        # Flush IO stream for next SVG byte array
        self.properties.byteIO.seek(0)
        self.properties.byteIO.truncate()

    # Tick Rendering Per Keystroke
    def renderticker(self):
        # Attempt to render equation
        try:
            self.createSVG(self.render_eq(False))
        except Exception as err:
            print(f'An error occurred while rendering equation: {err}')
        else:
            return

    def __init__(self):
        super().__init__()
        # Assign properties
        self.properties = Properties()

        # Initialize elements
        # Create equation input field
        self.eq_box = QLineEdit(self)
        self.eq_box.setPlaceholderText("Input Equation [TeX]")
        self.eq_box.textChanged.connect(self.renderticker)

        # Create DPI input field
        self.DPIbox = QLineEdit(self)
        # Set placeholder text
        self.DPIbox.setPlaceholderText(f'DPI - Defaults to 300')
        # Connect text change events to ticker and updates
        self.DPIbox.textChanged.connect(self.updateDPIValue)
        self.DPIbox.textChanged.connect(self.renderticker)

        # Create Path field
        self.PathBox = QLineEdit(self)
        # Set placeholder text
        self.PathBox.setPlaceholderText(f'')

        # Create Font Size input field
        self.FontSizeBox = QLineEdit(self)
        # Set placeholder text
        self.FontSizeBox.setPlaceholderText(f'Font size - Defaults to 18 pt')
        # Connect text change events to ticker and updates
        self.FontSizeBox.textChanged.connect(self.updateFontSizeValue)
        self.FontSizeBox.textChanged.connect(self.renderticker)

        # Create DPI label
        self.DPILabel = QLabel(f'Resolution: {self.properties.DPI} DPI')
        # Enable updates for the label for changes to show
        self.DPILabel.setUpdatesEnabled(True)

        # Create FontSize label
        self.FontSizeLabel = QLabel(f'Font Size: {self.properties.FontSize} pt')
        # Enable updates for the label for changes to show
        self.FontSizeLabel.setUpdatesEnabled(True)

        # Set window title and size
        self.setWindowTitle('Tex2ClipboardSVG')
        self.resize(800, 600)

        # Create scene and view for SVG display
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene, self)

        # Create layout
        layout = QVBoxLayout()
        layout.addWidget(self.eq_box)
        layout.addWidget(self.DPIbox)
        layout.addWidget(self.FontSizeBox)
        layout.addWidget(self.PathBox)
        layout.addWidget(self.DPILabel)
        layout.addWidget(self.FontSizeLabel)
        layout.addWidget(self.view)
        central_widget = QWidget()
        central_widget.setLayout(layout)
        central_widget.keyPressEvent = self.keyPressEvent
        self.setCentralWidget(central_widget)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            print(self.changed)
            if (self.changed):
                self.changed = False

                # Write the SVG data to a temporary file
                with tempfile.NamedTemporaryFile(dir=tempdir, delete=False, delete_on_close=False,
                                                 suffix=".svg") as temp:
                    # Write the byte array to the temporary file
                    temp.write(self.svgData)
                    temp.close()
                    # Get the path of the temporary file
                    self.PathBox.setText(temp.name)
                    multiprocessing.Process(target=os.system,
                                            args=[f"powershell Set-Clipboard -LiteralPath {temp.name}"]).start()

                with open("log.txt", "r+") as f:
                    for line in f:
                        if (line.strip() == self.properties.equation):
                            break
                    else:
                        f.write(f"{self.properties.equation}\n")


# main function because yes, if you dont know what that is i suggest you reconsider your life choices
if __name__ == '__main__':
    with tempfile.TemporaryDirectory() as tempdir:
        # Initialize Qt application
        app = QApplication(sys.argv)
        # Initialize main window
        window = MainWindow()
        # Show main window, because that is literally the point of the program
        window.show()
        window.render_eq(True)
        window.createSVG('EMPTY')
        # Close when windows is closed because why the fuck would the CLI stay open
        sys.exit(app.exec())
