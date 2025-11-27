import numpy as np

def calcular_EAR(pontos_olho):
    # pontos_olho = [p0, p1, p2, p3, p4, p5]
    p = [np.array(pt, dtype=float) for pt in pontos_olho]

    A = np.linalg.norm(p[1] - p[5])
    B = np.linalg.norm(p[2] - p[4])
    C = np.linalg.norm(p[0] - p[3])

    if C == 0:
        return 0

    return (A + B) / (2.0 * C)


def calcular_MAR(pontos_boca):
    # pontos_boca = [superior, inferior, esquerda, direita]
    p = [np.array(pt, dtype=float) for pt in pontos_boca]

    altura = np.linalg.norm(p[0] - p[1])
    largura = np.linalg.norm(p[2] - p[3])

    if largura == 0:
        return 0

    return altura / largura
