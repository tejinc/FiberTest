#!/usr/local/bin/python3.8
from time import sleep
import fibertest as ft

def main():
    if not ft.no_board:
        ft.a_board = ft.board_setup()
        ft.move_initial_home(ft.end_home)
        sleep(5)
    return 0

if __name__ == "__main__":
    main()
