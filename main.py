#!/usr/bin/python3

from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QTableView, QTableWidgetItem, QHBoxLayout
from PyQt5.QtGui import QPixmap, QPainter, QFont, QColor, QPen, QFontMetrics
from signal import signal, SIGINT, SIG_DFL
from collections import deque
from math import cos, sin, pi
from threading import Thread
from time import sleep
from enum import Enum
import sys

class MonitorSetting(Enum):
	Nothing = 0
	ShotImage = 1
	ShotImageWithPoints = 3
	EverythingAnonym = 7
	Everything = 15

class QTable(QWidget):

	_columns = list()
	_rows = list()
	_line_width = 4
	_border = 10
	_font_size = 20
	_font_name = "Arial"

	def __init__(self):
		super().__init__()
		self.initUI()

	def initUI(self):
		self.setMinimumSize(400, 400)

	def add_column(self, column_name):
		self._columns.append(column_name)
		self.update()

	def add_row(self, row_data):
		self._rows.append(row_data)
		self.update()

	def set_line_width(self, line_width):
		self._line_width = line_width
		self.update()

	def set_border(self, border):
		self._border = border
		self.update()

	def set_font_size(self, font_size):
		self._font_size = font_size
		self.update()

	def set_font_name(self, font_name):
		self._font_name = font_name
		self.update()
	
	def paintEvent(self, e):
		qp = QPainter()
		qp.begin(self)
		self.drawWidget(qp)
		qp.end()

	def drawWidget(self, qp):

		#Init fonts
		font = QFont(self._font_name, self._font_size, QFont.Light)
		bold_font = QFont(self._font_name, self._font_size, QFont.Bold)
		font_metrics = QFontMetrics(font)
		bold_font_metrics = QFontMetrics(bold_font)

		#Init QPainter
		pen = QPen(QColor(0, 0, 0))
		pen.setWidth(self._line_width)
		qp.setFont(bold_font)
		qp.setPen(pen)
		qp.setBrush(QColor(255, 255, 255))


		#Setting up some helper vars
		w = self.width()
		h = self.height()
		height = font_metrics.height()
		column_starts = list()
		bold_height = bold_font_metrics.height()
		row_count = int((h - 2 * (self._border + self._line_width)) / (height + 3 * self._line_width)) - 1 
		rows = self._rows[-row_count:]

		#Draw Outer Border
		qp.drawRect(self._border, self._border, w - 2* self._border, h - 2* self._border)

		#Draw vertical lines
		column_index = 0
		current_x = self._border 
		for column in self._columns:
			width = bold_font_metrics.width(column)
			for row in rows:
				if len(row) > column_index:
					width = max(width, font_metrics.width(row[column_index]))
			column_starts.append(current_x + self._line_width)
			current_x += width + 4 * self._line_width
			if column != self._columns[-1]:
				qp.drawLine(current_x, self._border, current_x, h - self._border)
			column_index += 1

		#Draw column header text
		column_index = 0
		for column_x in column_starts:
			qp.drawText(column_x, 4 * self._border, self._columns[column_index])
			column_index += 1

		#Draw rows and horizontal lines
		current_y = self._border + bold_height + 2 * self._line_width
		qp.drawLine(self._border, current_y, w - self._border, current_y)
		qp.setFont(font)
		for i in range(0, row_count):
			if len(rows) > i:
				row = rows[i]
				cell_index = 0
				for cell in row:
					qp.drawText(column_starts[cell_index], current_y + height, cell)
					cell_index += 1
			current_y += 3 * self._line_width + height
			qp.drawLine(self._border, current_y, w - self._border, current_y)
		
class QTarget(QWidget):

	_target_pixmap = None
	_border = 10
	_font_size = 20
	_font_name = "Arial"
	_queue = deque()
	_current_record = None
	_current_step = 0
	_interval = 5
	_shots = list()
	def __init__(self, target_pixmap):
		super().__init__()
		self._target_pixmap = target_pixmap
		self.initUI()
		thread = Thread(target=self.timer)
		thread.start()

	def initUI(self):
		self.setMinimumSize(400, 500)

	def add_sequence(self, name, profile, results, monitor_setting):
		self._queue.append((name, profile, results, monitor_setting))
		
	def paintEvent(self, e):
		qp = QPainter()
		qp.begin(self)
		self.drawWidget(qp)
		qp.end()

	def timer(self):
		while True:
			if self._current_record is None and len(self._queue) > 0:
				self._current_record = self._queue.popleft()
				self._current_step = 0
			if self._current_record is not None:
				self._shots = list()
				shots = self._current_record[2]
				if self._current_step > len(shots):
					if len(self._queue) > 0:
						self._current_record = self._queue.popleft()
					self._current_step = 0
				w = self.width()
				if self._current_step == len(shots):
					shot_index = 0
					for s in shots:
						color = QColor(255, 0, 0)
						if shot_index == 0:
							color = QColor(0, 255, 0)
						elif shot_index == len(shots) - 1:
							color = QColor(0, 0, 255)
						if not s[3]:
							color = QColor(255, 255, 0)
						factor = (s[1] / 2300) * (w / 2)
						angle = s[0] * (pi / 180)
						x = (w / 2) + cos(angle) * factor
						y = (w / 2) + sin(angle) * factor
						self._shots.append((x, y, color))
						shot_index += 1
				else:
					s = shots[self._current_step]
					color = QColor(255, 0, 0)
					if not s[3]:
						color = QColor(255, 255, 0)
					factor = (s[1] / 2300) * (w / 2)
					angle = s[0] * (pi / 180)
					x = (w / 2) + cos(angle) * factor
					y = (w / 2) + sin(angle) * factor
					self._shots.append((x, y, color))
				self.update()
				sleep(self._interval)
				self._current_step += 1



	def drawWidget(self, qp):

		#Init fonts
		font = QFont(self._font_name, self._font_size, QFont.Light)
		bold_font = QFont(self._font_name, self._font_size, QFont.Bold)
		font_metrics = QFontMetrics(font)
		bold_font_metrics = QFontMetrics(bold_font)

		#Init QPainter
		qp.setFont(font)
		qp.setBrush(QColor(255, 0, 0))

		#Setting up some helper vars
		w = self.width()
		h = self.height()
		height = font_metrics.height()
		size = int(w / 11.5)
		#Draw target
		qp.drawPixmap(0, 0, w, w, self._target_pixmap)

		if self._current_record is None:
			return

		if self._current_record[3] == MonitorSetting.Nothing:
			return

		#Draw shots
		for s in self._shots:
			qp.setBrush(s[2])
			qp.drawEllipse(s[0] - (size / 2), s[1] - (size /2), size, size)


		if self._current_record[3] == MonitorSetting.ShotImage:
			return

		#Draw the profile
		if self._current_record[1] is not None:
			qp.drawText(w - self._border - font_metrics.width(self._current_record[1]), w + self._border, self._current_record[1])

		#Draw the rings
		if len(self._current_record[2]) > 0:
			width = 0
			shots = self._current_record[2]
			shot_index = 0
			for shot in shots:
				if shot[3]:
					s = str(shot[2])
				else:
					s = "X"
				if shot_index == self._current_step:
					width += bold_font_metrics.width(s)
				else:
					width += font_metrics.width(s)
				shot_index += 1
			padding = (w - width - 2 * self._border) / len(shots)
			current_x = self._border
			shot_index = 0
			for shot in shots:
				if shot[3]:
					s = str(shot[2])
				else:
					s = "X"
				if shot_index == self._current_step:
					qp.setFont(bold_font)
				qp.drawText(current_x, h - height - self._border, s)
				if shot_index == self._current_step:
					qp.setFont(font)
				current_x += padding + font_metrics.width(s)
				shot_index += 1

		if self._current_record[3] == MonitorSetting.ShotImageWithPoints:
			return

		if self._current_record[3] == MonitorSetting.EverythingAnonym:
			return
		#Draw the name
		if self._current_record[0] is not None:
			qp.drawText(self._border, w + self._border, self._current_record[0])


class Monitor(QWidget):
	
	def __init__(self, width, height):
		super().__init__()
		self.initUI(width, height)
	
	def initUI(self, width, height):
		image = QPixmap("Zielscheibe.png")
		

		self.create_table(height * 0.8, 0)
		self.create_target(0, 0, image)
		self.layout = QHBoxLayout()
		self.layout.addWidget(self.target)
		self.layout.addWidget(self.table)
		self.setLayout(self.layout)


		self.showFullScreen()
		self.show()

		self.add_test_data()

	def create_target(self, x, y, image):
		self.target = QTarget(image)
		self.target.move(0,0)
		self.target.resize(height * 0.8, height * 0.8)

	def create_table(self, x, y):
		self.table = QTable()
		self.table.add_column("Name")
		self.table.add_column("Profil")
		self.table.add_column("Ringe")
		self.table.move(x, y)

	def add_result(self, name, profile, results, monitor_settings):
		sum = 0
		for s in results:
			sum += s[2]
		self.table.add_row([name, "LG 10", "98"])
		self.target.add_sequence(name, profile, results, monitor_settings)

	def add_test_data(self):
		results = [
			[222.3, 460, 9, True],
			[170.7, 120, 10, True],
			[347.8, 73, 10, True],
			[295.1, 370, 9, True],
			[231.6, 282, 9, True],
			[147.1, 151, 10, True],
			[202, 76, 10, False],
			[160.3, 140, 10, True],
			[202.3, 193, 10, True],
			[50.7, 131, 10, True]
		]
		self.add_result("Test Person", "LG 10", results, MonitorSetting.Everything)


if __name__ == "__main__":
	signal(SIGINT, SIG_DFL)
	app = QApplication(sys.argv)
	screen_resolution = app.desktop().screenGeometry()
	width, height = screen_resolution.width(), screen_resolution.height()
	w = Monitor(width, height)
	sys.exit(app.exec_())