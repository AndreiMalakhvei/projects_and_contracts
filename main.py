from db import PostgresqlDB
from interaction import MainMenu

if __name__ == '__main__':
    db1 = PostgresqlDB()

    menu = MainMenu()
    while True:
        menu.main_menu()
