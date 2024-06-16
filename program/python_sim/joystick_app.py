from CTkMessagebox import CTkMessagebox
import customtkinter as ctk
import serial
import serial.tools.list_ports
import pyautogui
import threading
from time import sleep
from readline_serial import Readline

BAUD_RATE = 9600


class JoystickApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Настройка джойстика под Atari2600")
        self.geometry("400x450")
        self.resizable(width=False, height=False)
        
        self.label = ctk.CTkLabel(self, text="Настройка джойстика", font=("Arial", 20))
        self.label.pack(pady=20)
        
        self.__ports = []
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.__ports.append(port.device)

        self.__selected_port = self.__ports[0]
        self.__selected_mode = "Стандарт"
        self.label_ports = ctk.CTkLabel(self, text=f"Устройство:")
        self.label_ports.pack(padx=5)
        self.combobox_com_ports = ctk.CTkComboBox(self, values=self.__ports, command=self.combobox_ports_callback, state="readonly")
        self.combobox_com_ports.set(self.__selected_port)
        self.combobox_com_ports.pack(padx=5)

        self.__modes = ["Стандарт", "Игра"]
        
        self.label_mode = ctk.CTkLabel(self, text=f"Режим:")
        self.label_mode.pack(padx=5)
        self.combobox_mode = ctk.CTkComboBox(self, values=self.__modes, command=self.combobox_mode_callback, state="readonly")
        self.combobox_mode.set("Стандарт")
        self.combobox_mode.pack(padx=5)
 
        self.bind_buttons = {}
        self.bindings = {
            1: "up",
            2: "down",
            3: "left", 
            4: "right",
            5: "space"
        }

        self.create_bind_buttons()

        serial_thread = threading.Thread(target=self.read_serial_standard)
        serial_thread.daemon = True
        serial_thread.start()
        
        self.__is_stop_thread_read_serial_standard = False
        self.__is_stop_thread_read_serial_game = True
        

    def create_bind_buttons(self):
        commands = ["UP", "DOWN", "LEFT", "RIGHT", "SPACE"]
        i = 0
        for action in self.bindings:
            frame = ctk.CTkFrame(self)
            frame.pack(pady=10)
            label = ctk.CTkLabel(frame, text=f"Привязка клавиши на {commands[i]}:")
            label.pack(side="left", padx=5)
            button = ctk.CTkButton(frame, text=self.bindings[action], command=lambda cmd=action: self.bind_key(cmd))
            button.pack(side="right", padx=5)
            self.bind_buttons[action] = button
            i += 1

    def bind_key(self, command):
        self.unbind_all("<KeyPress>")
        self.label.configure(text=f"Нажмите клавишу для привязки к {command}")
        self.bind("<KeyPress>", lambda event, cmd=command: self.set_binding(event, cmd))

    def set_binding(self, event, command):
        self.bindings[command] = event.keysym
        self.bind_buttons[command].configure(text=event.keysym)
        self.label.configure(text="Настройка джойстика")
        self.unbind_all("<KeyPress>")

    def combobox_ports_callback(self, choice):
        self.__is_stop_thread_read_serial_standard = True
        self.__is_stop_thread_read_serial_game = True
        sleep(0.5)
        self.__selected_port = choice
        self.combobox_mode_callback(self.__selected_mode)


    def combobox_mode_callback(self, choice):
        if choice == "Стандарт":
            self.__selected_mode = "Стандарт"
            self.__is_stop_thread_read_serial_game = True
            sleep(1)
            self.__is_stop_thread_read_serial_standard = False
            serial_thread = threading.Thread(target=self.read_serial_standard)
            serial_thread.daemon = True
            serial_thread.start()
        elif choice == "Игра":
            self.__selected_mode = "Игра"
            self.__is_stop_thread_read_serial_standard = True
            sleep(1)
            self.__is_stop_thread_read_serial_game = False
            serial_thread_game = threading.Thread(target=self.read_serial_game)
            serial_thread_game.daemon = True
            serial_thread_game.start()
        
        
    def read_serial_standard(self):
        try:
            ser = serial.Serial(self.__selected_port, BAUD_RATE)
            while self.__is_stop_thread_read_serial_standard == False:     
                if ser.in_waiting > 0:
                    line = Readline(ser).readline().decode('utf-8').strip()
                    command = line.split(";")[0]
                    action = int(command)
                    if action in self.bindings:
                        pyautogui.press(self.bindings[action])  
            ser.close()
        except serial.SerialException as e:
            CTkMessagebox(title="Ошибка", 
                                message=e,
                                icon="cancel",
                                option_1="Ok") 
                
    def read_serial_game(self):
        try:
            ser = serial.Serial(self.__selected_port, BAUD_RATE)
            while self.__is_stop_thread_read_serial_game == False:
                if ser.in_waiting > 0:
                    line = Readline(ser).readline().decode('utf-8').strip()
                    commands = line.split(";")
                    if commands[len(commands)-1] == '':
                        commands = commands[0:len(commands)-1]
                    keys = []
                    for command in commands:
                        action = int(command)
                        if action in self.bindings:
                            keys.append(self.bindings[action])
                            pyautogui.keyDown(self.bindings[action])
                    
                    line_check = Readline(ser).readline().decode('utf-8').strip()                   
                    while line == line_check:
                        for key in keys:
                            pyautogui.keyDown(key)
                        line_check = Readline(ser).readline().decode('utf-8').strip()
                    
                    for key in keys:
                        pyautogui.keyUp(key) 
                    
            ser.close()  
        except serial.SerialException as e:
            CTkMessagebox(title="Ошибка", 
                                message=e,
                                icon="cancel",
                                option_1="Ok") 