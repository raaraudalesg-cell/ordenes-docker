
import requests
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods, require_POST


API_URL = settings.API_URL
TIMEOUT = 10


def solicitar_api(metodo, ruta, datos=None):
    try:
        respuesta = requests.request(
            metodo,
            f"{API_URL}{ruta}",
            json=datos,
            timeout=TIMEOUT
        )

        try:
            contenido = respuesta.json()
        except ValueError:
            contenido = {}

        if not respuesta.ok:
            if isinstance(contenido, dict):
                mensaje = contenido.get(
                    "error",
                    f"Error HTTP {respuesta.status_code}"
                )
            else:
                mensaje = f"Error HTTP {respuesta.status_code}"

            return None, mensaje

        return contenido, None

    except requests.exceptions.Timeout:
        return None, "La API tardó demasiado en responder"

    except requests.exceptions.ConnectionError:
        return None, "No se pudo establecer conexión con la API"

    except requests.exceptions.RequestException as e:
        return None, f"Error de comunicación: {str(e)}"


def validar_orden(request):
    cliente = request.POST.get("cliente", "").strip()
    estado = request.POST.get("estado", "Pendiente")

    if not cliente:
        return None, "El nombre del cliente es obligatorio"

    if len(cliente) > 150:
        return None, "El nombre del cliente es demasiado largo"

    if estado not in ["Pendiente", "Pagada", "Anulada"]:
        return None, "El estado seleccionado no es válido"

    return {
        "cliente": cliente,
        "estado": estado
    }, None


def validar_detalle(request):
    producto = request.POST.get("producto", "").strip()
    cantidad = request.POST.get("cantidad", "").strip()
    precio = request.POST.get("precio_unitario", "").strip()

    if not producto:
        return None, "El nombre del producto es obligatorio"

    if len(producto) > 150:
        return None, "El nombre del producto es demasiado largo"

    try:
        cantidad = int(cantidad)
    except ValueError:
        return None, "La cantidad debe ser un número entero"

    if cantidad <= 0:
        return None, "La cantidad debe ser mayor que cero"

    try:
        precio = Decimal(precio)
    except (InvalidOperation, ValueError):
        return None, "El precio unitario no es válido"

    if not precio.is_finite() or precio < 0:
        return None, "El precio debe ser positivo o cero"

    if precio.as_tuple().exponent < -2:
        return None, "El precio admite máximo dos decimales"

    return {
        "producto": producto,
        "cantidad": cantidad,
        "precio_unitario": float(precio)
    }, None


def lista_ordenes(request):
    ordenes, error = solicitar_api(
        "GET",
        "/api/ordenes"
    )

    if error:
        messages.error(request, error)
        ordenes = []

    return render(
        request,
        "ordenes/lista.html",
        {
            "ordenes": ordenes
        }
    )


def ver_orden(request, orden_id):
    orden, error = solicitar_api(
        "GET",
        f"/api/ordenes/{orden_id}"
    )

    if error:
        messages.error(request, error)
        return redirect("lista_ordenes")

    return render(
        request,
        "ordenes/detalle.html",
        {
            "orden": orden
        }
    )


@require_http_methods(["GET", "POST"])
def crear_orden(request):
    if request.method == "POST":
        datos, error = validar_orden(request)

        if error:
            messages.error(request, error)
        else:
            resultado, error = solicitar_api(
                "POST",
                "/api/ordenes",
                datos
            )

            if error:
                messages.error(request, error)
            else:
                messages.success(
                    request,
                    "Orden creada correctamente"
                )
                return redirect(
                    "ver_orden",
                    orden_id=resultado["id"]
                )

    return render(
        request,
        "ordenes/formulario_orden.html",
        {
            "titulo": "Nueva orden",
            "orden": None
        }
    )


@require_http_methods(["GET", "POST"])
def editar_orden(request, orden_id):
    orden, error = solicitar_api(
        "GET",
        f"/api/ordenes/{orden_id}"
    )

    if error:
        messages.error(request, error)
        return redirect("lista_ordenes")

    if request.method == "POST":
        datos, error = validar_orden(request)

        if error:
            messages.error(request, error)
            orden.update({
                "cliente": request.POST.get("cliente", ""),
                "estado": request.POST.get("estado", "Pendiente")
            })
        else:
            resultado, error = solicitar_api(
                "PUT",
                f"/api/ordenes/{orden_id}",
                datos
            )

            if error:
                messages.error(request, error)
            else:
                messages.success(
                    request,
                    "Orden actualizada correctamente"
                )
                return redirect(
                    "ver_orden",
                    orden_id=orden_id
                )

    return render(
        request,
        "ordenes/formulario_orden.html",
        {
            "titulo": "Editar orden",
            "orden": orden
        }
    )


@require_POST
def eliminar_orden(request, orden_id):
    resultado, error = solicitar_api(
        "DELETE",
        f"/api/ordenes/{orden_id}"
    )

    if error:
        messages.error(request, error)
    else:
        messages.success(
            request,
            "Orden eliminada correctamente"
        )

    return redirect("lista_ordenes")


@require_http_methods(["GET", "POST"])
def agregar_detalle(request, orden_id):
    orden, error = solicitar_api(
        "GET",
        f"/api/ordenes/{orden_id}"
    )

    if error:
        messages.error(request, error)
        return redirect("lista_ordenes")

    if request.method == "POST":
        datos, error = validar_detalle(request)

        if error:
            messages.error(request, error)
        else:
            resultado, error = solicitar_api(
                "POST",
                f"/api/ordenes/{orden_id}/detalles",
                datos
            )

            if error:
                messages.error(request, error)
            else:
                messages.success(
                    request,
                    "Producto agregado correctamente"
                )
                return redirect(
                    "ver_orden",
                    orden_id=orden_id
                )

    return render(
        request,
        "ordenes/formulario_detalle.html",
        {
            "titulo": "Agregar producto",
            "orden": orden,
            "detalle": None
        }
    )


@require_http_methods(["GET", "POST"])
def editar_detalle(request, detalle_id):
    ordenes, error = solicitar_api(
        "GET",
        "/api/ordenes"
    )

    if error:
        messages.error(request, error)
        return redirect("lista_ordenes")

    detalle = None
    orden = None

    for item in ordenes:
        datos_orden, error = solicitar_api(
            "GET",
            f"/api/ordenes/{item['id']}"
        )

        if error:
            continue

        for producto in datos_orden.get("detalles", []):
            if producto["id"] == detalle_id:
                detalle = producto
                orden = datos_orden
                break

        if detalle:
            break

    if detalle is None:
        messages.error(
            request,
            "No se encontró el producto"
        )
        return redirect("lista_ordenes")

    if request.method == "POST":
        datos, error = validar_detalle(request)

        if error:
            messages.error(request, error)
        else:
            resultado, error = solicitar_api(
                "PUT",
                f"/api/detalles/{detalle_id}",
                datos
            )

            if error:
                messages.error(request, error)
            else:
                messages.success(
                    request,
                    "Producto actualizado correctamente"
                )
                return redirect(
                    "ver_orden",
                    orden_id=orden["id"]
                )

    return render(
        request,
        "ordenes/formulario_detalle.html",
        {
            "titulo": "Editar producto",
            "orden": orden,
            "detalle": detalle
        }
    )


@require_POST
def eliminar_detalle(request, detalle_id):
    orden_id = request.POST.get("orden_id")

    try:
        orden_id = int(orden_id)
    except (TypeError, ValueError):
        messages.error(
            request,
            "Identificador de orden inválido"
        )
        return redirect("lista_ordenes")

    resultado, error = solicitar_api(
        "DELETE",
        f"/api/detalles/{detalle_id}"
    )

    if error:
        messages.error(request, error)
    else:
        messages.success(
            request,
            "Producto eliminado correctamente"
        )

    return redirect(
        "ver_orden",
        orden_id=orden_id
    )
