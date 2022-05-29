from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtUiTools import *
from PySide2.QtGui import *
import cv2
import qimage2ndarray
import sys
import os
import threading
import hashlib
import face_recognition

# Путь до домашней папки
faceRecognitionPath: str = os.path.expanduser("~")
if sys.platform == "win32":
    faceRecognitionPath += "\\FaceRecognition\\"
else:
    faceRecognitionPath += "/FaceRecognition/"

# Конец видеопотока?
isStreamEnd: bool = False

# Видеопоток opencv
cap = cv2.VideoCapture(0)

# Хеш строка пароля
passwordHash: str = ""
# Файл фотографии лица
faceImagePng = None
# Кодирование фотографии лица
faceImageEncoding = None
# Кодирование фотографии лица
faceImageEncodings = None

# Приложение
app: QApplication = QApplication([])
# Главное окно
window: QWidget = QWidget()
# Окно потока
label: QLabel = QLabel("Нет камеры")
# Строка для ввода пароля
passwordLine: QLineEdit = QLineEdit()
# Кнопка выхода (позже может быть удалена)
button: QPushButton = QPushButton("Выход")
# Кнопка для ввода пароля
button_enter: QPushButton = QPushButton("->")
# Макет окна
layout: QVBoxLayout = QVBoxLayout()

# Функция вывода кадра из видеопотока и сравнение лица
def displayFrame():
    while True:
        global isStreamEnd
        if (isStreamEnd):
            break
        global cap
        global label
        global faceImageEncoding
        global faceImageEncodings

        # Считываем кадр из видеопотока
        ret, frame = cap.read()
        # Перевод кадра из BGR формата в RGB формат
        frame: cv2.Mat = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Преобразование из массива RGB в QImage
        image: QImage = qimage2ndarray.array2qimage(frame)
        # Отображение кадра в label
        label.setPixmap(QPixmap.fromImage(image))

        # Поиск лиц в кадре
        faceLocations = face_recognition.face_locations(frame)
        # Сохранение кодированных лиц
        faceEncodings = face_recognition.face_encodings(frame, faceLocations)
        for faceEncoding in faceEncodings:
            # Если лица совпадают, то программа закрывается
            matches = face_recognition.compare_faces(
                faceImageEncodings, faceEncoding)
            print(matches)
            if True in matches:
                stopApp()


# Поток вывода кадра из видеопотока и сравнение лица
streamThread: threading.Thread = threading.Thread(target=displayFrame)


# Функция остановки приложения
def stopApp():
    global isStreamEnd
    isStreamEnd = True
    global streamThread
    streamThread.join()
    sys.exit(0)


# Функция сравнивающая хеш паролей
def passwordEnter():
    global passwordLine
    global passwordHash
    passwordLineHash = hashlib.sha256(
        passwordLine.text().encode("utf-8")).hexdigest()
    if (passwordHash == passwordLineHash):
        stopApp()


def main() -> int:
    global cap
    global passwordHash
    global streamThread
    global app
    global window
    global label
    global passwordLine
    global button
    global button_enter
    global layout

    global faceImagePng
    global faceImageEncoding
    global faceImageEncodings

    # Загрузка пользовательских данных
    try:
        file = open(faceRecognitionPath + "password.txt",
                    "r", encoding="utf-8")
        passwordHash = file.readline()
        file.close()
        file = open(faceRecognitionPath + "face.png", "r")
        file.close()
        # faceImage = cv2.imread(faceRecognitionPath + "face.png")
        faceImagePng = face_recognition.load_image_file(
            faceRecognitionPath + "face.png")
        faceImageEncoding = face_recognition.face_encodings(faceImagePng)[0]
        faceImageEncodings = [faceImageEncoding]
    except FileNotFoundError as error:
        # label.setText("User does not exist")
        # label.setAlignment(Qt.AlignCenter)
        # button.clicked.connect(sys.exit)
        # layout.addWidget(button)
        # layout.addWidget(label)
        # window.setLayout(layout)
        # window.show()
        # app.exec_()
        os.system("python UserCreate.py")

    else:
        # Настройка opencv
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

        streamThread.start()
        passwordLine.setEchoMode(QLineEdit.Password)

        button.clicked.connect(stopApp)
        button_enter.clicked.connect(passwordEnter)

        layout.addWidget(button)
        layout.addWidget(label)
        layout.addWidget(passwordLine)
        layout.addWidget(button_enter)
        window.setLayout(layout)
        window.setWindowTitle("Face Recognition")
        # Теперь окно будет поверх всех окон и свернуть его не получится
        window.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        window.setWindowState(Qt.WindowFullScreen)
        window.show()
        app.exec_()
    return 0


if __name__ == "__main__":
    main()
