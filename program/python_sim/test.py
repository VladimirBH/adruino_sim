import pyautogui
import time

# Эмулируем зажатие клавиши
pyautogui.keyDown('a')

# Удерживаем клавишу зажатой в течение 5 секунд
time.sleep(5)

# Отпускаем клавишу
pyautogui.keyUp('a')