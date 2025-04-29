# TESTED IN PYTHON 3.12, CANNOT GUARANTEE COMPATIBILITY WITH OLDER VERSIONS
# If anything happens, github.com/SolarBakha is to be blamed, even though the code is my creation
# go blame her, she introduced the eldritch horror that are classes into this program,
# even though they were the most unnecessary thing in the universe after what my ex did to me
import multiprocessing
import os
import subprocess

from PyQt6.QtSvgWidgets import QGraphicsSvgItem
from PyQt6.QtWidgets import QWidget, QApplication, QMainWindow, QVBoxLayout, QLineEdit, QPushButton
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtCore import QMimeData, QByteArray, Qt, QObject
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QLabel
import tempfile
import sys
import io
import matplotlib.pyplot as plot
import latextools
import drawsvg as draw
import re

# Declare math text usage for matplotlib
plot.rc('mathtext', fontset='cm')
#plot.rc('mathtext', fontset='stix')


# Initialize properties class
class Properties(QObject):
    def __init__(self):
        super().__init__()
        # Initialize byte I/O stream for svg data
        self.byteIO = io.BytesIO()

        # Declare defaults
        self.DPI = 300
        self.FontSize = 12
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
        self.properties.equation = self.properties.equation.rstrip()
        # If it's empty, render empty space to avoid errors
        changed = True
        if self.properties.equation == '':
            self.properties.equation = r'\text{ }'
            changed = False
        try:
            # latex_eq = latextools.render_snippet(fr'${self.properties.equation}$')  # ,
            #                                     commands=[
            #                                         latextools.command.LatexCommand("color",
            #                                                                         "white",
            #                                                                         packages=(
            #                                                                             latextools.LatexPackage(
            #                                                                                 "xcolor", ("svgnames",)),
            #                                                                         ))
            #                                     ])
            # svg_eq = latex_eq.as_svg()
            # self.properties.svg = svg_eq
            # self.properties.byteIO.write(svg_eq.content.encode('utf-8'))
            
            # Render the equation using matplotlib plot labelling
            text = img.text(0, 1, fr'${self.properties.equation}$', fontsize=int(self.properties.FontSize),
                            color="#DDDDDD",
                            parse_math=True)
            # text.ha = "center"
            # Create SVG of plot, save as byte stream instead of file
            img.savefig(self.properties.byteIO, transparent=True, dpi=int(self.properties.DPI), format='svg',
                        bbox_inches='tight', pad_inches=0, bbox_extra_artists=[text])
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

        # Write the SVG data to a temporary file
        with tempfile.NamedTemporaryFile(dir=tempdir, delete=False, delete_on_close=False, suffix=".svg") as temp:
            # Write the byte array to the temporary file

            # svg = self.properties.svg
            # d = draw.Drawing(svg.width, svg.height)  # , )
            # d.draw(svg, x=0, y=0)
            # d.append(
            #     draw.Text(fr"${self.properties.equation}$", self.properties.FontSize, 0, svg.height // 2, fill="grey"))
            # latex = latextools.render_svg(d)
            # svg = latex.as_svg()
            # temp.write(svg.content.encode('utf-8'))
            # d.save_svg(temp.name)
            decoded = bytes(byte_array).decode("utf-8")

            # print(str)

            re_width = r"(^<svg.*width=\")(.*?)(\".*?$)"
            re_height = r"(^<svg.*height=\")(.*?)(\".*?$)"
            re_viewbox = r"(^<svg.*viewBox=\")(.*?)(\".*?$)"

            # width_match = re.search(re_width, decoded, flags=re.M)
            # height_match = re.search(re_height, decoded, flags=re.M)
            # viewbox_match = re.search(re_viewbox, decoded, flags=re.M)
            # print(width, height, viewbox)

            def vb_repl(m):
                viewbox = m.group(2)
                viewbox_arr = [float(x) for x in viewbox.split(" ")]
                print(viewbox)
                if viewbox_arr[3] < self.properties.FontSize + 1:
                    print("Here2")
                    viewbox_arr[0] -= 0
                    viewbox_arr[1] -= 2.25
                    viewbox_arr[2] += 1
                    viewbox_arr[3] += 2.25
                    if("\\dot \\" in self.properties.equation):
                        pass
                        #viewbox_arr[1] -= 1
                elif (re.search("(?!.* [ypfjg])(\\\\\\w+ ){2,}[A-Z]", self.properties.equation)):
                    pass
                    print("Here")
                    viewbox_arr[1] -= 2.5
                print("#############################\n", self.properties.equation, "\n", re.search("(?!.*[ypfjg])\\\\dot \\\\\\w+ [A-Z]", self.properties.equation))
                print(self.properties.equation)
                        
                print(viewbox)
                ret_val = f"{m.group(1)}{" ".join(f"{x}" for x in viewbox_arr)}{m.group(3)}"
                print(ret_val)
                return ret_val
                pass

            def h_repl(m):
                height = m.group(2)
                ret_val = f"{m.group(1)}{height}{m.group(3)}"
                print(ret_val)
                return ret_val
                pass

            def w_repl(m):
                width = m.group(2)
                pass

            decoded = re.sub(re_viewbox, vb_repl, decoded, flags=re.M)
            # decoded = re.sub(re_height, h_repl, decoded, flags=re.M)
            # decoded = re.sub(re_width, w_repl, decoded, flags=re.M)
            # print(decoded)
            temp.write(decoded.encode("utf-8"))
            temp.close()
            # Get the path of the temporary file
            self.temp_path = temp.name

            # Remove previous SVG from view
            self.scene.clear()
            # Load the temporary file created earlier
            # into the QGraphicsSvgItem and add it to the viewport
            svgItem = QGraphicsSvgItem(self.temp_path)
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

        # Create Font Size input field
        self.FontSizeBox = QLineEdit(self)
        # Set placeholder text
        self.FontSizeBox.setPlaceholderText(f'Font size - Defaults to 12 pt')
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
                multiprocessing.Process(target=os.system,
                                        args=[f"powershell Set-Clipboard -LiteralPath {self.temp_path}"]).start()

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
