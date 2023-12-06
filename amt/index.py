from datetime import date
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from flask_login import LoginManager, login_user, logout_user, login_required

# Models
from models.ModelUser import ModelUser

# Entities
from models.entities.User import User


# aqui importamos el mysql.conector por que sino no inicia la pagina. sabemos que no es necesario porque en el codigo anterior lo vinculamos con flask, pero de todas maneras no se puede :'(
import mysql.connector

app = Flask(__name__)


# Configuración de la base de datos
conexion = mysql.connector.connect
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""




# Crear objeto MySQL
mysql = MySQL(app)
login_manager_app = LoginManager(app)


@login_manager_app.user_loader
def load_user(id):
    return ModelUser.get_by_id(mysql, id)


# configuraciones
app.secret_key = "mysecretkey"

# Establecer la conexión a la base de datos


@app.route("/")
def principal():
    return render_template("principal.html")



@app.route("/consulta", methods=["GET"])
@login_required
def consulta():
    from_fecha = request.args.get("from_fecha")
    to_fecha = request.args.get("to_fecha")
    nom_comercio = request.args.get("nomComercio")
    estado_turno = request.args.get("estado")

    print("from_fecha:", from_fecha)
    print("to_fecha:", to_fecha)
    print("nom_comercio:", nom_comercio)
    print("estado_turno:", estado_turno)

    cur = mysql.connection.cursor()

    if from_fecha and to_fecha:
        from_fecha = date.fromisoformat(from_fecha)
        to_fecha = date.fromisoformat(to_fecha)

        if nom_comercio:
            if estado_turno:
                cur.execute(
                    "SELECT * FROM calendario WHERE fecha BETWEEN %s AND %s AND nomComercio = %s AND estado = %s ORDER BY fecha DESC",
                    (from_fecha, to_fecha, nom_comercio, estado_turno),
                )
            else:
                cur.execute(
                    "SELECT * FROM calendario WHERE fecha BETWEEN %s AND %s AND nomComercio = %s ORDER BY fecha DESC",
                    (from_fecha, to_fecha, nom_comercio),
                )
        else:
            if estado_turno:
                cur.execute(
                    "SELECT * FROM calendario WHERE fecha BETWEEN %s AND %s AND estado = %s ORDER BY fecha DESC",
                    (from_fecha, to_fecha, estado_turno),
                )
            else:
                cur.execute(
                    "SELECT * FROM calendario WHERE fecha BETWEEN %s AND %s ORDER BY fecha DESC, horario ASC",
                    (from_fecha, to_fecha),
                )
    else:
        if nom_comercio:
            if estado_turno:
                cur.execute(
                    "SELECT * FROM calendario WHERE nomComercio = %s AND estado = %s ORDER BY fecha DESC",
                    (nom_comercio, estado_turno),
                )
            else:
                cur.execute(
                    "SELECT * FROM calendario WHERE nomComercio = %s ORDER BY fecha DESC",
                    (nom_comercio,),
                )
        else:
            if estado_turno:
                cur.execute(
                    "SELECT * FROM calendario WHERE estado = %s ORDER BY fecha DESC, horario ASC",
                    (estado_turno,),
                )
            else:
                cur.execute(
                    "SELECT * FROM calendario ORDER BY fecha DESC, horario ASC"
                )

    results = cur.fetchall()
    cur.close()

    cur = mysql.connection.cursor()
    cur.execute("SELECT nomComercio FROM calendario ORDER BY nomComercio ASC")
    consultas = [fila[0] for fila in cur.fetchall()]
    cur.close()
    """ 
    cur = mysql.connection.cursor()
    cur.execute("SELECT estado FROM calendario")
    consultas2 = [fila[0] for fila in cur.fetchall()]
    cur.close()
    """

    return render_template("consulta.html", results=results, consultas=consultas)


@app.route("/inicio", methods=["GET", "POST"])
def inicio():
    if request.method == "POST":
        # print(request.form['username'])
        # print(request.form['password'])
        user = User(0, request.form["username"], request.form["password"],"")
        logged_user = ModelUser.login(mysql, user)
        if logged_user != None:
            if logged_user.password:
                login_user(logged_user)
                """
                if logged_user.id_rol == 1:
                    return redirect(url_for("principal.html"))
                elif logged_user.id_rol == 2:
                    return redirect(url_for("consulta.html"))
                    """
                return redirect(url_for("principal"))
            else:
                flash("Datos Incorrectos")
                return render_template("/inicio.html")
        else:
            flash("Datos Incorrectos")
            return render_template("/inicio.html")
    else:
        return render_template("/inicio.html")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("inicio"))


@app.route("/calendario")
@login_required
def calendario():
    cur = mysql.connection.cursor()
    cur.execute("SELECT *FROM calendario")
    data = cur.fetchall()
    return render_template("calendario.html", data=data)
def status_401(error):
    return redirect(url_for("inicio"))
def status_404(error):
    return "<h1>Pagina no encontrada</h1>", 404


@app.route("/add_calendario", methods=["POST"])
def add_calendario():
    if request.method == "POST":
        nomCliente = request.form["nomCliente"]
        nomComercio = request.form["nomComercio"]
        nomServicio = request.form["nomServicio"]
        localidad = request.form["localidad"]
        direccion = request.form["direccion"]
        nomFumigador = request.form["nomFumigador"]
        producto = request.form["producto"]
        fecha = request.form["fecha"]
        horario = request.form["horario"]
        precio = request.form["precio"]
        estado = request.form["estado"]

        # Obtener el cursor

        cur = mysql.connection.cursor()

        # Ejecutar la consulta

        cur.execute(
            "INSERT INTO calendario(nomCliente, nomComercio, nomServicio, localidad, direccion, nomFumigador, producto, fecha, horario, precio, estado) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (
                nomCliente,
                nomComercio,
                nomServicio,
                localidad,
                direccion,
                nomFumigador,
                producto,
                fecha,
                horario,
                precio,
                estado,
            ),
        )
        mysql.connection.commit()
        flash("Se agendo correctamente el Servicio")
        return redirect(url_for("calendario"))


@app.route("/editTurno/<idFumigacion>")
def get_calendario(idFumigacion):
    cur = mysql.connection.cursor()
    idFumigacion_int = int(idFumigacion)
    cur.execute("SELECT * FROM calendario WHERE idFumigacion = %s", (idFumigacion_int,))
    data = cur.fetchall()
    return render_template("edit_turno.html", eturno=data[0])


@app.route("/updateTurno/<idFumigacion>", methods=["POST"])
def update_turno(idFumigacion):
    if request.method == "POST":
        nomCliente = request.form["nomCliente"]
        nomServicio = request.form["nomServicio"]
        localidad = request.form["localidad"]
        direccion = request.form["direccion"]
        nomFumigador = request.form["nomFumigador"]
        producto = request.form["producto"]
        fecha = request.form["fecha"]
        horario = request.form["horario"]
        precio = request.form["precio"]
        nomComercio = request.form["nomComercio"]
        estado = request.form["estado"]

        cur = mysql.connection.cursor()
        cur.execute(
            """
            UPDATE calendario
            SET nomCliente = %s,
                nomServicio = %s,
                localidad = %s,
                direccion = %s,
                nomFumigador = %s,
                producto = %s,
                fecha = %s,
                horario = %s,
                precio = %s,
                nomComercio = %s,
                estado = %s
            WHERE idFumigacion = %s
            """,
            (
                nomCliente,
                nomServicio,
                localidad,
                direccion,
                nomFumigador,
                producto,
                fecha,
                horario,
                precio,
                nomComercio,
                estado,
                idFumigacion,
            ),
        )
        mysql.connection.commit()
        flash("Turno Actualizado Correctamente")
        print(request.form)
        return redirect(url_for("consulta"))


@app.route("/deleteTurno/<int:idFumigacion>")
def delete_turno(idFumigacion):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM calendario WHERE idFumigacion = {0}".format(idFumigacion))
    mysql.connection.commit()
    flash("Turno Eliminado Correctamente")
    return redirect(url_for("consulta"))


# CLIENTE
@app.route("/cliente", methods=["GET"])
@login_required
def cliente():
    apellido_cliente = request.args.get("apellidocliente")
    cur = mysql.connection.cursor()
     
    if apellido_cliente:
            cur.execute(
                "SELECT * FROM cliente WHERE apellidocliente = %s ORDER BY apellidocliente DESC",
                (apellido_cliente,),
            )
    else:
        cur.execute("SELECT * FROM cliente")
    data = cur.fetchall()
    cur.close()

    # Obtener la lista de clientes desde tu base de datos
    cur = mysql.connection.cursor()
    cur.execute("SELECT apellidocliente FROM cliente ORDER BY apellidocliente ASC")  # Ajusta la consulta según la estructura de tu base de datos
    consultas = [fila[0] for fila in cur.fetchall()]
    cur.close()

    return render_template("cliente.html", dcliente=data, consultas=consultas)



@app.route("/add_cliente", methods=["POST"])
def add_cliente():
    if request.method == "POST":
        nomcliente = request.form["nomcliente"]
        apellidocliente = request.form["apellidocliente"]
        direccion = request.form["direccion"]
        tipocliente = request.form["tipocliente"]
        certificado = request.form["certificado"]
        presupuesto = request.form["presupuesto"]
        cuit = request.form["cuit"]
        celular = request.form["celular"]
        correo = request.form["correo"]


        # Obtener el cursor

        cur = mysql.connection.cursor()

        # Ejecutar la consulta

        cur.execute(
            "INSERT INTO cliente (nomcliente, apellidocliente, direccion, tipocliente, certificado, presupuesto, cuit, celular, correo) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (nomcliente, apellidocliente, direccion, tipocliente, certificado, presupuesto, cuit, celular, correo),
        )
        mysql.connection.commit()
        flash("Se agregó correctamante el contacto")
        return redirect(url_for("cliente"))


@app.route("/edit/<numcliente>")
def get_cliente(numcliente):
    cur = mysql.connection.cursor()
    numcliente_int = int(numcliente)
    cur.execute("SELECT * FROM cliente WHERE numcliente = %s", (numcliente_int,))
    data = cur.fetchall()
    return render_template("edit_cliente.html", ecliente=data[0])


@app.route("/update/<numcliente>", methods=["POST"])
def update_cliente(numcliente):
    if request.method == "POST":
        nomcliente = request.form["nomcliente"]
        apellidocliente = request.form["apellidocliente"]
        direccion = request.form["direccion"]
        tipocliente = request.form["tipocliente"]
        certificado = request.form["certificado"]
        presupuesto = request.form["presupuesto"]
        cuit = request.form["cuit"]
        celular = request.form["celular"]
        correo = request.form["correo"]
    cur = mysql.connection.cursor()
    cur.execute(
        """
     UPDATE cliente
     SET nomcliente = %s,
        apellidocliente = %s,
        direccion = %s,
        tipocliente = %s,
        certificado = %s,
        presupuesto = %s,
        cuit = %s,
        celular = %s,
        correo = %s
     WHERE numcliente = %s       
       """,
        (nomcliente, apellidocliente, direccion, tipocliente, certificado, presupuesto, cuit, celular, correo, numcliente),
    )
    mysql.connection.commit()
    flash("Cliente Actualizado Correctamente")
    return redirect(url_for("cliente"))


@app.route("/delete/<string:numcliente>")
def delete_cliente(numcliente):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM cliente WHERE numcliente = {0}".format(numcliente))
    mysql.connection.commit()
    flash("Cliente Eliminado Correctamente")
    return redirect(url_for("cliente"))


if __name__ == "__main__":
    app.register_error_handler(401, status_401)
    app.register_error_handler(404, status_404)
    app.run(debug=True)
