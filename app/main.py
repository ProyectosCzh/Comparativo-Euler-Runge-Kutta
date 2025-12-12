# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.routes_euler import router as euler_router
from app.api.v1.routes_rk4 import router as rk4_router
from app.api.v1.routes_analytic import router as analytic_router
from app.api.v1.routes_errors import router as errors_router


app = FastAPI(
    title="ODE Solver API",
    description=(
        "API para resolver ecuaciones diferenciales de primer orden "
        "mediante solución analítica, método de Euler y Runge-Kutta RK4."
    ),
    version="1.0.0",
)

# CORS configuration for React+Vite frontend
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "*"  # Use only in development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(euler_router, prefix="/api/v1/ode", tags=["Euler"])
app.include_router(rk4_router, prefix="/api/v1/ode", tags=["RK4"])
app.include_router(analytic_router, prefix="/api/v1/ode", tags=["Analítica"])
app.include_router(errors_router, prefix="/api/v1/ode", tags=["Errores / Comparación"])
