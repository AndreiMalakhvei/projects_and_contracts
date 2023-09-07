import sys
from choice_handlers import ProjectHandler, ContractHandler

# here define a decorator for hot keys + header/footer

class MainMenu:

    def __init__(self):
        self.project_handler = ProjectHandler("projects")
        self.contract_handler = ContractHandler("contracts")


    def main_menu(self):
        choice = int(input("ГЛАВНОЕ МЕНЮ\nВыберите нужный пункт меню:\n1. Проект\n2. Договор\n"
                           "3.Завершить работу с программой\nВаш выбор: "))
        if choice == 1:
            self.project_menu()
        elif choice == 2:
            self.contract_menu()
        elif choice == 3:
            sys.exit(0)
        else:
            print("Вы ввели неверный запрос")
            self.main_menu()

    def project_menu(self):
        choice = int(input("МЕНЮ ПРОЕКТА\nВыберите нужный пункт меню:\n1. Создать новый проект\n2. Выбрать проект\n\nВаш выбор: "))
        if choice == 1:
            if self.project_handler.any_active_contract_exists():
                self.project_handler.create_object()
            else:
                print("Для начала Вы должны создать хотя бы один договор со статусом 'active'")
        elif choice == 2:
            project_id = self.project_handler.choose_from_list()
            self.single_project_menu(project_id)
        else:
            print("Вы ввели неверный запрос")
            self.project_menu()

    def single_project_menu(self, id):
        self.project_handler.retrieve_object_info(id)
        choice = int(input(
            "Выберите нужный пункт меню:\n1. Добавить договор в проект\n2. Завершить активный договор\n\nВаш выбор: "))
        if choice == 1:
            self.project_handler.add_contract_to_project(id)
        elif choice == 2:
            self.project_handler.close_active_contract(id)
        else:
            print("Вы ввели неверный запрос")
            self.single_project_menu(id)


    def contract_menu(self):
        choice = int(input("МЕНЮ ДОГОВОРА\nВыберите нужный пункт меню:\n1. Создать новый договор\n2. Подтвердить договор\n"
                           "3.Завершить договор\nВаш выбор: "))
        if choice == 1:
            self.contract_handler.create_object()
        elif choice == 2:
            self.contract_handler.activate_contract()
        elif choice == 3:
            self.contract_handler.close_contract()
        else:
            print("Вы ввели неверный запрос")
            self.contract_menu()
