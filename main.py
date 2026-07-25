import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import StaTranslator
from core.project_manager import ProjectManager
from controller.app_controller import AppController


def main():
    app = QApplication(sys.argv)
    model = ProjectManager()
    view = StaTranslator()
    controller = AppController(model, view)
    view.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
