from flask import Flask, render_template, request, redirect, url_for
from supabase import create_client

# Configuración de Supabase
url = "https://fggoijrprvtpjqnsmmyc.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."  # clave anon
supabase = create_client(url, key)

app = Flask(__name__)

# RUTA PRINCIPAL - LISTAR
@app.route("/")
def index():
    res = supabase.table("tabletas").select("*").execute()
    productos = res.data
    return render_template("index.html", productos=productos)

# RUTA AGREGAR
@app.route("/agregar", methods=["GET", "POST"])
def agregar():
    if request.method == "POST":
        data = {
            "nombre": request.form["nombre"],
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
            "sku": request.form["sku"],
            "cantidad": request.form.get("cantidad", type=int),
        }
        supabase.table("tabletas").insert(data).execute()
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
        supabase.table("tabletas").update(data).eq("id", id).execute()
        return redirect(url_for("index"))
    producto = supabase.table("tabletas").select("*").eq("id", id).execute().data[0]
    return render_template("editar.html", producto=producto)

# RUTA ELIMINAR
@app.route("/eliminar/<int:id>")
def eliminar(id):
    supabase.table("tabletas").delete().eq("id", id).execute()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
