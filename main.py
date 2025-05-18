from gui.app import App
import sys
import traceback

def main():
    """Punto de entrada principal de la aplicación."""
    try:
        App()
    except KeyboardInterrupt:
        print("\nAplicación cerrada por el usuario.")
        return 0
    except Exception as e:
        print(f"Error inesperado: {e}")
        traceback.print_exc()
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())

        