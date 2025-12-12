
import sys
import os

# Agregamos el directorio actual al path
sys.path.append(os.getcwd())

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
try:
    from fastapi.testclient import TestClient
    HAS_HTTPX = True
except Exception:
    # Capturamos cualquier error (ImportError, ModuleNotFoundError, RuntimeError)
    # si httpx no está instalado.
    HAS_HTTPX = False

# Importamos la app y funciones
from app.main import app
from app.models.ode_requests import ODEBaseRequest, AnalyticRequest, ErrorAnalysisRequest
from app.api.v1.routes_euler import solve_euler
from app.api.v1.routes_rk4 import solve_rk4
from app.api.v1.routes_analytic import solve_analytic
from app.api.v1.routes_errors import solve_all

def check_cors_static():
    print("\n--- Verificando Configuración CORS (Estático) ---")
    cors_found = False
    # Revisamos los middleware definidos por el usuario
    for mw in app.user_middleware:
        if mw.cls == CORSMiddleware:
            cors_found = True
            print("✅ CORSMiddleware encontrado en la configuración.")
            # print(f"   Opciones detectadas: {mw.options}") # Evitar error de atributo
            break
            
    if cors_found:
        print("✅ La integración de CORS parece correcta.")
    else:
        print("❌ ADVERTENCIA: No se detectó CORSMiddleware en app.user_middleware.")

def check_cors_dynamic():
    if not HAS_HTTPX:
        print("\n⚠️ 'httpx' no está instalado. Saltando prueba dinámica de CORS (TestClient).")
        return

    print("\n--- Verificando Configuración CORS (Dinámico via TestClient) ---")
    client = TestClient(app)
    try:
        # Simulamos una petición preflight OPTIONS desde un origen permitido
        response = client.options(
            "/api/v1/ode/euler",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST"
            }
        )
        print(f"Status OPTIONS: {response.status_code}")
        if "access-control-allow-origin" in response.headers:
            print(f"✅ Header Access-Control-Allow-Origin: {response.headers['access-control-allow-origin']}")
        else:
            print("❌ Falta header Access-Control-Allow-Origin en la respuesta.")
            
    except Exception as e:
        print(f"❌ Error probando CORS dinámicamente: {e}")

def run_logic_tests():
    print("\n--- Verificando Lógica de Endpoints (Llamadas directas) ---")
    
    # Payload común
    payload_exp = {
        "f": "y",
        "t0": 0.0,
        "y0": 1.0,
        "T": 1.0,
        "h": 0.1
    }

    # Helper para correr test
    def _test(name, func, model, data):
        try:
            req = model(**data)
            res = func(req)
            # Si no explota, asumimos éxito básico. Verificamos algo básico
            d = res.dict()
            if "grid" in d:
                print(f"✅ {name}: OK ({len(d['grid'])} puntos)")
        except Exception as e:
            print(f"❌ {name}: FALLÓ ({e})")

    _test("Euler", solve_euler, ODEBaseRequest, payload_exp)
    _test("RK4", solve_rk4, ODEBaseRequest, payload_exp)
    _test("Analítico", solve_analytic, AnalyticRequest, payload_exp)
    
    payload_stiff = {"f": "-15*y", "t0": 0, "y0": 1, "T": 0.5, "h": 0.01}
    _test("Comparación", solve_all, ErrorAnalysisRequest, payload_stiff)

def run_tests():
    print("=== INICIANDO SCRIPT DE COMPROBACIÓN DEL PROYECTO ===")
    
    # 1. Verificar CORS
    check_cors_static()
    check_cors_dynamic()
    
    # 2. Verificar Lógica
    run_logic_tests()
    
    print("\n=== COMPROBACIÓN FINALIZADA ===")

if __name__ == "__main__":
    run_tests()
