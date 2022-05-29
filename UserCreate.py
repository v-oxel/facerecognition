from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtUiTools import *
from PySide2.QtGui import *
import cv2
import qimage2ndarray
import sys
import threading
import hashlib
import os

# Путь до домашней папки
faceRecognitionPath: str = os.path.expanduser("~")
if sys.platform == "win32":
    faceRecognitionPath += "\\FaceRecognition\\"
else:
    faceRecognitionPath += "/FaceRecognition/"

# Конец видеопотока?
isStreamEnd: bool = False
# Сделана фотография?
isPhotoTaken: bool = False
# Сохранен пароль?
isPasswordEnter: bool = False

# Видеопоток opencv
cap = cv2.VideoCapture(0)
ret, frame = cap.read()

# Приложение
app: QApplication = QApplication([])
# Главное окно
window: QWidget = QWidget()
# Кнопка выхода
button: QPushButton = QPushButton("Выход")
# Окно потока
label: QLabel = QLabel("Нет камеры")
# Кнопка сохранить фото
buttonStream: QPushButton = QPushButton("Сохранить фото")
# Строка для ввода пароля
passwordLine: QLineEdit = QLineEdit()
# Кнопка сохранить пароль
buttonPassword: QPushButton = QPushButton("Сохранить пароль")
# Макет окна
layout: QVBoxLayout = QVBoxLayout()


# Функция вывода кадра из видеопотока
def displayFrame():
    while True:
        global isStreamEnd
        global frame
        if (isStreamEnd):
            break
        global cap
        global label
        # Считываем кадр из видеопотока
        ret, frame = cap.read()
        # Перевод кадра из BGR формата в RGB формат
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Преобразование из массива RGB в QImage
        image: QImage = qimage2ndarray.array2qimage(frame)
        # Отображение кадра в label
        label.setPixmap(QPixmap.fromImage(image))


# Поток вывода кадра из видеопотока
streamThread: threading.Thread = threading.Thread(target=displayFrame)


# Функция остановки приложения
def stopApp():
    global isPhotoTaken
    global isPasswordEnter
    # Если фото или пароль не сохранены, то приложение не закроется, а пользователь получит соответствующее предупреждение
    if (not isPhotoTaken) or (not isPasswordEnter):
        msgbox = QMessageBox()
        msgbox.setWindowTitle("Ошибка!")
        msgbox_txt = ""
        if (not isPhotoTaken):
            msgbox_txt += "Вы должны сохранить фото!"
        elif (not isPasswordEnter):
            msgbox_txt += "Вы должны сохранить пароль!"
        msgbox.setText(msgbox_txt)
        msgbox.exec_()
        return 1
    global isStreamEnd
    isStreamEnd = True
    global streamThread
    streamThread.join()
    sys.exit(0)


# Функция сохраняющая фото
def stopStream():
    global isStreamEnd
    isStreamEnd = True
    global streamThread
    streamThread.join()

    global frame
    global label
    image: QImage = qimage2ndarray.array2qimage(frame)
    label.setPixmap(QPixmap.fromImage(image))
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    cv2.imwrite(faceRecognitionPath + "face.png", frame)
    global isPhotoTaken
    isPhotoTaken = True


# Функция сохраняющая пароль
def passwordEnter():
    global passwordLine
    filePath = faceRecognitionPath + "password.txt"
    file = open(filePath, "w", encoding="utf-8")
    # Сохраняется не пароль, а его хеш
    file.write(hashlib.sha256(passwordLine.text().encode("utf-8")).hexdigest())
    file.close()
    global isPasswordEnter
    isPasswordEnter = True


def main() -> int:
    global cap
    global streamThread
    global app
    global window
    global button
    global label
    global buttonStream
    global passwordLine
    global buttonPassword
    global layout

    try:
        # Создание домашней папки
        os.mkdir(faceRecognitionPath)
    except FileExistsError as error:
        print(end='')

    # Настройка opencv
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

    streamThread.start()

    button.clicked.connect(stopApp)
    buttonStream.clicked.connect(stopStream)
    buttonPassword.clicked.connect(passwordEnter)

    layout.addWidget(button)
    layout.addWidget(label)
    layout.addWidget(buttonStream)
    layout.addWidget(passwordLine)
    layout.addWidget(buttonPassword)
    window.setLayout(layout)
    window.setWindowTitle("Face Recognition - Создание пользователя")
    window.show()
    app.exec_()
    return 0


if __name__ == "__main__":
    main()
