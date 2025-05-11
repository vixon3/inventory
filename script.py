from flask import Flask, render_template, request, redirect, url_for
from supabase import create_client

# Configuración de Supabase
url = "https://fggoijrprvtpjqnsmmyc.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZnZ29panJwcnZ0cGpxbnNtbXljIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDY5Nzg2NDksImV4cCI6MjA2MjU1NDY0OX0.JT9IgkEMuWpwygx88fWVZbirhhRtlVFoZy4faKjx6yk"  # clave anon
supabase = create_client(url, key)

app = Flask(__name__)

# RUTA PRINCIPAL - LISTAR
@app.route("/")
def index():
    res = supabase.table("inventory").select("*").execute()
    productos = res.data
    return render_template("index.html", productos=productos)

# RUTA AGREGAR
@app.route("/agregar", methods=["GET", "POST"])
def agregar():
    if request.method == "POST":
        def safe(field):  # helper para campos de texto
            return request.form.get(field) or "N/A"

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
            "sku": safe("sku"),
            "cantidad": request.form.get("cantidad", type=int) or 0,
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

if __name__ == "__main__":
    app.run(debug=True)
