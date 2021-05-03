from src.visualization import WindowGTK


def main():
    # window = Window()
    #
    # window.main_loop()

    window = WindowGTK()

    window.main_loop()


if __name__ == '__main__':
    # TODO: parse args

    main()
