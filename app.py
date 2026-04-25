from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)

def get_db_connection():
    return sqlite3.connect("Buvnieciba.db", check_same_thread=False)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/saraksts")
def saraksts():
    darbinieku_dati = get_darbinieki()
    return render_template("saraksts.html", darbinieki=darbinieku_dati)

@app.route("/darbi")
def darbi():
    darbu_dati = get_darbi()
    return render_template("darbi.html", darbi=darbu_dati)

def get_darbinieki():
    conn = sqlite3.connect("Buvnieciba.db")
    cursor = conn.cursor()
    cursor.execute("SELECT Darbinieka_vards, Darbinieka_uzvards, Darbinieka_tel, Darbinieka_amats FROM Darbinieki")
    darbinieki = [
        {
            "Darbinieka_vards": row[0],
            "Darbinieka_uzvards": row[1],
            "Darbinieka_tel": row[2],
            "Darbinieka_amats": row[3],
        }
        for row in cursor.fetchall()
    ]
    conn.close()
    return darbinieki

def get_darbi():
    conn = sqlite3.connect("Buvnieciba.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT d.Apraksts, d.izmaksas, d.Beigu_datums, o.Adrese
        FROM Darbi d
        LEFT JOIN Objekti o ON o.id_objekts = d.id_objekts
        """
    )
    darbi = [
        {
            "Apraksts": row[0],
            "izmaksas": row[1],
            "Beigu_datums": row[2],
            "Adrese": row[3] if row[3] else "Adrese nav norādīta",
        }
        for row in cursor.fetchall()
    ]
    conn.close()
    return darbi

def get_darbi_redigesanai():
    conn = sqlite3.connect("Buvnieciba.db")
    cursor = conn.cursor()
    cursor.execute("SELECT rowid, Apraksts, izmaksas, Beigu_datums FROM Darbi")
    darbi = [
        {
            "darbs_rowid": row[0],
            "Apraksts": row[1],
            "izmaksas": row[2],
            "Beigu_datums": row[3],
        }
        for row in cursor.fetchall()
    ]
    conn.close()
    return darbi

@app.route("/rediget_darbus", methods=["GET", "POST"])
def rediget_darbus():
    if request.method == "POST":
        action = request.form.get("action", "").strip()
        conn = sqlite3.connect("Buvnieciba.db")
        cursor = conn.cursor()

        if action == "update":
            darbs_rowid = request.form.get("darbs_rowid", "").strip()
            apraksts = request.form.get("apraksts", "").strip()
            izmaksas = request.form.get("izmaksas", "").strip()
            beigu_datums = request.form.get("beigu_datums", "").strip()

            if darbs_rowid and apraksts and izmaksas and beigu_datums:
                cursor.execute(
                    "UPDATE Darbi SET Apraksts = ?, izmaksas = ?, Beigu_datums = ? WHERE rowid = ?",
                    (apraksts, izmaksas, beigu_datums, darbs_rowid),
                )

        if action == "delete":
            darbs_rowid = request.form.get("darbs_rowid", "").strip()
            if darbs_rowid:
                cursor.execute("DELETE FROM Darbi WHERE rowid = ?", (darbs_rowid,))

        conn.commit()
        conn.close()

        return redirect(url_for("rediget_darbus"))

    darbi = get_darbi_redigesanai()
    return render_template("rediget_darbus.html", darbi=darbi)

@app.route("/pievienot_darbu", methods=["GET", "POST"])
def pievienot_darbu():
    if request.method == "POST":
        id_objekts = request.form.get("id_objekts", "").strip()
        id_darbinieks = request.form.get("id_darbinieks", "").strip()
        apraksts = request.form.get("apraksts", "").strip()
        izmaksas = request.form.get("izmaksas", "").strip()
        beigu_datums = request.form.get("beigu_datums", "").strip()

        if id_objekts and id_darbinieks and apraksts and izmaksas and beigu_datums:
            conn = sqlite3.connect("Buvnieciba.db")
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Darbi (id_objekts, id_darbinieks, Apraksts, izmaksas, Beigu_datums) VALUES (?, ?, ?, ?, ?)",
                (id_objekts, id_darbinieks, apraksts, izmaksas, beigu_datums),
            )
            conn.commit()
            conn.close()

        return redirect(url_for("pievienot_darbu"))

    objekti = get_objekti_redigesanai()
    darbinieki = get_darbinieki_redigesanai()
    return render_template("pievienot_darbu.html", objekti=objekti, darbinieki=darbinieki)

def get_darbinieki_redigesanai():
    conn = sqlite3.connect("Buvnieciba.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id_darbinieks, Darbinieka_vards, Darbinieka_uzvards, Darbinieka_amats, Darbinieka_tel FROM Darbinieki"
    )
    darbinieki = [
        {
            "id_darbinieks": row[0],
            "Darbinieka_vards": row[1],
            "Darbinieka_uzvards": row[2],
            "Darbinieka_amats": row[3],
            "Darbinieka_tel": row[4],
        }
        for row in cursor.fetchall()
    ]
    conn.close()
    return darbinieki

@app.route("/rediget_darbinieks", methods=["GET", "POST"])
def rediget_darbinieks():
    if request.method == "POST":
        action = request.form.get("action")
        conn = sqlite3.connect("Buvnieciba.db")
        cursor = conn.cursor()

        if action == "add":
            vards = request.form.get("darbinieka_vards", "").strip()
            uzvards = request.form.get("darbinieka_uzvards", "").strip()
            amats = request.form.get("darbinieka_amats", "").strip()
            tel = request.form.get("darbinieka_tel", "").strip()

            if vards and uzvards and amats and tel:
                cursor.execute(
                    "INSERT INTO Darbinieki (Darbinieka_vards, Darbinieka_uzvards, Darbinieka_amats, Darbinieka_tel) VALUES (?, ?, ?, ?)",
                    (vards, uzvards, amats, tel),
                )

        if action == "delete":
            darbinieks_id = request.form.get("id_darbinieks", "").strip()
            if darbinieks_id:
                cursor.execute("DELETE FROM Darbinieki WHERE id_darbinieks = ?", (darbinieks_id,))

        conn.commit()
        conn.close()
        return redirect(url_for("rediget_darbinieks"))

    darbinieki = get_darbinieki_redigesanai()
    return render_template("rediget_darbinieks.html", darbinieki=darbinieki)

@app.route("/klienti")
def klientu_saraksts():
    klientu_dati = get_klienti()
    return render_template("klientu_saraksts.html", klienti=klientu_dati)
def get_klienti():
    conn = sqlite3.connect("Buvnieciba.db")
    cursor = conn.cursor()
    cursor.execute("SELECT klienta_vards, klienta_uzvards, klienta_telefons, klienta_epasts FROM Klienti")
    klienti = [
        {
            "klienta_vards": row[0],
            "klienta_uzvards": row[1],
            "klienta_telefons": row[2],
            "klienta_epasts": row[3],
        }
        for row in cursor.fetchall()
    ]
    conn.close()
    return klienti

def get_klienti_redigesanai():
    conn = sqlite3.connect("Buvnieciba.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id_klients, klienta_vards, klienta_uzvards, klienta_telefons, klienta_epasts FROM Klienti"
    )
    klienti = [
        {
            "id_klients": row[0],
            "klienta_vards": row[1],
            "klienta_uzvards": row[2],
            "klienta_telefons": row[3],
            "klienta_epasts": row[4],
        }
        for row in cursor.fetchall()
    ]
    conn.close()
    return klienti

@app.route("/rediget_klienti", methods=["GET", "POST"])
def rediget_klienti():
    if request.method == "POST":
        action = request.form.get("action")
        conn = sqlite3.connect("Buvnieciba.db")
        cursor = conn.cursor()

        if action == "add":
            vards = request.form.get("klienta_vards", "").strip()
            uzvards = request.form.get("klienta_uzvards", "").strip()
            telefons = request.form.get("klienta_telefons", "").strip()
            epasts = request.form.get("klienta_epasts", "").strip()

            if vards and uzvards and telefons:
                cursor.execute(
                    "INSERT INTO Klienti (klienta_vards, klienta_uzvards, klienta_telefons, klienta_epasts) VALUES (?, ?, ?, ?)",
                    (vards, uzvards, telefons, epasts if epasts else None),
                )

        if action == "delete":
            klients_id = request.form.get("id_klients", "").strip()
            if klients_id:
                cursor.execute("DELETE FROM Klienti WHERE id_klients = ?", (klients_id,))

        conn.commit()
        conn.close()
        return redirect(url_for("rediget_klienti"))

    klienti = get_klienti_redigesanai()
    return render_template("rediget_klienti.html", klienti=klienti)

@app.route("/materiali")
def materiali():
    materiali_dati = get_materiali()
    return render_template("materiali.html", mats = materiali_dati)

def get_materiali():
    conn = sqlite3.connect("Buvnieciba.db")
    cursor = conn.cursor()
    cursor.execute("SELECT Materiala_nosaukums, Daudzums, Cena FROM Materiali")
    materials = [{"Materiala_nosaukums": row[0], "Daudzums": row[1], "Cena": row[2]} for row in cursor.fetchall()]
    conn.close()
    return materials

def get_materiali_redigesanai():
    conn = sqlite3.connect("Buvnieciba.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id_materials, Materiala_nosaukums, Cena, Daudzums FROM Materiali")
    materiali = [
        {
            "id_materials": row[0],
            "Materiala_nosaukums": row[1],
            "Cena": row[2],
            "Daudzums": row[3],
        }
        for row in cursor.fetchall()
    ]
    conn.close()
    return materiali

def get_objekta_materiali():
    conn = sqlite3.connect("Buvnieciba.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT om.id_objekts, o.Adrese, om.id_materials, m.Materiala_nosaukums, om.daudzums
        FROM ObjektaMateriali om
        LEFT JOIN Objekti o ON o.id_objekts = om.id_objekts
        LEFT JOIN Materiali m ON m.id_materials = om.id_materials
        ORDER BY om.id_objekts, om.id_materials
        """
    )
    saites = [
        {
            "id_objekts": row[0],
            "Adrese": row[1] if row[1] else "Adrese nav norādīta",
            "id_materials": row[2],
            "Materiala_nosaukums": row[3] if row[3] else "Materiāls nav atrasts",
            "daudzums": row[4],
        }
        for row in cursor.fetchall()
    ]
    conn.close()
    return saites

@app.route("/objekta_materiali", methods=["GET", "POST"])
def objekta_materiali():
    if request.method == "POST":
        action = request.form.get("action", "").strip()
        conn = sqlite3.connect("Buvnieciba.db")
        cursor = conn.cursor()

        if action == "add":
            id_objekts = request.form.get("id_objekts", "").strip()
            id_materials = request.form.get("id_materials", "").strip()
            daudzums = request.form.get("daudzums", "").strip()

            if id_objekts and id_materials and daudzums:
                cursor.execute(
                    "SELECT daudzums FROM ObjektaMateriali WHERE id_objekts = ? AND id_materials = ?",
                    (id_objekts, id_materials),
                )
                esoais = cursor.fetchone()

                if esoais:
                    cursor.execute(
                        "UPDATE ObjektaMateriali SET daudzums = ? WHERE id_objekts = ? AND id_materials = ?",
                        (daudzums, id_objekts, id_materials),
                    )
                else:
                    cursor.execute(
                        "INSERT INTO ObjektaMateriali (id_objekts, id_materials, daudzums) VALUES (?, ?, ?)",
                        (id_objekts, id_materials, daudzums),
                    )

        if action == "delete":
            id_objekts = request.form.get("id_objekts", "").strip()
            id_materials = request.form.get("id_materials", "").strip()
            if id_objekts and id_materials:
                cursor.execute(
                    "DELETE FROM ObjektaMateriali WHERE id_objekts = ? AND id_materials = ?",
                    (id_objekts, id_materials),
                )

        conn.commit()
        conn.close()
        return redirect(url_for("objekta_materiali"))

    objekti = get_objekti_redigesanai()
    materiali = get_materiali_redigesanai()
    saites = get_objekta_materiali()
    return render_template(
        "objekta_materiali.html",
        objekti=objekti,
        materiali=materiali,
        saites=saites,
    )

@app.route("/rediget_materialus", methods=["GET", "POST"])
def rediget_materialus():
    if request.method == "POST":
        materiala_id = request.form.get("id_materials", "").strip()
        cena = request.form.get("cena", "").strip()
        daudzums = request.form.get("daudzums", "").strip()

        if materiala_id and cena and daudzums:
            conn = sqlite3.connect("Buvnieciba.db")
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE Materiali SET Cena = ?, Daudzums = ? WHERE id_materials = ?",
                (cena, daudzums, materiala_id),
            )
            conn.commit()
            conn.close()

        return redirect(url_for("rediget_materialus"))

    materiali = get_materiali_redigesanai()
    return render_template("rediget_materialus.html", materiali=materiali)

@app.route("/pievienot_materialu", methods=["GET", "POST"])
def pievienot_materialu():
    if request.method == "POST":
        nosaukums = request.form.get("materiala_nosaukums", "").strip()
        cena = request.form.get("cena", "").strip()
        daudzums = request.form.get("daudzums", "").strip()

        if nosaukums and cena and daudzums:
            conn = sqlite3.connect("Buvnieciba.db")
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Materiali (Materiala_nosaukums, Cena, Daudzums) VALUES (?, ?, ?)",
                (nosaukums, cena, daudzums),
            )
            conn.commit()
            conn.close()

        return redirect(url_for("pievienot_materialu"))

    return render_template("pievienot_materialu.html")

@app.route("/dzest_materialu", methods=["GET", "POST"])
def dzest_materialu():
    if request.method == "POST":
        materiala_id = request.form.get("id_materials", "").strip()
        if materiala_id:
            conn = sqlite3.connect("Buvnieciba.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Materiali WHERE id_materials = ?", (materiala_id,))
            conn.commit()
            conn.close()

        return redirect(url_for("dzest_materialu"))

    materiali = get_materiali_redigesanai()
    return render_template("dzest_materialu.html", materiali=materiali)

@app.route("/objekti")
def objekti():
    objektu_dati = get_objekti()
    return render_template("objekti.html", objekti=objektu_dati)

def get_objekti_redigesanai():
    conn = sqlite3.connect("Buvnieciba.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id_objekts, Adrese, Objekta_tips, Status, Sakums_datums FROM Objekti")
    objekti = [
        {
            "id_objekts": row[0],
            "Adrese": row[1],
            "Objekta_tips": row[2],
            "Status": row[3],
            "Sakums_datums": row[4],
        }
        for row in cursor.fetchall()
    ]
    conn.close()
    return objekti

@app.route("/rediget_objektus", methods=["GET", "POST"])
def rediget_objektus():
    if request.method == "POST":
        objekta_id = request.form.get("id_objekts", "").strip()
        adrese = request.form.get("adrese", "").strip()
        objekta_tips = request.form.get("objekta_tips", "").strip()
        status = request.form.get("status", "").strip()
        sakums_datums = request.form.get("sakums_datums", "").strip()

        if objekta_id and adrese and objekta_tips and status and sakums_datums:
            conn = sqlite3.connect("Buvnieciba.db")
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE Objekti SET Adrese = ?, Objekta_tips = ?, Status = ?, Sakums_datums = ? WHERE id_objekts = ?",
                (adrese, objekta_tips, status, sakums_datums, objekta_id),
            )
            conn.commit()
            conn.close()

        return redirect(url_for("rediget_objektus"))

    objekti = get_objekti_redigesanai()
    return render_template("rediget_objektus.html", objekti=objekti)

@app.route("/pievienot_objektu", methods=["GET", "POST"])
def pievienot_objektu():
    if request.method == "POST":
        id_klients = request.form.get("id_klients", "").strip()
        adrese = request.form.get("adrese", "").strip()
        objekta_tips = request.form.get("objekta_tips", "").strip()
        status = request.form.get("status", "").strip()
        sakums_datums = request.form.get("sakums_datums", "").strip()

        if id_klients and adrese and objekta_tips and status and sakums_datums:
            conn = sqlite3.connect("Buvnieciba.db")
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Objekti (id_klients, Adrese, Objekta_tips, Status, Sakums_datums) VALUES (?, ?, ?, ?, ?)",
                (id_klients, adrese, objekta_tips, status, sakums_datums),
            )
            conn.commit()
            conn.close()

        return redirect(url_for("pievienot_objektu"))

    klienti = get_klienti_redigesanai()
    return render_template("pievienot_objektu.html", klienti=klienti)

@app.route("/dzest_objektu", methods=["GET", "POST"])
def dzest_objektu():
    if request.method == "POST":
        objekta_id = request.form.get("id_objekts", "").strip()
        if objekta_id:
            conn = sqlite3.connect("Buvnieciba.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Objekti WHERE id_objekts = ?", (objekta_id,))
            conn.commit()
            conn.close()

        return redirect(url_for("dzest_objektu"))

    objekti = get_objekti_redigesanai()
    return render_template("dzest_objektu.html", objekti=objekti)

def get_objekti():
    conn = sqlite3.connect("Buvnieciba.db")
    cursor = conn.cursor()
    cursor.execute("SELECT Adrese, Objekta_tips, Status, Sakums_datums FROM Objekti")
    objekti = [
        {
            "Adrese": row[0],
            "Objekta_tips": row[1],
            "Status": row[2],
            "Sakums_datums": row[3],
        }
        for row in cursor.fetchall()
    ]
    conn.close()
    return objekti
        

if __name__ == "__main__":
    app.run(debug=True)