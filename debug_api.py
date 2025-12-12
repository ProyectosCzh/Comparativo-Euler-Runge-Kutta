
import sys
import os
import math

# Agregamos el directorio actual al path
sys.path.append(os.getcwd())

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
try:
    from fastapi.testclient import TestClient
    HAS_HTTPX = True
except Exception:
    HAS_HTTPX = False

# Importamos la app y funciones directas (bypass HTTP layer si no hay httpx)
from app.main import app
from app.models.ode_requests import ODEBaseRequest, AnalyticRequest, ErrorAnalysisRequest
from app.api.v1.routes_euler import solve_euler
from app.api.v1.routes_rk4 import solve_rk4
from app.api.v1.routes_analytic import solve_analytic
from app.api.v1.routes_errors import solve_all

# Colores para consola
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"{Colors.HEADER}{Colors.BOLD}\n=== {text} ==={Colors.ENDC}")

def print_ok(text):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_fail(text):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def check_cors_static():
    print_header("Verificando Integración CORS (Configuración)")
    cors_found = False
    for mw in app.user_middleware:
        if mw.cls == CORSMiddleware:
            cors_found = True
            break
            
    if cors_found:
        print_ok("CORSMiddleware detectado en app.user_middleware.")
    else:
        print_fail("ADVERTENCIA: No se detectó CORSMiddleware.")

def run_test_case(name, func, model, payload, check_fn=None):
    print(f"\n{Colors.OKBLUE}Probando Caso: {name}{Colors.ENDC}")
    print(f"  Input: {payload}")
    try:
        req = model(**payload)
        res = func(req)
        data = res.dict()
        
        # Validaciones básicas
        if "grid" in data:
            print(f"  -> Grid generado: {len(data['grid'])} puntos.")
        
        # Validación personalizada del resultado
        if check_fn:
            check_fn(data)
        else:
            print_ok("Ejecución correcta (Sin validación específica de valores).")
            
    except Exception as e:
        print_fail(f"Excepción: {e}")

def val_exponential(data):
    # euler debe ser cercana a e^1 = 2.718
    last_y = data['euler'][-1] if 'euler' in data else (data['rk4'][-1] if 'rk4' in data else None)
    if 'exact' in data and data['exact']:
        last_y = data['exact'][-1]
    
    if last_y is not None:
        print(f"  -> Valor final (y_end): {last_y:.5f}")
        if 2.0 < last_y < 3.0:
            print_ok("Resultado dentro de rango esperado para e^1.")
        else:
            print_fail(f"Resultado sospechoso para e^t en t=1: {last_y}")

def val_stiff(data):
    # Debe decaer a 0
    y_rk4 = data['rk4'][-1]
    print(f"  -> Valor final RK4: {y_rk4:.5e}")
    if abs(y_rk4) < 0.1:
        print_ok("Decaimiento correcto (converge a 0).")
    else:
        print_fail("No convergió a 0 como se esperaba.")

def run_logic_tests():
    print_header("Ejecutando Suite de Pruebas Matemáticas")

    # CASO 1: Exponencial (Euler)
    payload_exp = {"f": "y", "t0": 0.0, "y0": 1.0, "T": 1.0, "h": 0.1}
    run_test_case("Crecimiento Exponencial (Euler)", solve_euler, ODEBaseRequest, payload_exp, val_exponential)

    # CASO 2: Logística (RK4)
    # y' = y*(1-y), y(0)=0.5 -> tiende a 1
    payload_log = {"f": "y*(1-y)", "t0": 0.0, "y0": 0.5, "T": 5.0, "h": 0.5}
    run_test_case("Logística (RK4)", solve_rk4, ODEBaseRequest, payload_log, 
                  lambda d: print_ok(f"Valor final: {d['rk4'][-1]:.4f} (aprox 1.0)") if abs(d['rk4'][-1] - 1.0) < 0.1 else print_fail(f"Lejos de 1.0: {d['rk4'][-1]}"))

    # CASO 3: Trigonométrica (Analítico)
    # y' = cos(t), y(0)=0 -> y=sin(t)
    payload_trig = {"f": "cos(t)", "t0": 0.0, "y0": 0.0, "T": 3.14159, "h": 0.1}
    run_test_case("Trigonométrica (Analítico)", solve_analytic, AnalyticRequest, payload_trig,
                  lambda d: print_ok("Solución exacta encontrada.") if d['exact'] else print_fail("No se halló solución analítica."))

    # CASO 4: Comparación Stiff
    # y' = -15y
    payload_stiff = {"f": "-15*y", "t0": 0.0, "y0": 1.0, "T": 0.5, "h": 0.01}
    run_test_case("Comparación Stiff (Solve All)", solve_all, ErrorAnalysisRequest, payload_stiff, val_stiff)

    # CASO 5: Validación de Errores (Inputs incorrectos)
    print(f"\n{Colors.OKBLUE}Probando Caso: Validación de Input Incorrecto{Colors.ENDC}")
    try:
        # 'z' no existe
        bad_req = ODEBaseRequest(f="z + y", t0=0, y0=0, T=1, h=0.1)
        solve_euler(bad_req)
        print_fail("Debió fallar por variable desconocida 'z'.")
    except Exception as e:
        print_ok(f"Capturó error esperado: {str(e)[:50]}...")

def run_tests():
    # Habilitar colores en Windows 10+ si es posible (os.system('') a veces ayuda a init VT100)
    os.system('') 
    
    print_header("INICIANDO DEBUGGING COMPLETO DEL PROYECTO")
    
    # 1. Configuración
    check_cors_static()
    
    # 2. Lógica Matemática
    run_logic_tests()
    
    print_header("DEBUGGING FINALIZADO")

if __name__ == "__main__":
    run_tests()
