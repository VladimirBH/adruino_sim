from CTkMessagebox import CTkMessagebox
import customtkinter as ctk
import serial
import serial.tools.list_ports
import pyautogui
import threading
from time import sleep
from readline_serial import Readline
from tkinter import filedialog, messagebox
import json


BAUD_RATE = 9600

class JoystickApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Настройка джойстика под Atari2600")
        self.geometry("400x550+500+200")
        self.resizable(width=False, height=False)
        
        self.label = ctk.CTkLabel(self, text="Настройка джойстика", font=("Arial", 20))
        self.label.pack(pady=20)
        
        self.__ports = []
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.__ports.append(port.device)

        self.__selected_port = self.__ports[0]
        self.__selected_mode = "Стандарт"
        self.__modes = ["Стандарт", "Игра"]
        
        self.label_ports = ctk.CTkLabel(self, text=f"Устройство:")
        self.label_ports.pack(padx=5)
        self.combobox_com_ports = ctk.CTkComboBox(self, values=self.__ports, command=self.combobox_ports_callback, state="readonly")
        self.combobox_com_ports.set(self.__selected_port)
        self.combobox_com_ports.pack(padx=5)
        
        self.label_mode = ctk.CTkLabel(self, text=f"Режим:")
        self.label_mode.pack(padx=5)
        self.combobox_mode = ctk.CTkComboBox(self, values=self.__modes, command=self.combobox_mode_callback, state="readonly")
        self.combobox_mode.set("Стандарт")
        self.combobox_mode.pack(padx=5)
  
        self.bind_buttons_game = {}
        self.bindings_game = {
            1: "up",
            2: "down",
            3: "left", 
            4: "right",
            5: "space"
        }
        
        self.bind_buttons_standard = {}
        self.bindings_standard = {
            1: [],
            2: [],
            3: [],
            4: [],
            5: []
        }

        self.create_save_load_buttons()
        
        #Создание фреймов для кнопок

        #В режиме "Игра"
        self.frame_game = ctk.CTkFrame(self)

        #В режиме "Стандарт"        
        self.frame_standard = ctk.CTkFrame(self)
        self.frame_standard.pack(pady=10)
        
        self.create_bind_buttons()

        self.__is_stop_thread_read_serial_standard = False
        self.__is_stop_thread_read_serial_game = True
        
        self.start_thread(self.read_serial_standard)
        

    def create_bind_buttons(self):
        commands = ["UP", "DOWN", "LEFT", "RIGHT", "SPACE"]
        i = 0
        for action in self.bindings_game:
            frame1 = ctk.CTkFrame(self.frame_game)
            frame1.pack(pady=10)
            label = ctk.CTkLabel(frame1, text=f"Привязка клавиши на {commands[i]}:")
            label.pack(side="left", padx=5)
            button_game = ctk.CTkButton(frame1, text=self.bindings_game[action], command=lambda cmd=action: self.bind_key(cmd))
            button_game.pack(side="right", padx=5)
            self.bind_buttons_game[action] = button_game
            i += 1
        
        i = 0
        for action in self.bindings_standard:    
            frame = ctk.CTkFrame(self.frame_standard)
            frame.pack(pady=10)
            label = ctk.CTkLabel(frame, text=f"Привязка клавиши на {commands[i]}:")
            label.pack(side="left", padx=5)
            button_standard = ctk.CTkButton(frame, text=self.get_combination_text(action), command=lambda cmd=action: self.bind_key(cmd))
            button_standard.pack(side="right", padx=5)
            self.bind_buttons_standard[action] = button_standard
            i += 1


    def bind_key(self, command):
        if self.__selected_mode == "Игра":
            self.unbind_all("<KeyPress>")
            self.label.configure(text=f"Нажмите клавишу для привязки к {command}")
            self.bind("<KeyPress>", lambda event, cmd=command: self.set_binding(event, cmd))
        elif self.__selected_mode == "Стандарт":
            self.bindings_standard[command].clear()
            self.bind_buttons_standard[command].configure(text="")
            self.unbind_all("<KeyPress>")
            self.label.configure(text=f"Нажмите клавишу для привязки к {command} \n(нажмите Enter для подтверждения)")
            self.bind("<KeyPress>", lambda event, cmd=command: self.set_binding(event, cmd))

    #Настройка клавиш
    def set_binding(self, event, command):
        if self.__selected_mode == "Игра":
            self.bindings_game[command] = event.keysym
            self.bind_buttons_game[command].configure(text=event.keysym)
            self.label.configure(text="Настройка джойстика")
            self.unbind_all("<KeyPress>")
        elif self.__selected_mode == "Стандарт":
            if event.keysym == "Return":
                self.unbind_all("<KeyPress>")
                self.label.configure(text="Настройка джойстика")
                self.bind_buttons_standard[command].configure(text=self.get_combination_text(command))
            elif event.keysym not in self.bindings_standard[command]:
                self.bindings_standard[command].append(event.keysym)
                self.bind_buttons_standard[command].configure(text=self.get_combination_text(command))

    def combobox_ports_callback(self, choice):
        self.__is_stop_thread_read_serial_standard = True
        self.__is_stop_thread_read_serial_game = True
        sleep(0.5)
        self.__selected_port = choice
        self.combobox_mode_callback(self.__selected_mode)

    def start_thread(self, method):
        serial_thread = threading.Thread(target=method, daemon=True)
        serial_thread.start()
        
    def combobox_mode_callback(self, choice):
        if choice == "Стандарт":
            self.__selected_mode = "Стандарт"
            self.__is_stop_thread_read_serial_game = True
            self.frame_game.pack_forget()
            self.frame_standard.pack(pady=10)
            sleep(1)
            self.__is_stop_thread_read_serial_standard = False
            self.start_thread(self.read_serial_standard)
        elif choice == "Игра":
            self.__selected_mode = "Игра"
            self.__is_stop_thread_read_serial_standard = True
            self.frame_standard.pack_forget()
            self.frame_game.pack(pady=10)
            sleep(1)
            self.__is_stop_thread_read_serial_game = False
            self.start_thread(self.read_serial_game)
        
    def get_combination_text(self, command):
        return "+".join(self.bindings_standard[command]) if self.bindings_standard[command] else "None"
        
    def read_serial_standard(self):
        try:
            ser = serial.Serial(self.__selected_port, BAUD_RATE)
            while self.__is_stop_thread_read_serial_standard == False:     
                if ser.in_waiting > 0:
                    line = Readline(ser).readline().decode('utf-8').strip()
                    command = int(line.split(";")[0])
                    if command in self.bindings_standard:
                        for key in self.bindings_standard[command]:
                            pyautogui.press(key)  
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
                        if action in self.bindings_game:
                            keys.append(self.bindings_game[action])
                            pyautogui.keyDown(self.bindings_game[action])
                    
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
            
            
    def create_save_load_buttons(self):
        frame = ctk.CTkFrame(self)
        frame.pack(pady=20)
        save_button = ctk.CTkButton(frame, text="Сохранить настройки", command=self.save_settings)
        save_button.pack(side="left", padx=10)
        load_button = ctk.CTkButton(frame, text="Загрузить настройки", command=self.load_settings)
        load_button.pack(side="right", padx=10)


    def save_settings(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'w') as file:
                bindings = []
                bindings.append(self.bindings_game)
                bindings.append(self.bindings_standard)
                json.dump(bindings, file)
                CTkMessagebox(title="Сохранение настроек", 
                                    message="Настройки успешно сохранены!",
                                    icon="check",
                                    option_1="Ok") 

    def load_settings(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'r') as file:
                bindings = json.load(file)
                self.bindings_game.clear()
                self.bindings_standard.clear()
                for key in bindings[0]:
                    self.bindings_game[int(key)] = bindings[0][key]
                    
                for key in bindings[1]:
                    self.bindings_standard[int(key)] = bindings[1][key]
                    
                for command in self.bindings_game:
                    self.bind_buttons_game[int(command)].configure(text=self.bindings_game[int(command)])
                
                for command in self.bindings_standard:
                    self.bind_buttons_standard[int(command)].configure(text=self.get_combination_text(command))
                CTkMessagebox(title="Загрузка настроек", 
                                    message="Настройки загружены",
                                    icon="check",
                                    option_1="Ok") 