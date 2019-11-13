import sys
from PyQt5.QtWidgets import (QMainWindow, QTextEdit, QAction, QApplication,
                             QWidget, QTabWidget, QVBoxLayout, QPushButton,
                             QMessageBox, QLineEdit, QHBoxLayout, QLabel,
                             QTableWidget, QStackedWidget, QTableWidgetItem)
from PyQt5.QtGui import QIcon
from PyQt5 import QtCore, QtGui
import pymysql


def get_db():
    db = pymysql.connect(host='localhost', user='root', db='wishlist')
    with db:
        cur = db.cursor()
        cur.execute(
            """
                CREATE TABLE IF NOT EXISTS wishlist (
                id INT PRIMARY KEY AUTO_INCREMENT,
                title VARCHAR(20),
                price INT,
                link VARCHAR(80),
                note VARCHAR(60)
                );
                """
        )
        db.commit()
        return db


def get_wish(id):
    db = get_db()
    with db:
        cur = db.cursor()
        cur.execute("SELECT * FROM wishlist WHERE id = {}".format(id))
        wish = cur.fetchall()
        return wish[0]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.tmp = QVBoxLayout()

        self.list_widget = ListWidget(self)
        self.wish_widget = WishWidget(self)

        self.stacked = StackWidgets()

        self.setCentralWidget(self.stacked)

        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle('Main window')
        self.show()


class StackWidgets(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.list_widget = ListWidget(self)
        self.wish_widget = WishWidget(self)
        self.addWidget(self.list_widget)
        self.addWidget(self.wish_widget)

    def listCentral(self):
        self.list_widget = ListWidget(self)
        self.addWidget(self.list_widget)
        self.setCurrentWidget(self.list_widget)

    def wishCentral(self, id):
        self.wish_widget = WishWidget(self, id)
        self.addWidget(self.wish_widget)
        self.setCurrentWidget(self.wish_widget)


class ListWidget(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.unitUI()

    def unitUI(self):
        # Add central widget with tabs
        self.vbox = QVBoxLayout(self)

        font = QtGui.QFont()
        font.setFamily("Serif")
        font.setPointSize(12)

        # Создание таблицы-списка
        self.tableWidget = QTableWidget()
        self.tableWidget.setFont(font)
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setRowCount(0)
        self.tableWidget.setHorizontalHeaderLabels(['ID', 'Title', 'Price', 'Link', 'Note', '', ''])
        self.vbox.addWidget(self.tableWidget)

        self.wishesToTable()

        # Кнопка для создания новго желания
        self.addButton = QPushButton("ToWish")
        self.addButton.clicked.connect(self.changeWidget)
        self.vbox.addWidget(self.addButton)

        self.tableWidget.itemChanged.connect(self.saveChanges)

        self.setLayout(self.vbox)

    def wishesToTable(self):
        wishlist = self.getWishes()
        for i in range(len(wishlist)):
            rowPosition = self.tableWidget.rowCount()
            self.tableWidget.insertRow(rowPosition)
            for j in range(5):
                self.tableWidget.setItem(i, j, QTableWidgetItem(wishlist[i][j]))

            btn = QPushButton(self.tableWidget)
            btn.setText('Edit')
            btn.clicked.connect(self.editWish)
            self.tableWidget.setCellWidget(i, 5, btn)

            btn = QPushButton(self.tableWidget)
            btn.setText("Del")
            btn.clicked.connect(self.delWish)
            self.tableWidget.setCellWidget(i, 6, btn)

    def editWish(self):
        button = self.sender()
        if button:
            row = self.tableWidget.indexAt(button.pos()).row()
            id = self.tableWidget.item(row, 0).text()
            print("id =", id)
            self.parent().wishCentral(id)

    def delWish(self):
        button = self.sender()
        if button:
            row = self.tableWidget.indexAt(button.pos()).row()
            id = self.tableWidget.item(row, 0).text()
            print("id =", id)
            self.tableWidget.removeRow(row)
            print(button.pos())
            print(row)
            self.dbDelete(id)

    def dbDelete(self, id):
        db = get_db()
        with db:
            cur = db.cursor()
            insert_query = """ DELETE FROM wishlist WHERE id = {} """.format(id)
            cur.execute(insert_query)

        print(self.tableWidget.currentRow())
        # print(wish.table_id, wish.id)
        # self.tableWidget.removeRow(wish.table_id)

    def getWishes(self):
        db = get_db()
        with db:
            cur = db.cursor()
            cur.execute("SELECT * FROM wishlist")
            wishlist = cur.fetchall()
            wishlist = self.formatWishes(wishlist)
            return wishlist

    def formatWishes(self, wishlist):
        print("wishlist:", wishlist)
        new_wishlist = []
        for wish in wishlist:
            tmp = []
            for field in wish:
                tmp.append(str(field))
            new_wishlist.append(tmp)
        print("new_wishlist:", new_wishlist)
        return new_wishlist

    def saveChanges(self, item):
        print(item.text(), item.column(), item.row(), item)

    def changeWidget(self):
        self.parent().wishCentral()

    def test(self):
        print("test")


class WishWidget(QWidget):
    def __init__(self, main_window, id=-1):
        super().__init__()
        self.main_window = main_window
        self.id = id
        self.initUI()

    def initUI(self):
        # Add central widget with tabs
        self.vbox = QVBoxLayout(self)

        font = QtGui.QFont()
        font.setFamily("Serif")
        font.setPointSize(12)

        # Кнопка для создания новго желания
        hbox = QHBoxLayout()
        backButton = QPushButton("Back")
        backButton.clicked.connect(self.changeWidget)
        hbox.addStretch(1)
        hbox.addWidget(backButton)
        self.vbox.addLayout(hbox)

        self.lineedit1 = QLineEdit(self)
        self.lineedit1.setPlaceholderText('Wish')
        self.vbox.addWidget(self.lineedit1)

        self.lineedit2 = QLineEdit(self)
        self.lineedit2.setPlaceholderText('Cost')
        self.vbox.addWidget(self.lineedit2)

        self.lineedit3 = QLineEdit(self)
        self.lineedit3.setPlaceholderText('URL')
        self.vbox.addWidget(self.lineedit3)

        self.lineedit4 = QLineEdit(self)
        self.lineedit4.setPlaceholderText('Note')
        self.vbox.addWidget(self.lineedit4)

        if self.id != -1:
            # Get data from db
            wish = get_wish(self.id)
            print(wish)

            self.lineedit1.setText(str(wish[1]))
            self.lineedit2.setText(str(wish[2]))
            self.lineedit3.setText(str(wish[3]))
            self.lineedit4.setText(str(wish[4]))

        self.vbox.addStretch(1)

        # Кнопка для создания новго желания
        self.addButton = QPushButton("Save")
        self.addButton.clicked.connect(self.saveWish)
        self.vbox.addWidget(self.addButton)

        self.setLayout(self.vbox)

    def saveWish(self):
        if self.id == -1:
            self.insertData()
            self.changeWidget()
        else:
            self.updateData()
            self.changeWidget()

    def insertData(self):
        db = get_db()
        with db:
            cur = db.cursor()
            insert_data = (''.join(self.lineedit1.text()),
                           ''.join(self.lineedit2.text()),
                           ''.join(self.lineedit3.text()),
                           ''.join(self.lineedit4.text()))
            insert_query = """
                            INSERT INTO wishlist
                            (title, price, link, note)
                            VALUES {}
                            """.format(insert_data)
            print(insert_query)
            cur.execute(insert_query)
            db.commit()
            QMessageBox.about(self, 'Connection', 'Data succesfully inserted')
            self.parent().list_widget.test()

    def updateData(self):
        db = get_db()
        with db:
            cur = db.cursor()

            insert_query = """
                            UPDATE wishlist
                            SET title = '{}',
                                price = {},
                                link = '{}',
                                note = '{}'
                            WHERE id = {}

                            """.format(''.join(self.lineedit1.text()),
                                       int(self.lineedit2.text()),
                                       ''.join(self.lineedit3.text()),
                                       ''.join(self.lineedit4.text()),
                                       self.id)
            print(insert_query)
            cur.execute(insert_query)
            db.commit()
            QMessageBox.about(self, 'Connection', 'Data succesfully updated')

    def changeWidget(self):
        self.parent().listCentral()


class oneWish():
    def __init__(self, data, table_id):
        self.id = data[0]
        self.title = data[1]
        self.price = data[2]
        self.link = data[3]
        self.note = data[4]
        self.table_id = table_id


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
