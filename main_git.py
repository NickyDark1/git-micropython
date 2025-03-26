# main_git.py
from github_lib import GitHubRepoManager
import time
import sys
import os
from network_iot import Network
import ubinascii
import ujson
import gc

# Configuración de red Wi-Fi
ssid = ""
password = ""
static_ip_config = None

# Carpeta por defecto para subir archivos
CARPETA_PROYECTO = "proyecto"

# Conectar a la red
net = Network(ssid, password, static_ip_config)
if not net.conectar():
    print("Error al conectar la red. Saliendo...")
    sys.exit()

print("Conexión establecida.")

# Configuración
TOKEN = ""  # Reemplaza con tu token real

# Crear instancia del gestor
repo_manager = GitHubRepoManager(TOKEN)

# Función mejorada para subir archivos a un repositorio
def subir_archivos(owner, repo_name, directorio_local=CARPETA_PROYECTO):
    """
    Sube todos los archivos de un directorio al repositorio usando el método upload_file
    
    Args:
        owner (str): Propietario del repositorio
        repo_name (str): Nombre del repositorio
        directorio_local (str): Directorio con los archivos a subir (por defecto 'proyecto')
    """
    print(f"Buscando archivos en '{directorio_local}'...")
    
    try:
        # Asegurar que el directorio termine con /
        if not directorio_local.endswith('/'):
            directorio_local += '/'
            
        archivos = os.listdir(directorio_local)
        print(f"Encontrados {len(archivos)} elementos en '{directorio_local}'")
        
        # Contar éxitos y errores
        subidos = 0
        errores = 0
        
        for archivo in archivos:
            ruta_local = directorio_local + archivo
            
            # Verificar si es un archivo (no directorio)
            try:
                es_directorio = os.stat(ruta_local)[0] & 0x4000 != 0
                if es_directorio:
                    print(f"Omitiendo directorio: {archivo}")
                    continue
                    
                print(f"Subiendo {ruta_local}...")
                
                # Usar el método upload_file de la clase GitHubRepoManager
                resultado = repo_manager.upload_file(
                    owner=owner,
                    repo_name=repo_name,
                    file_path=ruta_local,
                    remote_path=archivo,
                    commit_message=f"Subiendo {archivo} desde MicroPython"
                )
                
                if 'error' in resultado:
                    print(f"Error al subir {archivo}: {resultado['error']}")
                    if 'details' in resultado:
                        if isinstance(resultado['details'], dict) and 'message' in resultado['details']:
                            print(f"Detalles: {resultado['details']['message']}")
                        else:
                            print(f"Detalles: {resultado['details']}")
                    errores += 1
                else:
                    print(f"Archivo {archivo} subido correctamente")
                    subidos += 1
                
                # Liberar memoria
                gc.collect()
                
                # Esperar entre subidas para no sobrecargar la API
                time.sleep(1)
                
            except Exception as e:
                print(f"Error procesando {archivo}: {e}")
                import sys
                sys.print_exception(e)  # Muestra el traceback completo
                errores += 1
                
        print(f"Proceso completado. Archivos subidos: {subidos}, Errores: {errores}")
        
    except OSError as e:
        print(f"Error al acceder al directorio '{directorio_local}': {e}")

# Menú interactivo para gestionar repositorios
def mostrar_menu():
    print("\n=== GESTOR DE REPOSITORIOS GITHUB ===")
    print("1. Crear nuevo repositorio")
    print("2. Listar mis repositorios")
    print("3. Actualizar repositorio existente")
    print("4. Eliminar repositorio")
    print("5. Listar repositorios de otro usuario")
    print("6. Subir archivos a un repositorio")
    print("7. Crear repositorio y subir archivos automáticamente")
    print("8. Descargar archivo de un repositorio")
    print("9. Crear carpeta en un repositorio")
    print("0. Salir")
    
    try:
        return input("Selecciona una opción: ")
    except:
        return "0"

def crear_repositorio():
    try:
        nombre = input("Nombre del repositorio: ")
        descripcion = input("Descripción (opcional, presiona Enter para omitir): ")
        if not descripcion:
            descripcion = None
        
        privado = input("¿Repositorio privado? (s/n): ").lower() == 's'
        inicializar = input("¿Inicializar con README? (s/n): ").lower() == 's'
    except KeyboardInterrupt:
        print("\nOperación cancelada")
        return
    
    print("Creando repositorio...")
    resultado = repo_manager.create_repository(
        nombre, 
        description=descripcion,
        private=privado,
        auto_init=inicializar
    )
    
    if 'error' in resultado:
        print(f"Error: {resultado['error']}")
        if 'details' in resultado:
            if isinstance(resultado['details'], dict) and 'message' in resultado['details']:
                print(f"Detalles: {resultado['details']['message']}")
            else:
                print(f"Detalles: {resultado['details']}")
    else:
        print(f"Repositorio creado con éxito: {resultado.get('html_url', '')}")

def listar_repositorios():
    print("Obteniendo tus repositorios...")
    repos = repo_manager.list_repositories()
    
    if isinstance(repos, dict) and 'error' in repos:
        print(f"Error: {repos['error']}")
        return
    
    if not repos:
        print("No se encontraron repositorios.")
        return
    
    print("\n=== TUS REPOSITORIOS ===")
    for i, repo in enumerate(repos, 1):
        privado = "Privado" if repo.get('private', False) else "Público"
        print(f"{i}. {repo.get('name')} [{privado}]")
        if repo.get('description'):
            print(f"   Descripción: {repo.get('description')}")
        print(f"   URL: {repo.get('html_url')}")
        print()

def actualizar_repositorio():
    try:
        owner = input("Propietario del repositorio: ")
        repo_name = input("Nombre actual del repositorio: ")
        
        print("\nDeja en blanco los campos que no quieras modificar:")
        new_name = input("Nuevo nombre (o Enter para mantener): ")
        if not new_name:
            new_name = None
        
        descripcion = input("Nueva descripción (o Enter para mantener): ")
        if not descripcion and descripcion != "":
            descripcion = None
        
        privado_input = input("¿Cambiar a privado? (s/n/Enter para mantener): ").lower()
        if privado_input == 's':
            privado = True
        elif privado_input == 'n':
            privado = False
        else:
            privado = None
    except KeyboardInterrupt:
        print("\nOperación cancelada")
        return
    
    print("Actualizando repositorio...")
    resultado = repo_manager.update_repository(
        owner,
        repo_name,
        new_name=new_name,
        description=descripcion,
        private=privado
    )
    
    if 'error' in resultado:
        print(f"Error: {resultado['error']}")
        if 'details' in resultado:
            if isinstance(resultado['details'], dict) and 'message' in resultado['details']:
                print(f"Detalles: {resultado['details']['message']}")
            else:
                print(f"Detalles: {resultado['details']}")
    else:
        print(f"Repositorio actualizado con éxito: {resultado.get('html_url', '')}")

def eliminar_repositorio():
    try:
        print("\n¡ADVERTENCIA! Esta operación es irreversible")
        owner = input("Propietario del repositorio a eliminar: ")
        repo_name = input("Nombre del repositorio a eliminar: ")
        
        # Confirmación adicional
        confirmacion = input(f"Para confirmar la eliminación, escribe exactamente: {owner}/{repo_name}: ")
        
        if confirmacion != f"{owner}/{repo_name}":
            print("Confirmación incorrecta. Operación cancelada.")
            return
    except KeyboardInterrupt:
        print("\nOperación cancelada")
        return
    
    print(f"Eliminando repositorio {owner}/{repo_name}...")
    resultado = repo_manager.delete_repository(owner, repo_name)
    
    if 'error' in resultado:
        print(f"Error: {resultado['error']}")
        if 'details' in resultado:
            if isinstance(resultado['details'], dict) and 'message' in resultado['details']:
                print(f"Detalles: {resultado['details']['message']}")
            else:
                print(f"Detalles: {resultado['details']}")
    else:
        print("Repositorio eliminado con éxito.")

def listar_repos_usuario():
    try:
        username = input("Nombre de usuario: ")
    except KeyboardInterrupt:
        print("\nOperación cancelada")
        return
    
    print(f"Obteniendo repositorios de {username}...")
    repos = repo_manager.list_repositories(username)
    
    if isinstance(repos, dict) and 'error' in repos:
        print(f"Error: {repos['error']}")
        return
    
    if not repos:
        print("No se encontraron repositorios.")
        return
    
    print(f"\n=== REPOSITORIOS DE {username.upper()} ===")
    for i, repo in enumerate(repos, 1):
        privado = "Privado" if repo.get('private', False) else "Público"
        print(f"{i}. {repo.get('name')} [{privado}]")
        if repo.get('description'):
            print(f"   Descripción: {repo.get('description')}")
        print(f"   URL: {repo.get('html_url')}")
        lenguaje = repo.get('language', 'No especificado')
        print(f"   Lenguaje principal: {lenguaje}")
        print()

def subir_archivos_a_repo():
    try:
        owner = input("Propietario del repositorio: ")
        repo_name = input("Nombre del repositorio: ")
        
        # Preguntar si usar la carpeta por defecto o especificar otra
        usar_carpeta_default = input(f"¿Usar carpeta '{CARPETA_PROYECTO}'? (s/n): ").lower() == 's'
        
        if usar_carpeta_default:
            directorio = CARPETA_PROYECTO
        else:
            directorio = input("Directorio local con los archivos a subir: ")
    except KeyboardInterrupt:
        print("\nOperación cancelada")
        return
    
    print(f"Subiendo archivos desde '{directorio}' a {owner}/{repo_name}...")
    subir_archivos(owner, repo_name, directorio)

def crear_repo_y_subir_auto():
    try:
        nombre = input("Nombre del repositorio: ")
        descripcion = input("Descripción (opcional, presiona Enter para omitir): ")
        if not descripcion:
            descripcion = None
        
        privado = input("¿Repositorio privado? (s/n): ").lower() == 's'
        inicializar = input("¿Inicializar con README? (s/n): ").lower() == 's'
    except KeyboardInterrupt:
        print("\nOperación cancelada")
        return
    
    # Verificar si la carpeta proyecto existe
    try:
        os.stat(CARPETA_PROYECTO)
    except:
        print(f"Error: La carpeta '{CARPETA_PROYECTO}' no existe.")
        return
    
    print("Creando repositorio...")
    resultado = repo_manager.create_repository(
        nombre, 
        description=descripcion,
        private=privado,
        auto_init=inicializar
    )
    
    if 'error' in resultado:
        print(f"Error: {resultado['error']}")
        if 'details' in resultado:
            if isinstance(resultado['details'], dict) and 'message' in resultado['details']:
                print(f"Detalles: {resultado['details']['message']}")
            else:
                print(f"Detalles: {resultado['details']}")
        return
    
    print(f"Repositorio creado con éxito: {resultado.get('html_url', '')}")
    
    # Esperar un momento para asegurar que el repositorio esté listo
    print("Esperando a que el repositorio esté listo...")
    time.sleep(2)
    
    # Obtener el nombre de usuario del dueño del token
    owner = resultado.get('owner', {}).get('login', '')
    if not owner:
        print("No se pudo determinar el propietario del repositorio.")
        return
    
    # Subir los archivos de la carpeta proyecto
    print(f"Subiendo archivos desde '{CARPETA_PROYECTO}' al nuevo repositorio...")
    subir_archivos(owner, nombre, CARPETA_PROYECTO)

def descargar_archivo():
    """Descarga un archivo de un repositorio"""
    try:
        owner = input("Propietario del repositorio: ")
        repo_name = input("Nombre del repositorio: ")
        remote_path = input("Ruta del archivo en el repositorio: ")
        local_path = input("Ruta local donde guardar (o Enter para usar el mismo nombre): ")
        
        if not local_path:
            local_path = None
    except KeyboardInterrupt:
        print("\nOperación cancelada")
        return
    
    print(f"Descargando {remote_path} desde {owner}/{repo_name}...")
    resultado = repo_manager.download_file(owner, repo_name, remote_path, local_path)
    
    if resultado is True:
        print("Archivo descargado correctamente")
    else:
        print(f"Error al descargar archivo: {resultado.get('error', 'Error desconocido')}")
        if 'details' in resultado:
            if isinstance(resultado['details'], dict) and 'message' in resultado['details']:
                print(f"Detalles: {resultado['details']['message']}")
            else:
                print(f"Detalles: {resultado['details']}")

def crear_carpeta():
    """Crea una carpeta en el repositorio"""
    try:
        owner = input("Propietario del repositorio: ")
        repo_name = input("Nombre del repositorio: ")
        folder_path = input("Ruta de la carpeta a crear: ")
        
        # Eliminar barras iniciales y finales si existen
        folder_path = folder_path.strip('/')
        
        # Asegurarse de que la ruta tenga formato adecuado
        if not folder_path:
            print("Error: La ruta de la carpeta no puede estar vacía.")
            return
    except KeyboardInterrupt:
        print("\nOperación cancelada")
        return
    
    print(f"Creando carpeta '{folder_path}' en {owner}/{repo_name}...")
    resultado = repo_manager.create_folder(owner, repo_name, folder_path)
    
    if 'error' in resultado:
        print(f"Error: {resultado['error']}")
        if 'details' in resultado:
            if isinstance(resultado['details'], dict) and 'message' in resultado['details']:
                print(f"Detalles: {resultado['details']['message']}")
            else:
                print(f"Detalles: {resultado['details']}")
    else:
        print(f"Carpeta creada con éxito: {folder_path}")

# Bucle principal
def main():
    try:
        # Verificar si la carpeta proyecto existe
        try:
            os.stat(CARPETA_PROYECTO)
            print(f"Carpeta de proyecto '{CARPETA_PROYECTO}' encontrada.")
        except:
            print(f"Advertencia: La carpeta '{CARPETA_PROYECTO}' no existe o no es accesible.")
        
        while True:
            opcion = mostrar_menu()
            
            if opcion == "1":
                crear_repositorio()
            elif opcion == "2":
                listar_repositorios()
            elif opcion == "3":
                actualizar_repositorio()
            elif opcion == "4":
                eliminar_repositorio()
            elif opcion == "5":
                listar_repos_usuario()
            elif opcion == "6":
                subir_archivos_a_repo()
            elif opcion == "7":
                crear_repo_y_subir_auto()
            elif opcion == "8":
                descargar_archivo()
            elif opcion == "9":
                crear_carpeta()
            elif opcion == "0":
                print("Saliendo del programa...")
                break
            else:
                print("Opción no válida, intenta de nuevo.")
            
            # Pequeña pausa antes de mostrar el menú de nuevo
            time.sleep(1)
            
            # Liberar memoria después de cada operación
            gc.collect()
    except KeyboardInterrupt:
        print("\nPrograma interrumpido.")
    except Exception as e:
        print(f"\nError inesperado: {e}")
        import sys
        sys.print_exception(e)  # Muestra el traceback completo
    finally:
        print("Finalizando programa.")

# Necesario para que funcione la subida de archivos
import urequests

# Ejecutar el programa
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error fatal: {e}")
        import sys
        sys.print_exception(e)
    finally:
        print("Programa finalizado")