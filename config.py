import pyautogui as pag


class Config:
    MAX_SIZE_WIDTH = int(int(pag.size()[0])  - (int(pag.size()[0]) / 100 * 20))
    MAX_SIZE_HEIGHT = int(int(pag.size()[1]) - (int(pag.size()[1]) / 100 * 15))
    PATH_FONT = r"C:\Windows\Fonts\tahoma.ttf"
    MAX_SIZE_BTN_WIDTH = 120
    MAX_SIZE_BTN_HEIGHT = 40
