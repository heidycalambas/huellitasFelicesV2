import os
import sys
import importlib.util

backend_dir = os.path.join(os.path.dirname(__file__), "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
os.chdir(backend_dir)

spec = importlib.util.spec_from_file_location("backend_app", os.path.join(backend_dir, "app.py"))
backend_module = importlib.util.module_from_spec(spec)
sys.modules["backend_app"] = backend_module
spec.loader.exec_module(backend_module)

app = backend_module.app
Config = backend_module.Config

if __name__ == "__main__":
    port = Config.SERVER_PORT
    print("==================================================")
    print("  HUELLITAS FELICES — BACKEND (FLASK)")
    print("==================================================")
    print(f"  Servidor corriendo en: http://localhost:{port}")
    print(f"  Microservicio Mascotas: http://localhost:{port}/api/mascotas")
    print(f"  Microservicio Adopciones: http://localhost:{port}/api/adopciones")
    print(f"  Microservicio Veterinario: http://localhost:{port}/api/seguimiento")
    print("==================================================")
    app.run(
        host=Config.SERVER_HOST,
        port=port,
        debug=True,
    )
