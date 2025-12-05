from fastapi import FastAPI

from app.api.endpoints import meta, ode_solver


app = FastAPI(
    title="RK4 vs Euler Solver API",
    description="Motor numérico para EDO de primer orden (Euler y RK4).",
    version="0.1.0",
)


# Registrar routers
app.include_router(meta.router)
app.include_router(ode_solver.router)