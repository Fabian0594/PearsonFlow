from gui.app import App
import sys
import traceback
import argparse
import os

def setup_environment():
    """Configurar el entorno de ejecución."""
    # Configura variables de entorno para matplotlib
    os.environ['MPLBACKEND'] = 'Agg'  # Evitar problemas con backends en algunos sistemas
    
    # Configurar opciones de NumPy para mejorar el rendimiento
    try:
        import numpy as np
        np.seterr(divide='ignore', invalid='ignore')  # Ignorar advertencias comunes
    except ImportError:
        pass

def parse_args():
    """Analizar argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(description='PearsonFlow - Visualizador de datos con IA')
    parser.add_argument('--file', '-f', help='Ruta al archivo CSV para cargar automáticamente')
    parser.add_argument('--debug', action='store_true', help='Activar modo de depuración')
    return parser.parse_args()

def main():
    """Punto de entrada principal de la aplicación."""
    try:
        # Configurar el entorno
        setup_environment()
        
        # Analizar argumentos
        args = parse_args()
        
        # Configurar modo de depuración si es necesario
        if args.debug:
            import logging
            logging.basicConfig(level=logging.DEBUG)
            logging.debug("Modo de depuración activado")
        
        # Iniciar la aplicación
        file_to_load = args.file if args.file and os.path.exists(args.file) else None
        app = App(file_to_load)
        
    except KeyboardInterrupt:
        print("\nAplicación cerrada por el usuario.")
        return 0
    except Exception as e:
        print(f"Error inesperado: {e}")
        traceback.print_exc()
        return 1
    finally:
        # Limpiar recursos
        try:
            import matplotlib.pyplot as plt
            plt.close('all')  # Cerrar todas las figuras de matplotlib
        except:
            pass
    return 0

if __name__ == "__main__":
    sys.exit(main())

        