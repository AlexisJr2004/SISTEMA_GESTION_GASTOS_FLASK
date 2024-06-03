from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import json

app = Flask(__name__)

# Direccion a paginas
@app.route('/')
def index():
    return render_template('index.html', categorias=categorias)


# Lista para almacenar los gastos
gastos = []

# Diccionario para categorías
categorias = {
    'Alimentacion': [],
    'Transporte': [],
    'Entretenimiento': [],
    # Aquí podemos agregar más categorías
}

# Funciones
def actualizar_categorizacion():
    global categorias
    categorias = {
        'Alimentacion': [],
        'Transporte': [],
        'Entretenimiento': [],
    }
    for gasto in gastos:
        categorizacion_gastos(gasto)


def calcular_resumen_gastos_mensuales():
    resumen = {}
    totales = {}

    # Ordenar gastos por fecha
    gastos_ordenados_por_fecha = sorted(gastos, key=lambda x: x['fecha'])

    for gasto in gastos_ordenados_por_fecha:
        date = gasto['fecha']
        month = f"{date.year}-{date.month:02d}"

        if month not in resumen:
            resumen[month] = {}
            totales[month] = 0

        if gasto['categoria'] not in resumen[month]:
            resumen[month][gasto['categoria']] = []

        resumen[month][gasto['categoria']].append((float(gasto['cantidad']), date))  # Añadir gasto y fecha

        totales[month] += float(gasto['cantidad'])  # Agregar al total del mes

    return resumen, totales


def categorizacion_gastos(gasto):
    if gasto['categoria'] in categorias:
        categorias[gasto['categoria']].append(gasto)
    else:
        nueva_categoria = gasto['categoria']

        if nueva_categoria not in categorias:
            categorias[nueva_categoria] = []

        categorias[nueva_categoria].append(gasto)


@app.route('/add_gasto', methods=['POST'])
def add_gasto():
    if request.method == 'POST':

        cantidad = float(request.form['cantidad'])

        # Tomar el valor absoluto de la cantidad
        cantidad = abs(cantidad)

        fecha = request.form['fecha']
        fecha = datetime.strptime(fecha, '%Y-%m-%d')  # Convierte la fecha a datetime
        categoria = request.form['categoria']

        if categoria == 'nueva_categoria':
            nueva_categoria = request.form['nueva_categoria']

            if nueva_categoria not in categorias:
                categorias[nueva_categoria] = []

            expense = {
                'cantidad': cantidad,
                'fecha': fecha,
                'categoria': nueva_categoria
            }
        else:
            if categoria in categorias:
                expense = {
                    'cantidad': cantidad,
                    'fecha': fecha,
                    'categoria': categoria
                }
            else:
                return "Categoría no válida"

        categorizacion_gastos(expense)
        gastos.append(expense)


        return redirect(url_for('agregar_gastos'))


@app.route('/eliminar_gastos', methods=['POST'])
def eliminar_gastos_post():
    global gastos

    if request.method == 'POST':
        gastos_seleccionados_indices = request.form.getlist('gastos')

        # Convierte los índices a números enteros
        gastos_seleccionados_indices = [int(i) for i in gastos_seleccionados_indices]

        # Filtra los gastos para mantener solo los no seleccionados
        gastos = [gasto for i, gasto in enumerate(gastos) if i not in gastos_seleccionados_indices]

        actualizar_categorizacion()

    return redirect(url_for('mostrar_eliminar_gastos'))


@app.route('/agregar_gastos.html')
def agregar_gastos():
    categorias_list = [categoria for categoria in categorias]
    return render_template('agregar_gastos.html', categorias=categorias_list)


@app.route('/categorizacion_gastos.html')
def categorizar_gastos():
    return render_template('categorizacion_gastos.html', categorias=categorias)


@app.route('/resumen_gastos_mensuales.html')
def resumen_gastos_mensuales():
    resumen, totales = calcular_resumen_gastos_mensuales()
    return render_template('resumen_gastos_mensuales.html', resumen=resumen, totales=totales)


@app.route('/eliminar_gastos.html', methods=['GET'])
def mostrar_eliminar_gastos():
    return render_template('eliminar_gastos.html', gastos=gastos)


if __name__ == '__main__':
    app.run(port=8000)
