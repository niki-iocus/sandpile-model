import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

import matplotlib.figure as pltfigure
from matplotlib.backends.backend_qtagg import FigureCanvas

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QLineEdit, QVBoxLayout, QWidget, QTextEdit, QSlider, QGridLayout


import sys

from random import randint

size = 5


class MainWindow(QMainWindow):

    def checkBoundry(self, X, Y):
       if X >= 0 and X <= self.size - 1 and  Y >= 0 and Y <= self.size - 1:
        return True
       else:
           return False
    

    def addSand(self, X, Y):
        if self.checkBoundry(X, Y) == True:   
            self.piles[X, Y] = self.piles[X, Y] + 1
            self.changes[X, Y] += 1

            if self.piles[X, Y] >= 4:
                self.piles[X, Y] = self.piles[X, Y] - 4
                self.changes[X, Y] -= 4
                self.avalanche_size += 1

                self.addSand(X - 1, Y)
                self.addSand(X + 1, Y)
                self.addSand(X, Y - 1)
                self.addSand(X, Y + 1)
        else:
            self.number_of_sand -= 1


    def timeStep(self):

        self.time += 1

        #reset vars
        self.changes = np.zeros((self.size,self.size), dtype=int)
        self.avalanche_size = int(0)


        #Randomly add sand
        X = randint(0, self.piles.shape[0] -1)
        Y = randint(0, self.piles.shape[1] -1)
        self.addSand(X, Y)
        self.number_of_sand += 1


        if self.show_sim == True:
            #draw piles
            self.subplot.cla()
            self.showpiles = self.subplot.matshow(self.piles, vmin = 0, vmax = 3)
            self.subplot.set_title(f"t = {int(self.time)}", fontsize = 14)
            self.showpiles.figure.canvas.draw()

            #draw changes
            self.change_subplot.cla()
            self.showchanges = self.change_subplot.matshow(self.changes, vmin = -4, vmax = 4)
            self.change_subplot.set_title(f"t = {int(self.time)}", fontsize = 14)
            self.showchanges.figure.canvas.draw()

        #update stats
        self.stats_label.setText(f"Time: {self.time}, Number of sand: {self.number_of_sand}, Avalanche size: {self.avalanche_size}")

        #add to logs
        self.current_log = pd.Series([self.time, self.number_of_sand, self.avalanche_size], index=["Time", "Number of Sand", "Avalanche Size"])
        self.logs = pd.concat([self.logs, self.current_log.to_frame().T], ignore_index=True)


    def sim_init(self):
        self.time = 0
        self.size = int(self.size_slider.value())

        self.number_of_sand = 0
        self.avalanche_size = int(0)

        self.piles = np.zeros((self.size,self.size), dtype=int)
        self.changes = np.zeros((self.size,self.size), dtype=int)

        #slider text updaten
        self.size_slider_text.setText(f"Size: {self.size}")

        self.start_log = {
            "Time": pd.Series([self.time]),
            "Number of Sand": pd.Series([self.number_of_sand]),
            "Avalanche Size": pd.Series([self.avalanche_size])
        }
        self.logs = pd.DataFrame(self.start_log)


    def save_logs(self):
        self.logs.to_csv(path_or_buf=f"logs/{self.save_name_box.text()}.csv",index=False)

    def pause_button_click(self):
        if self.pause_button.text() == 'Pause':
            self.timer.stop()
            self.pause_button.setText('Continue')
        else:
            self.timer.start()
            self.pause_button.setText('Pause')

    def change_speed(self):
        sim_interval = int(1000/self.speed_slider.value())
        self.timer.interval = sim_interval
        sim_speed = int(self.speed_slider.value())
        self.speed_slider_text.setText(f"Speed: {sim_speed}")

    def fast_sim(self):        
        if self.fast_sim_button.text() == 'Fast Sim':
            self.show_sim = False
            self.timer.interval = 1
            self.fast_sim_button.setText('Normal Sim')
        else:
            self.show_sim = True
            self.change_speed()
            self.fast_sim_button.setText('Fast Sim')

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Abelian sandpile model")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QGridLayout(self.central_widget)

        #size slider
        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setMinimum(1)
        self.size_slider.setMaximum(100)
        self.size_slider.setValue(10)
        self.size_slider.valueChanged.connect(self.sim_init)
        self.layout.addWidget(self.size_slider, 0, 0, 1, 1)
        self.size_slider_text = QLabel(f"Size: {self.size_slider.value()}")
        self.layout.addWidget(self.size_slider_text, 0, 1, 1, 1)

        #pause button
        self.pause_button = QPushButton()
        self.pause_button.setText("Pause")
        self.pause_button.clicked.connect(self.pause_button_click)
        self.layout.addWidget(self.pause_button, 0, 2, 1, 1)

        #fast sim button
        self.show_sim = True
        self.fast_sim_button = QPushButton()
        self.fast_sim_button.setText("Fast Sim")
        self.fast_sim_button.clicked.connect(self.fast_sim)
        self.layout.addWidget(self.fast_sim_button, 1, 2, 1, 1)

        #speed slider
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(1)
        self.speed_slider.setMaximum(50)
        self.speed_slider.setValue(20)
        self.speed_slider.valueChanged.connect(self.change_speed)
        self.layout.addWidget(self.speed_slider, 1, 0, 1, 1)
        self.speed_slider_text = QLabel(f"Speed: {self.speed_slider.value()}")
        self.layout.addWidget(self.speed_slider_text, 1, 1, 1, 1)

        #savebutton
        self.save_button = QPushButton()
        self.save_button.setText("Save")
        self.save_button.clicked.connect(self.save_logs)
        self.layout.addWidget(self.save_button, 10, 2, 1, 1)

        
        #save name box
        self.save_name_box = QLineEdit()
        self.save_name_box.setMaxLength(25)
        self.save_name_box.setPlaceholderText("Enter save name")
        self.layout.addWidget(self.save_name_box, 10, 1, 1, 1)
        
        #show sandpiles
        self.model = FigureCanvas(pltfigure.Figure(figsize=(5, 5)))
        self.layout.addWidget(self.model, 4, 0, 3, 3)

        self.subplot = self.model.figure.subplots()
        
        #show changes

        self.change_chanvas = FigureCanvas(pltfigure.Figure(figsize=(5, 5)))
        self.layout.addWidget(self.change_chanvas, 7, 0, 3, 3)

        self.change_subplot = self.change_chanvas.figure.subplots()

        self.sim_init()

        #stats label
        self.stats_label = QLabel()
        self.layout.addWidget(self.stats_label, 10, 0, 1, 1)


        #timer
        self.timer = self.model.new_timer(50)
        self.timer.add_callback(self.timeStep)
        self.timer.start()


        self.showpiles = plt.matshow(self.piles)
        self.showchanges = plt.matshow(self.changes)


        


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()


