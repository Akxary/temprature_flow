from cx_Freeze import setup, Executable


# Указываем пакеты, которые нужно включить
build_options = {
    "packages": ["pandas", "scipy", "customtkinter", "matplotlib"],  # Перечислите здесь ваши пакеты
    # "excludes": [],  # Пакеты, которые нужно исключить
    # "include_files": ["data/", "images/"]  # Внешние файлы (например, изображения, конфиги)
}

# Настройка сборки
setup(
    name="Temperature Flow",
    version="1.0",
    description="Python GUI Application",
    options={"build_exe": build_options},
    executables=[Executable("main.py", base="Win32GUI")]  # base="Win32GUI" для GUI-приложений
)
