from flask import Flask, render_template, request, redirect, url_for
from supabase import create_client

# Configuración de Supabase
url = "https://fggoijrprvtpjqnsmmyc.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZnZ29panJwcnZ0cGpxbnNtbXljIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDY5Nzg2NDksImV4cCI6MjA2MjU1NDY0OX0.JT9IgkEMuWpwygx88fWVZbirhhRtlVFoZy4faKjx6yk"  # tu key aquí
supabase = create_client(url, key)

app = Flask(__name__)

# RUTA PRINCIPAL - LISTAR
@app.route("/")
def index():
    res = supabase.table("inventario").select("*").execute()
    productos = res.data
    return render_template("index.html", productos=productos)

# RUTA AGREGAR
@app.route("/agregar", methods=["GET", "POST"])
def agregar():
    if request.method == "POST":
        nombre = request.form["nombre"]
        cantidad = int(request.form["cantidad"])
        categoria = request.form["categoria"]
        supabase.table("inventario").insert({
            "nombre": nombre,
            "cantidad": cantidad,
            "categoria": categoria
        }).execute()
        return redirect(url_for("index"))
    return render_template("agregar.html")

# RUTA EDITAR
@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    if request.method == "POST":
        cantidad = int(request.form["cantidad"])
        supabase.table("inventario").update({"cantidad": cantidad}).eq("id", id).execute()
        return redirect(url_for("index"))
    producto = supabase.table("inventario").select("*").eq("id", id).execute().data[0]
    return render_template("editar.html", producto=producto)

# RUTA ELIMINAR
@app.route("/eliminar/<int:id>")
def eliminar(id):
    supabase.table("inventario").delete().eq("id", id).execute()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
