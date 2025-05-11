from gui.app import App

if __name__ == "__main__":
    try:
        app = App()
    except Exception as e:
        print(f"Error inesperado: {e}")