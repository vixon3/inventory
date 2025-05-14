from flask import Flask, render_template, request, redirect, url_for
from supabase import create_client
from io import BytesIO
from datetime import datetime
from dateutil import parser
import os
import barcode
from barcode.writer import ImageWriter

# Configuración de Supabase
url = "https://fggoijrprvtpjqnsmmyc.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZnZ29panJwcnZ0cGpxbnNtbXljIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDY5Nzg2NDksImV4cCI6MjA2MjU1NDY0OX0.JT9IgkEMuWpwygx88fWVZbirhhRtlVFoZy4faKjx6yk"  # clave anon
supabase = create_client(url, key)

app = Flask(__name__)

# RUTA PRINCIPAL - LISTAR
@app.route("/", methods=["GET"])
def index():
    query = request.args.get("q", "").strip().lower()
    orden_precio = request.args.get("orden_precio", "")
    productos = []

    # Cargar todos los productos
    res = supabase.table("inventory").select("*").execute()
    todos = res.data

    # Filtrar por texto (en cualquier campo)
    if query:
        for prod in todos:
            for campo in prod.values():
                if campo and query in str(campo).lower():
                    productos.append(prod)
                    break
    else:
        productos = todos

    # Ordenar por precio si se especifica
    if orden_precio == "desc":
        productos.sort(key=lambda x: x.get("precio", 0), reverse=True)
    else:
        productos.sort(key=lambda x: x.get("precio", 0))

    for item in productos:
        actualizado = item.get("actualizado")
        if actualizado and isinstance(actualizado, str):
            try:
                # Usamos dateutil.parser para parsear cualquier formato ISO8601
                item["actualizado"] = parser.isoparse(actualizado)
            except Exception:
                item["actualizado"] = None

    return render_template("index.html", productos=productos, query=query, orden_precio=orden_precio)

# RUTA AGREGAR
@app.route("/agregar", methods=["GET", "POST"])
def agregar():
    if request.method == "POST":
        def safe(field): return request.form.get(field) or "N/A"

        # Paso 1: obtener SKU y generar código de barras
        sku = safe("sku")
        ean_code = str(sku)  # usaremos el SKU directamente como EAN

        try:
            filename = f"{ean_code}.png"
            filepath = os.path.join("/tmp", filename)  # Render


            # Generar y guardar imagen del código de barras
            ean = barcode.get('ean13', ean_code, writer=ImageWriter())
            ean.save(filepath[:-4])  # quitar .png porque ean.save() lo agrega

            # Subir a Supabase
            with open(filepath, "rb") as f:
                supabase.storage.from_('barcodes').upload(
                    path=filename,
                    file=f,
                    file_options={"content-type": "image/png"}
                )

            # Obtener URL y limpiar
            public_url = supabase.storage.from_('barcodes').get_public_url(filename)
            os.remove(filepath)
        except Exception as e:
            print("⚠️ No se pudo subir a Supabase Storage:", e)
            public_url = ""

        # Paso 2: construir datos del producto
        data = {
            "nombre": safe("nombre"),
            "precio": request.form.get("precio", type=int) or 0,
            "procesador": safe("procesador"),
            "ram": safe("ram"),
            "almacenamiento": safe("almacenamiento"),
            "pantalla": safe("pantalla"),
            "tarjeta_video": safe("tarjeta_video"),
            "sistema_operativo": safe("sistema_operativo"),
            "otros": safe("otros"),
            "meson": safe("meson"),
            "tipo": safe("tipo"),
            "sku": sku,
            "cantidad": request.form.get("cantidad", type=int) or 0,
            "codigo_barras_url": public_url,
            "actualizado": datetime.now().isoformat()

        }

        supabase.table("inventory").insert(data).execute()
        return redirect(url_for("index"))

    return render_template("agregar.html")



# RUTA EDITAR
@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    if request.method == "POST":
        data = {
            "precio": request.form.get("precio", type=int),
            "procesador": request.form["procesador"],
            "ram": request.form["ram"],
            "almacenamiento": request.form["almacenamiento"],
            "pantalla": request.form["pantalla"],
            "tarjeta_video": request.form["tarjeta_video"],
            "sistema_operativo": request.form["sistema_operativo"],
            "otros": request.form["otros"],
            "meson": request.form["meson"],
            "tipo": request.form["tipo"],
            "cantidad": request.form.get("cantidad", type=int),
            "actualizado": datetime.now().isoformat()

        }
        supabase.table("inventory").update(data).eq("id", id).execute()
        return redirect(url_for("index"))
    producto = supabase.table("inventory").select("*").eq("id", id).execute().data[0]
    return render_template("editar.html", producto=producto)

# RUTA ELIMINAR
@app.route("/eliminar/<int:id>")
def eliminar(id):
    supabase.table("inventory").delete().eq("id", id).execute()
    return redirect(url_for("index"))


"""# ✅ AHORA PUEDES USARLA
sku = 2000396937469
codigo_barras = str(sku)  # ya es un EAN-13 válido
ean = barcode.get('ean13', codigo_barras, writer=ImageWriter())
ean.save("codigo_barras")

ean = barcode.get('ean13', codigo_barras, writer=ImageWriter())
ean.save("codigo_barras")"""

if __name__ == "__main__":
    app.run(debug=True)
