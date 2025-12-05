def euler_solve(f, x0: float, y0: float, h: float, x_end: float):
    if h <= 0:
        raise ValueError("El paso h debe ser > 0")

    n_steps_real = (x_end - x0) / h
    n_steps = int(round(n_steps_real))

    if n_steps <= 0:
        raise ValueError("x_end debe ser mayor que x0 y consistente con h")

    xs = [x0]
    ys = [y0]
    x = x0
    y = y0

    for k in range(n_steps):
        y = y + h * f(x, y)
        x = x0 + (k + 1) * h
        xs.append(x)
        ys.append(y)

    return xs, ys
