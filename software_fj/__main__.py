"""Interfaz de consola: modo demostración o modo interactivo."""

import argparse
import logging
from .demo import ejecutar_simulaciones, resumen
from .errores import GestionError
from .gestion import SistemaGestion
from .modelos import Sala, Equipo, Asesoria
from .registro import configurar_registro, ruta_registro_por_defecto

LOG = logging.getLogger("software_fj")


def poblar_servicios(sistema: SistemaGestion) -> None:
    """Catálogo inicial en memoria para permitir probar el menú."""
    sistema.registrar_servicio(Sala("S01", "Sala de reuniones", 85000, 10))
    sistema.registrar_servicio(Equipo("E01", "Portátil profesional", 50000, 3))
    sistema.registrar_servicio(Asesoria("A01", "Asesoría de software", 110000,
                                      "Desarrollo de software", 15000))


def menu() -> None:
    sistema = SistemaGestion()
    poblar_servicios(sistema)
    opciones = "\n1. Registrar cliente\n2. Listar clientes\n3. Ver servicios\n4. Crear reserva\n5. Ver reservas\n6. Cancelar reserva\n0. Salir\n"
    while True:
        print(opciones)
        try:
            opcion = input("Seleccione una opción: ").strip()
            if opcion == "0":
                print("Cierre correcto de la aplicación.")
                LOG.info("Fin de la sesión interactiva")
                return
            elif opcion == "1":
                cliente = sistema.registrar_cliente(
                    input("Identificador: "), input("Nombre: "),
                    input("Correo: "), input("Teléfono: "))
                print("Registrado:", cliente.describir())
            elif opcion == "2":
                for cliente in sistema.clientes:
                    print(cliente.describir())
                if not sistema.clientes:
                    print("No hay clientes registrados.")
            elif opcion == "3":
                for servicio in sistema.servicios:
                    print(servicio.identificador, servicio.describir())
            elif opcion == "4":
                reserva = sistema.crear_reserva(
                    input("Código reserva: "), input("Código cliente: "),
                    input("Código servicio: "), input("Inicio (AAAA-MM-DD HH:MM): "),
                    input("Duración (horas enteras): "), input("Impuesto (0..1; ej. 0.19): ") or "0",
                    input("Descuento (0..1; ej. 0.10): ") or "0")
                print(reserva.describir())
            elif opcion == "5":
                for reserva in sistema.reservas:
                    print(reserva.describir())
                if not sistema.reservas:
                    print("No hay reservas registradas.")
            elif opcion == "6":
                reserva = sistema.cancelar_reserva(input("Código de reserva: "))
                print("Se canceló la reserva:", reserva.identificador)
            else:
                print("Opción inválida. Intente de nuevo.")
                LOG.warning("Selección de menú inválida")
        except GestionError as error:
            LOG.error("Error controlado de menú: %s: %s", type(error).__name__, error)
            print(f"Operación no realizada: {error}. Puede continuar.")
        except (KeyboardInterrupt, EOFError):
            LOG.info("Sesión interrumpida por el usuario")
            print("\nSesión finalizada sin pérdida de estabilidad.")
            return
        except Exception:
            LOG.exception("Fallo inesperado durante la sesión de menú")
            print("Se presentó un error inesperado; revise el log y vuelva a intentar.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Gestor de clientes, servicios y reservas Software FJ")
    parser.add_argument("--demo", action="store_true", help="Ejecuta veinte simulaciones trazables")
    parser.add_argument("--log", default=None, help="Ruta personalizada del registro de eventos")
    args = parser.parse_args()
    ruta_log = args.log if args.log else ruta_registro_por_defecto()
    configurar_registro(ruta_log)
    print(f"Archivo de log: {ruta_log}")
    if args.demo:
        resultados, _ = ejecutar_simulaciones()
        print("N.º | Caso | Estado | Observación")
        print("-" * 95)
        for fila in resultados:
            print(f"{fila['numero']:>2} | {fila['caso']:<35} | {fila['resultado']:<8} | {fila['observacion'][:60]}")
        print(resumen(resultados))
        if any(c["resultado"] == "FALLIDA" for c in resultados):
            raise SystemExit(1)
    else:
        menu()


if __name__ == "__main__":
    main()
