def calcular_promedio(lista):
    if len(lista) == 0:
        return 0
    return sum(lista) / len(lista)


numeros = [10, 20, 30, 40, 50, 1000]

promedio = calcular_promedio(numeros)
print(f"El promedio de los números es: {promedio}")


def calcular_promedio_pares(lista):
    pares = []
    for x in lista:
        if x % 2 == 0:
            pares.append(x)
    if len(pares) == 0:
        return 0
    return sum(pares) / len(pares)


promedio_pares = calcular_promedio_pares(numeros)
print(f"El promedio de los números pares es: {promedio_pares}")
