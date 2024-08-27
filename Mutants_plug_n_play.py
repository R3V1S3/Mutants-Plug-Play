import tkinter as tk
from tkinter import ttk, messagebox
import pymysql
import wmi
import os
import webbrowser
from PIL import Image, ImageTk
import subprocess
import ctypes
import sys

def main_window(initial_tab):
    start_screen.destroy()

    # Функция для определения модели материнской платы
    def get_motherboard_model():
        global c
        c = wmi.WMI()
        for board in c.Win32_BaseBoard():
            return board.Product

# Функция для обновления информации о материнской плате
    def update_motherboard_info():
        if auto_detect_var.get():
            motherboard_label.config(state=tk.NORMAL)
            motherboard_info_label.config(state=tk.NORMAL)
            manualy_insert_label.config(state=tk.DISABLED)
            manual_insert_entry.config(state=tk.DISABLED)
        else:
            motherboard_label.config(state=tk.DISABLED)
            motherboard_info_label.config(state=tk.DISABLED)
            manualy_insert_label.config(state=tk.NORMAL)
            manual_insert_entry.config(state=tk.NORMAL)

    def switch_auto_detect():
        update_motherboard_info()

    # Функция для подключения к базе данных и выполнения запроса
    def get_database_link(cpu_variant):
        if auto_detect_var.get():
            motherboard_model = get_motherboard_model()
        else:
            motherboard_model = manual_insert_entry.get()
        
        try:
            # Установите ваши параметры подключения к базе данных
            db_connection = pymysql.connect(host='sql11.freemysqlhosting.net', user='sql11691615', password='q2p8XRUut8', database='sql11691615')
            cursor = db_connection.cursor()

            # Выполните запрос в зависимости от выбранного варианта процессора
            if cpu_variant == "QL3X/QL2X (Kaby Lake)":
                query = f"SELECT `link` FROM `QL3X/QL2X` WHERE `motherboard` = '{motherboard_model}'"
            elif cpu_variant == "QQLS/QQLT/QNCT (Coffee Lake)":
                query = f"SELECT `link` FROM `QQLS/QQLT/QNCT` WHERE `motherboard` = '{motherboard_model}'"
            else:
                return None

            cursor.execute(query)
            link = cursor.fetchone()

            cursor.close()
            db_connection.close()

            return link[0] if link else None
        except pymysql.Error as ex:
            messagebox.showerror("Connection error", f"An error occurred while connecting to the database \nCheck your internet connection")
            return link == 0

    # Функция для открытия ссылки в браузере
    def open_link():
        selected_variant = cpu_combobox.get()
        link = get_database_link(selected_variant)
        if link:
            webbrowser.open(link)
        elif link == 0:
            None
        else:
            messagebox.showerror("Error", f"No BIOS version found for the \nselected CPU and motherboard combination")

    # Функция для переключения темы
    def switch_theme():
        # Получение значения переключателя
        theme_state = switch_state.get()
        
        # Переключение темы
        if theme_state:
            root.tk.call("set_theme", "light")
        else:
            root.tk.call("set_theme", "dark")

    #Функция для запуска Open Hardware Monitor
    def start_openhardwaremonitor():
        try:
            # Путь к исполняемому файлу OpenHardwareMonitor
            openhardwaremonitor_path = os.path.join(current_dir, 'OpenHardwareMonitor/OpenHardwareMonitor.exe')

            # Запускаем OpenHardwareMonitor с параметрами, скрывающими окно
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            subprocess.Popen(openhardwaremonitor_path, startupinfo=startupinfo)
        except Exception as e:
            messagebox.showerror("OHM error", f"Error when starting Open Hardware Monitor \nTry to reinstall the app")

    #Функция завершения процесса Open Hardware Monitor при закрытии основного окна
    def on_closing():
        stop_openhardwaremonitor()
        root.destroy()

    #Функция для остановки Open Hardware Monitor
    def stop_openhardwaremonitor():
        # Завершаем процесс OpenHardwareMonitor
        subprocess.Popen("taskkill /F /IM OpenHardwareMonitor.exe", shell=True)

    #Функция получения информации о CPU
    def get_cpu_info():
        cpu_info = {}
        # Подключаемся к WMI и получаем информацию о датчиках
        w = wmi.WMI(namespace="root\\OpenHardwareMonitor")
        sensor_info = w.Sensor()
            
        # Проходимся по всем датчикам и находим информацию о температуре и напряжении CPU
        for sensor in sensor_info:
            if sensor.SensorType == 'Temperature' and sensor.Name == 'CPU Package':
                cpu_info['temperature'] = sensor.Value
            elif sensor.SensorType == 'Voltage' and sensor.Name == 'CPU VCore':
                cpu_info['vcore'] = round(sensor.Value, 3)
            elif sensor.SensorType == 'Clock' and sensor.Name == 'CPU Core #1':
                cpu_info['core_clock'] = round(sensor.Value, 1)
            elif sensor.SensorType == 'Load' and sensor.Name == 'CPU Total':
                cpu_info['cpu_load'] = round(sensor.Value, 1)
            elif sensor.SensorType == 'Power' and sensor.Name == 'CPU Package':
                cpu_info['cpu_power'] = round(sensor.Value, 1)
            elif sensor.SensorType == 'Clock' and sensor.Name == 'Bus Speed':
                cpu_info['bus_speed'] = round(sensor.Value, 1)
            elif sensor.SensorType == 'Data' and sensor.Name == 'Used Memory':
                cpu_info['used_ram'] = round(sensor.Value, 1)
            elif sensor.SensorType == 'Data' and sensor.Name == 'Available Memory':
                cpu_info['avail_ram'] = sensor.Value
        return cpu_info

    #Функция обновления информации о CPU
    def update_cpu_info_label():
        cpu_info = get_cpu_info()
        if cpu_info:
            temperature_accentbutton.config(text=f"CPU Temperature: {cpu_info.get('temperature', 'N/A')}°C")
            vcore_accentbutton.config(text=f"CPU Voltage: {cpu_info.get('vcore', 'N/A')}V")
            core_clock_accentbutton.config(text=f"CPU Frequency: {cpu_info.get('core_clock', 'N/A')}MHz")
            cpu_load_accentbutton.config(text=f"CPU Load: {cpu_info.get('cpu_load', 'N/A')}%")
            cpu_power_accentbutton.config(text=f"CPU Power: {cpu_info.get('cpu_power', 'N/A')}W")
            bus_speed_accentbutton.config(text=f"Bus Frequency: {cpu_info.get('bus_speed', 'N/A')}MHz")
            ram_accentbutton.config(text=f"RAM Used: {cpu_info.get('used_ram', 'N/A')}GB of {round(cpu_info.get('avail_ram', 'N/A') + cpu_info.get('used_ram', 'N/A'), 0)}GB")
        root.after(100, update_cpu_info_label)  # Обновление каждые 100 милисекунд

    #Функция получения частоты оперативной памяти 
    def ram_freq():
        memory_info = c.Win32_PhysicalMemory()
        return "RAM Frequency: " + str(memory_info[0].Speed) + "MHz"

    # Основное окно
    root = tk.Tk()
    root.title("Mutants - plug & play")
    root.resizable(False, False)
    root.attributes("-toolwindow", False)

    # Создание переменной для хранения состояния переключателя темы
    switch_state = tk.BooleanVar()

    #Путь к теме
    root.tk.call("source", os.path.join(current_dir, 'azure.tcl'))

    #Определение стартовой темы
    root.tk.call("set_theme", "dark")

    # Создание вкладок
    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True)

    # Вкладка "Get BIOS"
    tab1 = ttk.Frame(notebook)
    notebook.add(tab1, text="Get BIOS")

    #Переменная для переключателья автоопределения материнской платы
    auto_detect_var = tk.BooleanVar()
    auto_detect_var.set(True)

    #Лэйбл для автоопределения материнской платы
    motherboard_model = get_motherboard_model()
    motherboard_label = tk.Label(tab1, text="Automatically Detected Motherboard:")
    motherboard_label.pack(pady=(20,5))

    #Автоматически определенная модель материнской платы
    motherboard_info_label = tk.Label(tab1, text=motherboard_model)
    motherboard_info_label.pack()

    #Переключатель автоопределения материнской платы
    auto_detect_checkbutton = ttk.Checkbutton(tab1, text="Automatic Motherboard Detection", variable=auto_detect_var, style="Switch.TCheckbutton", command=switch_auto_detect)
    auto_detect_checkbutton.pack(pady=30)

    #Лэйбл для ручного ввода материнской платы
    manualy_insert_label = tk.Label(tab1, text="Insert the motherboard manually:")
    manualy_insert_label.pack()

    #Ручной ввод модели материнской платы
    manual_insert_entry = ttk.Entry(tab1, justify="center")
    manual_insert_entry.pack(pady=5)

    #Обновление state'ов для переключателя автоопределения материнской платы
    update_motherboard_info()

    #Лэйбл для выбора варианта процессора
    cpu_info_label = tk.Label(tab1, text="Choose a CPU option:")
    cpu_info_label.pack(pady=(30,5))

    #Комбобокс с вариантами процессоров
    cpu_variants = ["QL3X/QL2X (Kaby Lake)", "QQLS/QQLT/QNCT (Coffee Lake)"]
    cpu_combobox = ttk.Combobox(tab1, values=cpu_variants, width=29, state="readonly")
    cpu_combobox.set(cpu_variants[0])
    cpu_combobox.pack(pady=(0,40))

    #Кнопка получения файла
    get_data_button = ttk.Button(tab1, text="Get BIOS file", width=15, command=open_link)
    get_data_button.pack(pady=20)

    #Переключатель цветовой темы
    switch = ttk.Checkbutton(tab1, text="Switch color theme", variable=switch_state, style="Switch.TCheckbutton", command=switch_theme)
    switch.pack(side=tk.BOTTOM, pady=10)

    # Вкладка "Installation"
    tab2 = ttk.Frame(notebook)
    notebook.add(tab2, text="Installation")

    # Разделение на две страницы во вкладке "Installation"
    installation_notebook = ttk.Notebook(tab2)
    installation_notebook.pack(fill=tk.BOTH, expand=True)

    # Первая страница
    page1 = ttk.Frame(installation_notebook)
    installation_notebook.add(page1, text="Step 1")

    #Картинка для шага 1
    image1 = ImageTk.PhotoImage(Image.open(os.path.join(current_dir, 'step1.png')))

    #Текст и изображение 1
    step1_text_label = tk.Label(page1, text="Replace the motherboard BIOS with a new one")
    step1_text_label.pack(pady=1)
    step1_image_label = tk.Label(page1, image=image1)
    step1_image_label.pack(pady=(10))

    # Вторая страница
    page2 = ttk.Frame(installation_notebook)
    installation_notebook.add(page2, text="Step 2")

    #Картинка для шага 2
    image2 = ImageTk.PhotoImage(Image.open(os.path.join(current_dir, 'step2.png')))

    #Текст и изображение 2
    step2_text_label = tk.Label(page2, text="Dismantle the standard CPU mount frame")
    step2_text_label.pack(pady=1)
    step2_image_label = tk.Label(page2, image=image2)
    step2_image_label.pack(pady=10)

    # Третья страница
    page3 = ttk.Frame(installation_notebook)
    installation_notebook.add(page3, text="Step 3")

    #Картинка для шага 3
    image3 = ImageTk.PhotoImage(Image.open(os.path.join(current_dir, 'step3.png')))

    #Текст и изображение 3
    step3_text_label = tk.Label(page3, text="Install the new CPU in the motherboard socket")
    step3_text_label.pack(pady=1)
    step3_image_label = tk.Label(page3, image=image3)
    step3_image_label.pack(pady=10)

    #Четвертая страница
    page4 = ttk.Frame(installation_notebook)
    installation_notebook.add(page4, text="Step 4")

    #Картинка для шага 4
    image4 = ImageTk.PhotoImage(Image.open(os.path.join(current_dir, 'step4.png')))

    #Текст и изображение 4
    step1_text_label = tk.Label(page4, text="Secure the CPU with the new included frame")
    step1_text_label.pack(pady=1)
    step1_image_label = tk.Label(page4, image=image4)
    step1_image_label.pack(pady=10)

    # Вкладка "Installation"
    tab3 = ttk.Frame(notebook)
    notebook.add(tab3, text="Monitoring")

    # Автоматически запускаем OpenHardwareMonitor при инициализации приложения
    start_openhardwaremonitor()

    temperature_accentbutton = ttk.Button(tab3, text="", style="Accent.TButton", width=25)
    temperature_accentbutton.pack(padx=20, pady=(35, 15))

    vcore_accentbutton = ttk.Button(tab3, text="", style="Accent.TButton", width=25)
    vcore_accentbutton.pack(padx=20, pady=15)

    core_clock_accentbutton = ttk.Button(tab3, text="", style="Accent.TButton", width=25)
    core_clock_accentbutton.pack(padx=20, pady=15)

    cpu_load_accentbutton = ttk.Button(tab3, text="", style="Accent.TButton", width=25)
    cpu_load_accentbutton.pack(padx=20, pady=15)

    cpu_power_accentbutton = ttk.Button(tab3, text="", style="Accent.TButton", width=25)
    cpu_power_accentbutton.pack(padx=20, pady=15)

    bus_speed_accentbutton = ttk.Button(tab3, text="", style="Accent.TButton", width=25)
    bus_speed_accentbutton.pack(padx=20, pady=15)

    ram_freq_accentbutton = ttk.Button(tab3, text=ram_freq(), style="Accent.TButton", width=25)
    ram_freq_accentbutton.pack(padx=20, pady=15)

    ram_accentbutton = ttk.Button(tab3, text="", style="Accent.TButton", width=25)
    ram_accentbutton.pack(padx=20, pady=15)

    # Обновляем метки с информацией о CPU каждые 100 милисекунд         
    update_cpu_info_label()

    # Вкладка "Instruction"
    tab4 = ttk.Frame(notebook)
    notebook.add(tab4, text="Instruction")

    instruction_start = ttk.Label(tab4, text="If you have any problems using the app,\nplease read this instruction", justify="left")
    instruction_start.pack(pady=10)

    # Создаем вертикальную полосу прокрутки
    scrollbar = ttk.Scrollbar(tab4)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Создаем текстовое поле с прокруткой
    text_box = tk.Text(tab4, yscrollcommand=scrollbar.set, wrap=tk.WORD, width=30)
    text_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Подключаем полосу прокрутки к текстовому полю
    scrollbar.config(command=text_box.yview)

    # Добавляем текст
    text = "   In the Get BIOS section, you initially need to select only the version of the CPU you need; The model of the motherboard will be detected automatically. If you want to specify the model of the motherboard yourself, you need to switch the mode and you will have access to a line for manual input.\n\n    The Installation section provides instructions for installing the processor. If you have not installed similar modified processors before, then you should follow the steps indicated in this manual. If you have problems displaying instructions, please reinstall the application.\n\n    The Monitoring section displays the main indicators of the central processor, motherboard and RAM. During the first time after installation, you need to periodically monitor these indicators to make sure there are no errors in the operation of the installed processor. If you have errors in displaying indicators, try reinstalling the application. If the indicators are normal, but you think that the processor is not working correctly, we recommend that you turn to specialized software for monitoring indicators, where you can get more detailed information.\n\n    This version of the application is not final. We continue to improve this application. To contact the developer, you can send an email to: usshifter@gmail.com. We will respond as soon as possible."
    text_box.insert(tk.END, text)

    text_box.config(state="disabled")

    # Вызов функции для расположения окна по центру
    center_window(root)

    #Устанавливаем икноку
    root.iconbitmap(icon_path)

    # Привязываем обработчик события закрытия окна к функции on_closing
    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Открытие выбранной вкладки
    notebook.select(initial_tab)

    # Запуск главного цикла
    root.mainloop()

def start_window():
    global start_screen
    start_screen = tk.Tk()
    start_screen.title("Welcome!")
    start_screen.resizable(False, False)
    start_screen.attributes("-toolwindow", False)

    #Путь к теме
    start_screen.tk.call("source", os.path.join(current_dir, 'azure.tcl'))

    #Определение стартовой темы
    start_screen.tk.call("set_theme", "dark")

    # Создаем метку с приветствием
    label = tk.Label(start_screen, text="Welcome to Mutants Plug & Play\n\nThis application was created\nto simplify the process of using\nmodified engineering processors.\nYou can navigate to one of the 3\ntools or read the instructions\nby clicking the button below")
    label.pack(padx=10, pady=(10, 10))

    #Создаем кнопки
    get_bios_button = ttk.Button(start_screen, text="Get BIOS automatically", command=lambda: main_window(0), width=25)
    get_bios_button.pack(padx=60, pady=15)

    installation_button = ttk.Button(start_screen, text="CPU installation guide", command=lambda: main_window(1), width=25)
    installation_button.pack(padx=60, pady=15)

    monitoring_button = ttk.Button(start_screen, text="Monitoring tools", command=lambda: main_window(2), width=25)
    monitoring_button.pack(padx=60, pady=15)

    instruction_button = ttk.Button(start_screen, text="Instruction", command=lambda: main_window(3), width=25)
    instruction_button.pack(padx=60, pady=15)

    #Центрируем окно
    center_window(start_screen)

    #Устанавливаем икноку
    start_screen.iconbitmap(icon_path)

    start_screen.mainloop()

#Функция для расположения окна по центру
def center_window(window):
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x_coordinate = (screen_width - width) // 2
    y_coordinate = (screen_height - height) // 2
    window.geometry(f"+{x_coordinate}+{y_coordinate}")

#Функция проверки является ли пользователь администратором
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

#Текущая директория выполнения для работы с файлами ресурсов
current_dir = os.path.dirname(os.path.abspath(__file__))

#Путь к файлу иконки приложения
icon_path = os.path.join(current_dir, 'motherboard-icon-16.ico')

# Проверяем права администратора и запрашиваем их, если они отсутствуют
if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 0)
    sys.exit()

#Запуск стартового экрана
start_window()