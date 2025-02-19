from cx_Freeze import setup, Executable


# Указываем пакеты, которые нужно включить
build_options = {
    "packages": [
        "pandas",
        "scipy",
        "customtkinter",
        "matplotlib",
    ],  # Перечислите здесь ваши пакеты
    "excludes": [
        "pytest",
        "black",
        "pyright",
        "scipy-stubs",
        "pandas-stubs",
        "pytest-mypy",
        "matplotlib-stubs",
        "cx-freeze",
        # "scipy.linalg",
        "scipy.fft",
        "scipy.signal",
        # "scipy.sparse",
        "scipy.integrate",
        "scipy.io",
        "scipy.interpolate",
        "scipy.ndimage",
        "scipy.special",
        "scipy.cluster",
        "scipy.constants",
        "scipy.misc",
        "scipy.odr",
        "scipy.spatial",
        "scipy.weave",
    ],  # Пакеты, которые нужно исключить
    "include_files": ["config.json"],  # Внешние файлы (например, изображения, конфиги)
}

# Настройка сборки
setup(
    name="Temperature Flow",
    version="1.0",
    description="Python GUI Application",
    options={"build_exe": build_options},
    executables=[
        Executable("main.py", base="Win32GUI")
    ],  # base="Win32GUI" для GUI-приложений
)
