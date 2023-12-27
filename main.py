from models.main import Model
from views.main import View
from controllers.main import Controller
from PIL import Image


def main():
    model = Model()
    view = View()
    controller = Controller(model, view)
    controller.start()


def get_image_dimensions(file_path):
    try:
        with Image.open(file_path) as img:
            width, height = img.size
            print(f"Wymiary obrazu: {width} x {height}")
    except Exception as e:
        print(f"Błąd: {e}")


if __name__ == "__main__":
    # Przykładowe użycie
    get_image_dimensions(r"C:\Users\48505\PycharmProjects\tkinter-multiframe-mvc\red2.png")
    main()
