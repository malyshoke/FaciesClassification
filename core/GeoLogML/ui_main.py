# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_main.ui'
##
## Created by: Qt User Interface Compiler version 6.7.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QSizePolicy,
    QVBoxLayout, QWidget)

from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QSizePolicy, QVBoxLayout, QWidget
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QRect, Qt


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        MainWindow.setStyleSheet(u"background-color: rgb(227, 227, 227);")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")

        # Настройка QWebEngineView
        self.webEngineView = QWebEngineView(self.centralwidget)
        self.webEngineView.setObjectName(u"webEngineView")
        self.webEngineView.setGeometry(QRect(200, 30, 550, 530))  # Задаем размер и позицию

        # Оставшиеся элементы в отдельном layout
        self.verticalLayoutWidget = QWidget(self.centralwidget)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(10, 30, 181, 91))

        self.ButtonLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.ButtonLayout.setSpacing(0)
        self.ButtonLayout.setObjectName(u"ButtonLayout")
        self.ButtonLayout.setContentsMargins(0, 0, 0, 0)

        self.openButton = QPushButton(self.verticalLayoutWidget)
        self.openButton.setObjectName(u"openButton")
        font = QFont()
        font.setFamilies([u"Yu Gothic UI Semibold"])
        font.setBold(True)
        self.openButton.setFont(font)
        self.openButton.setFocusPolicy(Qt.FocusPolicy.WheelFocus)
        self.openButton.setAutoDefault(False)
        self.openButton.setFlat(False)
        self.ButtonLayout.addWidget(self.openButton)

        self.saveCSVButton = QPushButton(self.verticalLayoutWidget)
        self.saveCSVButton.setObjectName(u"saveCSVButton")
        self.saveCSVButton.setFont(font)
        self.saveCSVButton.setFocusPolicy(Qt.FocusPolicy.WheelFocus)
        self.saveCSVButton.setAutoDefault(False)
        self.saveCSVButton.setFlat(False)
        self.ButtonLayout.addWidget(self.saveCSVButton)

        self.saveInferance = QPushButton(self.verticalLayoutWidget)
        self.saveInferance.setObjectName(u"saveInferance")
        self.saveInferance.setFont(font)
        self.saveInferance.setFocusPolicy(Qt.FocusPolicy.WheelFocus)
        self.saveInferance.setAutoDefault(False)
        self.saveInferance.setFlat(False)
        self.ButtonLayout.addWidget(self.saveInferance)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        self.openButton.setDefault(False)
        self.saveCSVButton.setDefault(False)
        self.saveInferance.setDefault(False)

        QMetaObject.connectSlotsByName(MainWindow)

    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"GeoLogML", None))
        self.openButton.setText(QCoreApplication.translate("MainWindow", u"\u041e\u0442\u043a\u0440\u044b\u0442\u044c LAS-\u0444\u0430\u0439\u043b", None))
        self.saveCSVButton.setText(QCoreApplication.translate("MainWindow", u"\u0421\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c \u0432 csv", None))
        self.saveInferance.setText(QCoreApplication.translate("MainWindow", u"\u0421\u0434\u0435\u043b\u0430\u0442\u044c \u043f\u0440\u043e\u0433\u043d\u043e\u0437", None))
    # retranslateUi

