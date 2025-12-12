import sys
import os

# Agregamos el directorio actual al path
sys.path.append(os.getcwd())

# Importamos los modelos y las funciones de los endpoints directamente
from app.models.ode_requests import ODEBaseRequest, AnalyticRequest, ErrorAnalysisRequest
from app.api.v1.routes_euler import solve_euler
from app.api.v1.routes_rk4 import solve_rk4
from app.api.v1.routes_analytic import solve_analytic
from app.api.v1.routes_errors import solve_all

def run_test(name, func, request_model, payload):
    print(f"\n--- Probando {name} ---")
    print(f"Payload: {payload}")
    
    try:
        # Creamos el objeto request validado por Pydantic
        req = request_model(**payload)
        
        # Llamamos a la función del endpoint directamente
        response = func(req)
        
        # Pydantic models se pueden convertir a dict para visualización
        data = response.dict()
        
        if "grid" in data:
            print(f"Grid size: {len(data['grid'])}")
            print(f"First 3 t: {data['grid'][:3]} ...")
        if "euler" in data:
            print(f"First 3 Euler y: {data['euler'][:3]} ...")
        if "rk4" in data:
            print(f"First 3 RK4 y: {data['rk4'][:3]} ...")
        if "exact" in data and data['exact']:
            print(f"First 3 Exact y: {data['exact'][:3]} ...")
        if "error_metrics" in data:
            print(f"Error Metrics: {data['error_metrics']}")
            
        print("✅ PRUEBA EXITOSA")
        
    except Exception as e:
        print(f"❌ FALLÓ: {e}")

def run_tests():
    print("INICIANDO DEBUGGING (Llamadas directas)...")

    # Payload común
    payload_exp = {
        "f": "y",
        "t0": 0.0,
        "y0": 1.0,
        "T": 1.0,
        "h": 0.1
    }

    # 1. Euler
    run_test("Euler (Exp)", solve_euler, ODEBaseRequest, payload_exp)

    # 2. RK4
    run_test("RK4 (Exp)", solve_rk4, ODEBaseRequest, payload_exp)

    # 3. Analítico
    run_test("Analítico (Exp)", solve_analytic, AnalyticRequest, payload_exp)

    # 4. Comparación (Stiff suave)
    payload_stiff = {
        "f": "-15*y",
        "t0": 0.0,
        "y0": 1.0,
        "T": 0.5,
        "h": 0.01
    }
    run_test("Comparación (Stiff)", solve_all, ErrorAnalysisRequest, payload_stiff)

    # 5. Validación (Simulada)
    # Al instanciar ODEBaseRequest Pydantic lanzará error si los tipos están mal, 
    # pero si el error es de lógica en 'solve_euler' (ej: parseo), lo atraparemos.
    payload_bad_func = {
        "f": "x + y",  # x no permitido
        "t0": 0.0, "y0": 1.0, "T": 1.0, "h": 0.1
    }
    print(f"\n--- Probando Validación (Debe fallar) ---")
    try:
        req = ODEBaseRequest(**payload_bad_func)
        # Esto debería fallar dentro de la función por el parser
        solve_euler(req)
        print("❌ FALLÓ: Debió lanzar excepción HTTPException o ValueError")
    except Exception as e:
        print(f"✅ PRUEBA EXITOSA (Capturó error esperado): {e}")

    print("\nDEBUGGING FINALIZADO.")

if __name__ == "__main__":
    run_tests()
