# github_lib.py
import urequests
import ujson

class GitHubRepoManager:
    """
    Cliente simplificado para gestionar repositorios en GitHub desde MicroPython
    """
    def __init__(self, token):
        """
        Inicializa el cliente de GitHub.
        
        Args:
            token (str): Token de acceso personal de GitHub
        """
        self.token = token
        self.api_base_url = "https://api.github.com"
        self.headers = {
            'Authorization': f'token {token}',
            'Content-Type': 'application/json',
            'User-Agent': 'MicroPython-GitHub-Client',
            'Accept': 'application/vnd.github.v3+json'
        }
    
    def create_repository(self, repo_name, description=None, private=False, auto_init=True):
        """
        Crea un nuevo repositorio en GitHub.
        
        Args:
            repo_name (str): Nombre del repositorio
            description (str, opcional): Descripción del repositorio
            private (bool, opcional): Si el repositorio es privado
            auto_init (bool, opcional): Si inicializar con README
        
        Returns:
            dict: Respuesta de la API de GitHub o información de error
        """
        # Preparar datos para la API - usar diccionario con claves entre comillas
        data = {
            "name": repo_name,
            "private": private,
            "auto_init": auto_init
        }
        if description:
            data["description"] = description

        # Convertir a JSON con ujson
        json_data = ujson.dumps(data)

        # Construimos una copia de las cabeceras y fijamos la longitud
        headers = self.headers.copy()
        headers['Content-Length'] = str(len(json_data))

        url = f"{self.api_base_url}/user/repos"
        try:
            response = urequests.post(
                url,
                headers=headers,
                data=json_data
            )
            
            print(f"Código de respuesta: {response.status_code}")
            
            if response.status_code in (200, 201):
                result = ujson.loads(response.text)
                response.close()
                return result
            else:
                try:
                    error_info = ujson.loads(response.text)
                    response.close()
                    return {
                        'error': f'Error al crear repositorio: {response.status_code}',
                        'details': error_info
                    }
                except:
                    error_text = response.text
                    response.close()
                    return {
                        'error': f'Error al crear repositorio: {response.status_code}',
                        'details': error_text
                    }
                
        except Exception as e:
            print(f"Excepción al crear repositorio: {e}")
            import sys
            sys.print_exception(e)
            return {'error': f'Error en la solicitud: {e}'}
    
    def list_repositories(self, username=None):
        """
        Lista los repositorios del usuario.
        
        Args:
            username (str, opcional): Usuario específico cuyos repositorios se quieren listar
                                     Si es None, lista los repositorios del usuario autenticado
        
        Returns:
            list/dict: Lista de repositorios o información de error
        """
        try:
            if username:
                url = f"{self.api_base_url}/users/{username}/repos"
            else:
                url = f"{self.api_base_url}/user/repos"
            
            print(f"Listando repositorios: {url}")
            
            response = urequests.get(
                url,
                headers=self.headers
            )
            
            if response.status_code == 200:
                repos = ujson.loads(response.text)
                response.close()
                return repos
            else:
                try:
                    error_info = ujson.loads(response.text)
                    response.close()
                    return {
                        'error': f'Error al listar repositorios: {response.status_code}',
                        'details': error_info
                    }
                except:
                    error_text = response.text
                    response.close()
                    return {
                        'error': f'Error al listar repositorios: {response.status_code}',
                        'details': error_text
                    }
                
        except Exception as e:
            print(f"Excepción al listar repositorios: {e}")
            import sys
            sys.print_exception(e)
            return {'error': f'Error en la solicitud: {e}'}
    
    def update_repository(self, owner, repo_name, new_name=None, description=None, private=None):
        """
        Actualiza un repositorio existente.
        
        Args:
            owner (str): Propietario del repositorio
            repo_name (str): Nombre actual del repositorio
            new_name (str, opcional): Nuevo nombre
            description (str, opcional): Nueva descripción
            private (bool, opcional): Cambiar visibilidad
            
        Returns:
            dict: Respuesta de la API de GitHub o información de error
        """
        data = {}
        
        if new_name:
            data["name"] = new_name
        
        if description is not None:
            data["description"] = description
        
        if private is not None:
            data["private"] = private
        
        if not data:
            return {'error': 'No se especificaron cambios'}
        
        try:
            json_data = ujson.dumps(data)
            
            url = f"{self.api_base_url}/repos/{owner}/{repo_name}"
            
            response = urequests.patch(
                url,
                headers=self.headers,
                data=json_data
            )
            
            if response.status_code == 200:
                result = ujson.loads(response.text)
                response.close()
                return result
            else:
                try:
                    error_info = ujson.loads(response.text)
                    response.close()
                    return {
                        'error': f'Error al actualizar repositorio: {response.status_code}',
                        'details': error_info
                    }
                except:
                    error_text = response.text
                    response.close()
                    return {
                        'error': f'Error al actualizar repositorio: {response.status_code}',
                        'details': error_text
                    }
                
        except Exception as e:
            print(f"Excepción al actualizar repositorio: {e}")
            import sys
            sys.print_exception(e)
            return {'error': f'Error en la solicitud: {e}'}
    
    def delete_repository(self, owner, repo_name):
        """
        Elimina un repositorio.
        """
        try:
            url = f"{self.api_base_url}/repos/{owner}/{repo_name}"

            # Copiamos las cabeceras y forzamos Content-Length: 0
            headers = self.headers.copy()
            headers['Content-Length'] = '0'

            response = urequests.delete(
                url,
                headers=headers,
                data=b''  # Mandar data vacío
            )

            if response.status_code == 204:  # No Content = éxito
                response.close()
                return {'success': True, 'message': 'Repositorio eliminado correctamente'}
            else:
                try:
                    error_info = ujson.loads(response.text)
                    response.close()
                    return {
                        'error': f'Error al eliminar repositorio: {response.status_code}',
                        'details': error_info
                    }
                except:
                    error_text = response.text
                    response.close()
                    return {
                        'error': f'Error al eliminar repositorio: {response.status_code}',
                        'details': error_text
                    }

        except Exception as e:
            print(f"Excepción al eliminar repositorio: {e}")
            import sys
            sys.print_exception(e)
            return {'error': f'Error en la solicitud: {e}'}

            
    def get_file_sha(self, owner, repo_name, file_path):
        """
        Obtiene el SHA de un archivo en el repositorio.
        
        Args:
            owner (str): Propietario del repositorio
            repo_name (str): Nombre del repositorio
            file_path (str): Ruta del archivo
            
        Returns:
            str/None: SHA del archivo o None si no existe o hay error
        """
        # Remover barras iniciales si existen
        if file_path.startswith('/'):
            file_path = file_path[1:]
            
        try:
            url = f"{self.api_base_url}/repos/{owner}/{repo_name}/contents/{file_path}"
            
            response = urequests.get(
                url,
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = ujson.loads(response.text)
                sha = data.get('sha')
                response.close()
                return sha
            else:
                # Si el archivo no existe, simplemente retornar None
                response.close()
                return None
                
        except Exception as e:
            print(f"Error al obtener SHA: {e}")
            return None
            
    def upload_file(self, owner, repo_name, file_path, remote_path=None, commit_message=None):
        """
        Sube un archivo al repositorio.
        
        Args:
            owner (str): Propietario del repositorio
            repo_name (str): Nombre del repositorio
            file_path (str): Ruta local del archivo
            remote_path (str, opcional): Ruta remota donde guardar el archivo
            commit_message (str, opcional): Mensaje del commit
            
        Returns:
            dict: Respuesta de la API de GitHub o información de error
        """
        import ubinascii
        
        # Si no se especifica ruta remota, usar el nombre del archivo
        if remote_path is None:
            import os
            # Obtener solo el nombre del archivo sin el path
            if '/' in file_path:
                remote_path = file_path.split('/')[-1]
            else:
                remote_path = file_path
        
        # Remover barras iniciales si existen
        if remote_path.startswith('/'):
            remote_path = remote_path[1:]
            
        # Si no se especifica mensaje, usar uno por defecto
        if commit_message is None:
            commit_message = f"Subir {remote_path} desde MicroPython"
            
        try:
            # Leer el archivo
            with open(file_path, 'rb') as f:
                content = f.read()
                
            # Codificar en base64
            content_base64 = ubinascii.b2a_base64(content).decode('utf-8').strip()
            
            # Verificar si el archivo ya existe para obtener su SHA
            sha = self.get_file_sha(owner, repo_name, remote_path)
            
            # Preparar datos para la API
            data = {
                "message": commit_message,
                "content": content_base64,
                "branch": "main"  # <- Cambiar aquí"branch": "main"
            }
            
            # Si el archivo ya existe, incluir su SHA
            if sha:
                data["sha"] = sha
                
            # Convertir a JSON
            json_data = ujson.dumps(data)
            
            # URL para subir el archivo
            url = f"{self.api_base_url}/repos/{owner}/{repo_name}/contents/{remote_path}"
            
            # Enviar solicitud
            response = urequests.put(
                url,
                headers=self.headers,
                data=json_data
            )
            
            if response.status_code in (200, 201):
                result = ujson.loads(response.text)
                response.close()
                return result
            else:
                try:
                    error_info = ujson.loads(response.text)
                    response.close()
                    return {
                        'error': f'Error al subir archivo: {response.status_code}',
                        'details': error_info
                    }
                except:
                    error_text = response.text
                    response.close()
                    return {
                        'error': f'Error al subir archivo: {response.status_code}',
                        'details': error_text
                    }
                
        except Exception as e:
            print(f"Excepción al subir archivo: {e}")
            import sys
            sys.print_exception(e)
            return {'error': f'Error en la solicitud: {e}'}
    
    def download_file(self, owner, repo_name, remote_path, local_path=None):
        """
        Descarga un archivo del repositorio.
        
        Args:
            owner (str): Propietario del repositorio
            repo_name (str): Nombre del repositorio
            remote_path (str): Ruta del archivo en el repositorio
            local_path (str, opcional): Ruta local donde guardar el archivo
            
        Returns:
            bool/dict: True si éxito, diccionario con error si falla
        """
        # Si no se especifica ruta local, usar el nombre del archivo
        if local_path is None:
            # Obtener solo el nombre del archivo sin el path
            if '/' in remote_path:
                local_path = remote_path.split('/')[-1]
            else:
                local_path = remote_path
                
        # Remover barras iniciales si existen
        if remote_path.startswith('/'):
            remote_path = remote_path[1:]
            
        try:
            # URL para obtener información del archivo
            url = f"{self.api_base_url}/repos/{owner}/{repo_name}/contents/{remote_path}"
            
            # Obtener metadatos del archivo
            response = urequests.get(
                url,
                headers=self.headers
            )
            
            if response.status_code == 200:
                file_info = ujson.loads(response.text)
                response.close()
                
                # Verificar que es un archivo
                if file_info.get('type') != 'file':
                    return {'error': 'El path proporcionado no es un archivo'}
                
                # Obtener la URL de descarga directa
                download_url = file_info.get('download_url')
                
                if not download_url:
                    return {'error': 'No se pudo obtener la URL de descarga'}
                
                # Descargar el contenido del archivo
                download_response = urequests.get(download_url)
                
                if download_response.status_code == 200:
                    # Guardar el archivo localmente
                    with open(local_path, 'wb') as f:
                        f.write(download_response.content)
                        
                    download_response.close()
                    return True
                else:
                    download_response.close()
                    return {'error': f'Error al descargar archivo: {download_response.status_code}'}
            else:
                try:
                    error_info = ujson.loads(response.text)
                    response.close()
                    return {
                        'error': f'Error al obtener información del archivo: {response.status_code}',
                        'details': error_info
                    }
                except:
                    error_text = response.text
                    response.close()
                    return {
                        'error': f'Error al obtener información del archivo: {response.status_code}',
                        'details': error_text
                    }
                
        except Exception as e:
            print(f"Excepción al descargar archivo: {e}")
            import sys
            sys.print_exception(e)
            return {'error': f'Error en la solicitud: {e}'}

    def create_folder(self, owner, repo_name, folder_path, commit_message=None):
        """
        Crea una carpeta en el repositorio (en GitHub, se crea añadiendo un archivo .gitkeep).
        
        Args:
            owner (str): Propietario del repositorio
            repo_name (str): Nombre del repositorio
            folder_path (str): Ruta de la carpeta a crear
            commit_message (str, opcional): Mensaje del commit
            
        Returns:
            dict: Respuesta de la API de GitHub o información de error
        """
        import ubinascii
        
        # Asegurarse de que no haya barra al inicio
        if folder_path.startswith('/'):
            folder_path = folder_path[1:]
            
        # Asegurarse de que haya una barra al final
        if not folder_path.endswith('/'):
            folder_path += '/'
            
        # Añadir archivo .gitkeep para crear la carpeta
        file_path = folder_path + '.gitkeep'
        
        # Si no se especifica mensaje, usar uno por defecto
        if commit_message is None:
            commit_message = f"Crear carpeta {folder_path} desde MicroPython"
            
        try:
            # Preparar datos para la API - contenido vacío para .gitkeep
            data = {
                "message": commit_message,
                "content": ubinascii.b2a_base64(b"").decode('utf-8').strip(),
                "branch": "main"
            }
                
            # Convertir a JSON
            json_data = ujson.dumps(data)
            
            # URL para crear el archivo
            url = f"{self.api_base_url}/repos/{owner}/{repo_name}/contents/{file_path}"
            
            # Enviar solicitud
            response = urequests.put(
                url,
                headers=self.headers,
                data=json_data
            )
            
            if response.status_code in (200, 201):
                result = ujson.loads(response.text)
                response.close()
                return result
            else:
                try:
                    error_info = ujson.loads(response.text)
                    response.close()
                    return {
                        'error': f'Error al crear carpeta: {response.status_code}',
                        'details': error_info
                    }
                except:
                    error_text = response.text
                    response.close()
                    return {
                        'error': f'Error al crear carpeta: {response.status_code}',
                        'details': error_text
                    }
                
        except Exception as e:
            print(f"Excepción al crear carpeta: {e}")
            import sys
            sys.print_exception(e)
            return {'error': f'Error en la solicitud: {e}'}
    
    def get_repository_info(self, owner, repo_name):
        """
        Obtiene información detallada de un repositorio.
        
        Args:
            owner (str): Propietario del repositorio
            repo_name (str): Nombre del repositorio
            
        Returns:
            dict: Información del repositorio o error
        """
        try:
            url = f"{self.api_base_url}/repos/{owner}/{repo_name}"
            
            response = urequests.get(
                url,
                headers=self.headers
            )
            
            if response.status_code == 200:
                result = ujson.loads(response.text)
                response.close()
                return result
            else:
                try:
                    error_info = ujson.loads(response.text)
                    response.close()
                    return {
                        'error': f'Error al obtener información del repositorio: {response.status_code}',
                        'details': error_info
                    }
                except:
                    error_text = response.text
                    response.close()
                    return {
                        'error': f'Error al obtener información del repositorio: {response.status_code}',
                        'details': error_text
                    }
                
        except Exception as e:
            print(f"Excepción al obtener información del repositorio: {e}")
            import sys
            sys.print_exception(e)
            return {'error': f'Error en la solicitud: {e}'}