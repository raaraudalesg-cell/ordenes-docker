import os
from datetime import datetime
from decimal import Decimal, InvalidOperation

import pymssql
from flask import Flask, jsonify, request

app = Flask(__name__)

ESTADOS = ("Pendiente", "Pagada", "Anulada")


def conectar():
    return pymssql.connect(
        server=os.getenv("DB_HOST", "db"),
        user=os.getenv("DB_USER", "sa"),
        password=os.environ["MSSQL_SA_PASSWORD"],
        database=os.getenv("DB_NAME", "OrdenesDB"),
        port=int(os.getenv("DB_PORT", "1433")),
        as_dict=True,
        login_timeout=10,
        timeout=15
    )


def convertir(fila):
    resultado = {}

    for clave, valor in fila.items():
        if isinstance(valor, Decimal):
            resultado[clave] = float(valor)
        elif isinstance(valor, datetime):
            resultado[clave] = valor.isoformat()
        else:
            resultado[clave] = valor

    return resultado


def error(mensaje, codigo=400):
    return jsonify({"error": mensaje}), codigo


def validar_detalle(datos):
    if not isinstance(datos, dict):
        raise ValueError("Se requiere un objeto JSON")

    producto = datos.get("producto")
    cantidad = datos.get("cantidad")
    precio = datos.get("precio_unitario")

    if not isinstance(producto, str) or not producto.strip():
        raise ValueError("El producto es obligatorio")

    if len(producto.strip()) > 150:
        raise ValueError("El producto supera 150 caracteres")

    if type(cantidad) is not int or cantidad <= 0:
        raise ValueError("La cantidad debe ser un entero positivo")

    if isinstance(precio, bool) or precio is None:
        raise ValueError("El precio unitario es inválido")

    try:
        precio = Decimal(str(precio))
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError("El precio unitario es inválido")

    if not precio.is_finite() or precio < 0:
        raise ValueError("El precio unitario debe ser positivo o cero")

    if precio.as_tuple().exponent < -2:
        raise ValueError("El precio admite máximo dos decimales")

    subtotal = precio * cantidad

    if subtotal > Decimal("9999999999.99"):
        raise ValueError("El subtotal supera el límite permitido")

    return producto.strip(), cantidad, precio, subtotal


def recalcular(cursor, orden_id):
    cursor.execute(
        """
        UPDATE dbo.ordenes
        SET total = (
            SELECT COALESCE(SUM(subtotal), 0)
            FROM dbo.orden_detalle
            WHERE orden_id = %s
        )
        WHERE id = %s
        """,
        (orden_id, orden_id)
    )


def obtener_orden(cursor, orden_id):
    cursor.execute(
        "SELECT * FROM dbo.ordenes WHERE id = %s",
        (orden_id,)
    )

    orden = cursor.fetchone()

    if orden is None:
        return None

    cursor.execute(
        """
        SELECT * FROM dbo.orden_detalle
        WHERE orden_id = %s
        ORDER BY id
        """,
        (orden_id,)
    )

    orden = convertir(orden)

    orden["detalles"] = [
        convertir(fila) for fila in cursor.fetchall()
    ]

    return orden


@app.get("/health")
def health():
    conexion = None
    cursor = None

    try:
        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("SELECT 1 AS resultado")
        resultado = cursor.fetchone()

        if resultado is None or resultado["resultado"] != 1:
            return jsonify({
                "status": "unhealthy",
                "database": "disconnected"
            }), 503

        return jsonify({
            "status": "healthy",
            "database": "connected"
        }), 200

    except Exception as e:
        app.logger.error("Healthcheck fallido: %s", e)

        return jsonify({
            "status": "unhealthy",
            "database": "disconnected",
            "error": "Base de datos no disponible"
        }), 503

    finally:
        if cursor is not None:
            cursor.close()

        if conexion is not None:
            conexion.close()


@app.get("/api/ordenes")
def listar_ordenes():
    with conectar() as conexion:
        cursor = conexion.cursor()

        cursor.execute(
            "SELECT * FROM dbo.ordenes ORDER BY id"
        )

        ordenes = [
            convertir(fila) for fila in cursor.fetchall()
        ]

        return jsonify(ordenes), 200


@app.get("/api/ordenes/<int:orden_id>")
def consultar_orden(orden_id):
    with conectar() as conexion:
        cursor = conexion.cursor()

        orden = obtener_orden(cursor, orden_id)

        if orden is None:
            return error("Orden no encontrada", 404)

        return jsonify(orden), 200


@app.post("/api/ordenes")
def crear_orden():
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return error("Se requiere un objeto JSON")

    cliente = datos.get("cliente")
    estado = datos.get("estado", "Pendiente")

    if not isinstance(cliente, str) or not cliente.strip():
        return error("El cliente es obligatorio")

    if len(cliente.strip()) > 150:
        return error("El cliente supera 150 caracteres")

    if estado not in ESTADOS:
        return error("Estado inválido")

    with conectar() as conexion:
        cursor = conexion.cursor()

        cursor.execute(
            """
            INSERT INTO dbo.ordenes (cliente, estado)
            OUTPUT INSERTED.id
            VALUES (%s, %s)
            """,
            (cliente.strip(), estado)
        )

        orden_id = cursor.fetchone()["id"]

        conexion.commit()

        orden = obtener_orden(cursor, orden_id)

        return jsonify(orden), 201


@app.put("/api/ordenes/<int:orden_id>")
def actualizar_orden(orden_id):
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return error("Se requiere un objeto JSON")

    with conectar() as conexion:
        cursor = conexion.cursor()

        orden = obtener_orden(cursor, orden_id)

        if orden is None:
            return error("Orden no encontrada", 404)

        cliente = datos.get("cliente", orden["cliente"])
        estado = datos.get("estado", orden["estado"])

        if not isinstance(cliente, str) or not cliente.strip():
            return error("El cliente es obligatorio")

        if len(cliente.strip()) > 150:
            return error("El cliente supera 150 caracteres")

        if estado not in ESTADOS:
            return error("Estado inválido")

        cursor.execute(
            """
            UPDATE dbo.ordenes
            SET cliente = %s, estado = %s
            WHERE id = %s
            """,
            (cliente.strip(), estado, orden_id)
        )

        conexion.commit()

        orden = obtener_orden(cursor, orden_id)

        return jsonify(orden), 200


@app.delete("/api/ordenes/<int:orden_id>")
def eliminar_orden(orden_id):
    with conectar() as conexion:
        cursor = conexion.cursor()

        cursor.execute(
            "SELECT id FROM dbo.ordenes WHERE id = %s",
            (orden_id,)
        )

        if cursor.fetchone() is None:
            return error("Orden no encontrada", 404)

        cursor.execute(
            "DELETE FROM dbo.orden_detalle WHERE orden_id = %s",
            (orden_id,)
        )

        cursor.execute(
            "DELETE FROM dbo.ordenes WHERE id = %s",
            (orden_id,)
        )

        conexion.commit()

        return jsonify({
            "mensaje": "Orden eliminada correctamente"
        }), 200


@app.get("/api/ordenes/<int:orden_id>/detalles")
def listar_detalles(orden_id):
    with conectar() as conexion:
        cursor = conexion.cursor()

        cursor.execute(
            "SELECT id FROM dbo.ordenes WHERE id = %s",
            (orden_id,)
        )

        if cursor.fetchone() is None:
            return error("Orden no encontrada", 404)

        cursor.execute(
            """
            SELECT * FROM dbo.orden_detalle
            WHERE orden_id = %s
            ORDER BY id
            """,
            (orden_id,)
        )

        detalles = [
            convertir(fila) for fila in cursor.fetchall()
        ]

        return jsonify(detalles), 200


@app.post("/api/ordenes/<int:orden_id>/detalles")
def agregar_detalle(orden_id):
    datos = request.get_json(silent=True)

    try:
        producto, cantidad, precio, subtotal = validar_detalle(datos)
    except ValueError as e:
        return error(str(e))

    with conectar() as conexion:
        cursor = conexion.cursor()

        cursor.execute(
            "SELECT id FROM dbo.ordenes WHERE id = %s",
            (orden_id,)
        )

        if cursor.fetchone() is None:
            return error("Orden no encontrada", 404)

        cursor.execute(
            """
            INSERT INTO dbo.orden_detalle
            (orden_id, producto, cantidad, precio_unitario, subtotal)
            OUTPUT INSERTED.id
            VALUES (%s, %s, %s, %s, %s)
            """,
            (orden_id, producto, cantidad, precio, subtotal)
        )

        detalle_id = cursor.fetchone()["id"]

        recalcular(cursor, orden_id)

        conexion.commit()

        cursor.execute(
            "SELECT * FROM dbo.orden_detalle WHERE id = %s",
            (detalle_id,)
        )

        detalle = convertir(cursor.fetchone())

        return jsonify(detalle), 201


@app.put("/api/detalles/<int:detalle_id>")
def actualizar_detalle(detalle_id):
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return error("Se requiere un objeto JSON")

    with conectar() as conexion:
        cursor = conexion.cursor()

        cursor.execute(
            "SELECT * FROM dbo.orden_detalle WHERE id = %s",
            (detalle_id,)
        )

        detalle = cursor.fetchone()

        if detalle is None:
            return error("Detalle no encontrado", 404)

        nuevos_datos = {
            "producto": datos.get(
                "producto",
                detalle["producto"]
            ),
            "cantidad": datos.get(
                "cantidad",
                detalle["cantidad"]
            ),
            "precio_unitario": datos.get(
                "precio_unitario",
                detalle["precio_unitario"]
            )
        }

        try:
            producto, cantidad, precio, subtotal = validar_detalle(
                nuevos_datos
            )
        except ValueError as e:
            return error(str(e))

        cursor.execute(
            """
            UPDATE dbo.orden_detalle
            SET producto = %s,
                cantidad = %s,
                precio_unitario = %s,
                subtotal = %s
            WHERE id = %s
            """,
            (producto, cantidad, precio, subtotal, detalle_id)
        )

        recalcular(cursor, detalle["orden_id"])

        conexion.commit()

        cursor.execute(
            "SELECT * FROM dbo.orden_detalle WHERE id = %s",
            (detalle_id,)
        )

        detalle = convertir(cursor.fetchone())

        return jsonify(detalle), 200


@app.delete("/api/detalles/<int:detalle_id>")
def eliminar_detalle(detalle_id):
    with conectar() as conexion:
        cursor = conexion.cursor()

        cursor.execute(
            "SELECT orden_id FROM dbo.orden_detalle WHERE id = %s",
            (detalle_id,)
        )

        detalle = cursor.fetchone()

        if detalle is None:
            return error("Detalle no encontrado", 404)

        orden_id = detalle["orden_id"]

        cursor.execute(
            "DELETE FROM dbo.orden_detalle WHERE id = %s",
            (detalle_id,)
        )

        recalcular(cursor, orden_id)

        conexion.commit()

        return jsonify({
            "mensaje": "Detalle eliminado correctamente"
        }), 200


@app.errorhandler(404)
def ruta_no_encontrada(e):
    return error("Ruta no encontrada", 404)


@app.errorhandler(405)
def metodo_no_permitido(e):
    return error("Método HTTP no permitido", 405)


@app.errorhandler(500)
def error_interno(e):
    app.logger.error("Error interno: %s", e)

    return error("Error interno del servidor", 500)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
