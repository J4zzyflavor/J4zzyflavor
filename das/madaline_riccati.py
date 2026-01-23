import numpy as np

# ============================================================
# MADALINE-based solver for generalized Riccati equation
# Shafiee & Amani (2005)
# Final version with multi-direction training
# ============================================================


def madaline_riccati(E, A, B, Q, R,
                     eta=5e-6,
                     max_iter=150000,
                     tol=1e-6):

    n = E.shape[0]

    # Initial symmetric P
    P = np.eye(n)

    R_inv = np.linalg.inv(R)
    S = B @ R_inv @ B.T

    # Use canonical basis vectors (IMPORTANT FIX)
    U = np.eye(n)

    for k in range(max_iter):

        total_grad = np.zeros_like(P)
        total_err = 0.0

        for i in range(n):
            u = U[:, i:i+1]

            # Error vector e(t) — Eq. (28)
            e = (
                 E.T @ P @ A @ u
                + A.T @ P @ E @ u
                + Q @ u
                - E.T @ P @ S @ P @ E @ u
            )

            # Gradient — Eq. (33), symmetrized
            grad = (
                E @ e @ u.T @ A.T
                + A @ u @ e.T @ E.T
                + A @ e @ u.T @ E.T
                + E @ u @ e.T @ A.T
                - E @ e @ u.T @ E.T @ P @ S
                - S @ P @ E @ u @ e.T @ E.T
            )

            grad = 0.5 * (grad + grad.T)

            total_grad += grad
            total_err += np.linalg.norm(e)

        # Update rule
        P = P - eta * (total_grad / n)
        P = 0.5 * (P + P.T)

        # Convergence check
        if total_err / n < tol:
            print(f"Обучение сошлось за {k} итераций")
            break

    return P


def check_solution(E, A, B, Q, R, P):

    R_inv = np.linalg.inv(R)

    residual = (
        E.T @ P @ A
        + A.T @ P @ E
        + Q
        - E.T @ P @ B @ R_inv @ B.T @ P @ E
    )

    sym_err = np.linalg.norm(P - P.T)
    res_err = np.linalg.norm(residual)

    print("\nПроверка решения:")
    if sym_err < 1e-6 and res_err < 2e-2:
        print("✅ ВСЕ ОК: решение Риккати найдено")
    else:
        print("❌ НЕ СОШЛОСЬ")

    print(f"Симметрия P: {sym_err:.2e}")
    print(f"Остаток Riccati: {res_err:.2e}")


# ============================================================
# DATA FROM PAPER — Example 1 (Shafiee & Amani, 2005)
# ============================================================

if __name__ == "__main__":

    E = np.array([
        [0., 0.],
        [1., 0.]
    ])

    A = np.array([
        [0.,  2.],
        [-1., -1.]
    ])

    B = np.array([
        [1.],
        [0.]
    ])

    Q = np.array([
        [1., 0.],
        [0., 0.]
    ])

    R = np.array([[1.]])

    # Solve Riccati equation
    P = madaline_riccati(E, A, B, Q, R)

    print("\nНайденная матрица P:")
    print(P)

    # Acceptance check
    check_solution(E, A, B, Q, R, P)
