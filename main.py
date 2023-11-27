import sys
from math import cos, sin, tan
from PyQt5 import QtWidgets
from PyQt5.uic.properties import QtGui
from qt_material import apply_stylesheet
from ui_Calculator import Ui_CaculatorWin
import sqlite3

try:
    # Включите в блок try/except, если вы также нацелены на Mac/Linux
    from PyQt5.QtWinExtras import QtWin
    myappid = 'mycompany.myproduct.subproduct.version'
    QtWin.setCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

db_request, db_result = str(), str()

# Основной класс программы.


class Calculator(QtWidgets.QWidget, Ui_CaculatorWin):

    # Инициализация классса и подключение к базе данных.

    def __init__(self):
        super(Calculator, self).__init__()
        self.con_r = sqlite3.connect("Results.sqlite")
        self.con_t = sqlite3.connect("Theme.sqlite")
        self.setupUi(self)
        self.expression = ''
        self.resultfinished = False

    # Вывод нажатого символа на экран.

    def CalObjPressed(self):
        global db_request
        if self.resultfinished:
            self.ClearInput()
        pbutton = self.sender()
        character = pbutton.text()
        db_request += character
        self.CalculatorDisplay.insertPlainText(character)
        self.expression += character

    def ctg_eval(self):
        se = str(self.expression)
        sef = se.find("ctg(")
        ctg = str(se[sef:se[sef:].find(")")])


    # Вычисление результата и обработка ошибок.

    def ExecuteCalculate(self):
        global db_result, db_request

        if "()" in db_request:
            db_request = db_request[2::]
        self.CalculatorDisplay.append("=")
        global_area = {}
        try:
            result = eval(self.expression)
            db_result = result
        except Exception as e:
            self.CalculatorDisplay.append(f"Результат расчета неверен, причина ошибки: \n - {str(e).capitalize()}")
        else:
            self.CalculatorDisplay.append(str(result))

        self.resultfinished = True

        self.AddDataToTable(db_request, db_result)

        db_result, db_request = "", ""

    # Очищение ввода.

    def ClearInput(self):
        self.CalculatorDisplay.clear()
        self.expression = ''
        self.resultfinished = False

    # Добавление выражения и результата в базу данных.

    def AddDataToTable(self, req, res):
        cur = self.con_r.cursor()
        data = req, res
        cur.execute(f"""INSERT INTO Results (Req, Res) VALUES (?, ?)""", data)
        self.con_r.commit()

    # Обновление истории запросов.

    def Update_Result(self):
        cur = self.con_r.cursor()
        results = cur.execute("SELECT * FROM Results").fetchall()

        row = len(results)
        self.tableWidget.setRowCount(row)

        for i, elem in enumerate(results):
            for j, val in enumerate(elem):
                if j == 2 and val == "":
                    self.tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem("Ошибка"))
                else:
                    self.tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem(str(val)))
        self.modified = {}

    def Set_Theme(self):
        cur1 = self.con_t.cursor()
        current_theme = str(cur1.execute("SELECT * FROM Theme").fetchall())[3:-4]
        apply_stylesheet(app, theme=f'{current_theme}.xml')
        self.modified = {}

    def copy_elem(self):
        # Получаем список элементов без повторов и их id
        rows = list(set([el.row() for el in self.tableWidget.selectedItems()]))
        ids = [self.tableWidget.item(el, 0).text() for el in rows]
        # Не забываем зафиксировать изменения
        cur = self.con_r.cursor()
        req = cur.execute("SELECT Req FROM Results WHERE id = ?", ids).fetchall()
        self.CalculatorDisplay.insertPlainText(str(req)[3:-4])
        self.con_r.commit()

    def change_theme(self):
        cur1 = self.con_t.cursor()
        theme_change = self.theme.currentText()
        apply_stylesheet(app, theme=f'{str(theme_change)}.xml')
        cur1.execute(f"UPDATE Theme SET Theme = ?", (theme_change, ))
        self.con_t.commit()


# Вывод скрытых ошибок PyQt5.


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)

# Код запуска программы.


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    W = Calculator()
    W.Set_Theme()
    W.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
