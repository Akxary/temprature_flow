import tkinter as tk
from ttkbootstrap import Style
from ttkbootstrap.widgets import Button

# Создаем основное окно
root = tk.Tk()
style = Style(theme='solar')  # Выбираем тему (например, 'cosmo', 'flatly', 'darkly')

# Добавляем виджеты
label = tk.Label(root, text="Привет, мир!", font=('Helvetica', 18))
label.pack(pady=20)

button = Button(root, text="Нажми меня", style='primary.TButton')
button.pack(pady=10)

if __name__ == "__main__":
    # Запускаем главный цикл
    root.mainloop()