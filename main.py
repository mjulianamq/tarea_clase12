#!/usr/bin/env python3
# ============================================================
# main.py — Orquestador principal de ChefCostos
# Reto 2: Gastronomía "Chef-Costos"
# Arquitectura: Backend (SQLite) + Frontend (Tkinter + Pillow)
# ============================================================

import os
import sys
import sqlite3

# ── Rutas del proyecto ─────────────────────────────────────
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR  = os.path.join(BASE_DIR, "Backend")
FRONTEND_DIR = os.path.join(BASE_DIR, "Frontend")
DB_PATH      = os.path.join(BACKEND_DIR, "chef_costos.db")

# Agrega Backend al path de importación
sys.path.insert(0, BACKEND_DIR)
sys.path.insert(0, FRONTEND_DIR)

from datos import (INGREDIENTES_INICIALES, PLATOS_INICIALES,
                   CATEGORIAS_PLATOS, UMBRAL_INFLACION)


# ════════════════════════════════════════════════════════════
#  INICIALIZACIÓN DE LA BASE DE DATOS
# ════════════════════════════════════════════════════════════
def crear_base_de_datos():
    """Crea las tablas y carga datos iniciales si es la primera ejecución."""
    primera_vez = not os.path.exists(DB_PATH)
    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA foreign_keys = ON")

    con.executescript("""
        CREATE TABLE IF NOT EXISTS ingredientes (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre           TEXT    NOT NULL,
            unidad           TEXT    NOT NULL,
            precio_historico REAL    NOT NULL,
            precio_mercado   REAL    NOT NULL
        );

        CREATE TABLE IF NOT EXISTS platos (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre    TEXT NOT NULL,
            categoria TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS recetas (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            id_plato       INTEGER NOT NULL REFERENCES platos(id),
            id_ingrediente INTEGER NOT NULL REFERENCES ingredientes(id),
            cantidad       REAL    NOT NULL,
            UNIQUE(id_plato, id_ingrediente)
        );

        CREATE TABLE IF NOT EXISTS alertas (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            id_ingrediente   INTEGER NOT NULL,
            nombre           TEXT    NOT NULL,
            inflacion_pct    REAL    NOT NULL,
            precio_historico REAL    NOT NULL,
            precio_mercado   REAL    NOT NULL,
            fecha            TEXT    NOT NULL
        );
    """)
    con.commit()

    if primera_vez:
        print("  ✅  Base de datos creada. Cargando datos iniciales...")

        for ing in INGREDIENTES_INICIALES:
            con.execute(
                "INSERT INTO ingredientes (nombre, unidad, precio_historico, precio_mercado) VALUES (?,?,?,?)",
                (ing["nombre"], ing["unidad"], ing["precio_historico"], ing["precio_mercado"]),
            )

        for p in PLATOS_INICIALES:
            con.execute(
                "INSERT INTO platos (nombre, categoria) VALUES (?,?)",
                (p["nombre"], p["categoria"]),
            )
        con.commit()

        recetas_iniciales = [
            (1, 2, 0.15), (1, 9, 0.20), (1, 10, 0.15), (1, 3, 0.10), (1, 4, 0.05),
            (2, 3, 0.30), (2, 1, 0.25), (2, 8, 0.03), (2, 4, 0.05),
            (3, 9, 0.35), (3, 7, 0.02), (3, 6, 0.05),
            (4, 2, 0.20), (4, 1, 0.25), (4, 5, 0.10), (4, 4, 0.05), (4, 6, 0.03),
        ]
        for rec in recetas_iniciales:
            try:
                con.execute(
                    "INSERT INTO recetas (id_plato, id_ingrediente, cantidad) VALUES (?,?,?)", rec
                )
            except Exception:
                pass

        cur = con.execute("SELECT id, nombre, precio_historico, precio_mercado FROM ingredientes")
        for row in cur.fetchall():
            ph, pm = row[2], row[3]
            inflacion = (pm - ph) / ph if ph else 0
            if inflacion > UMBRAL_INFLACION:
                from datetime import datetime
                con.execute(
                    "INSERT INTO alertas (id_ingrediente, nombre, inflacion_pct, precio_historico, precio_mercado, fecha) VALUES (?,?,?,?,?,?)",
                    (row[0], row[1], round(inflacion*100, 2), ph, pm,
                     datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                )
        con.commit()
        print("  ✅  Datos iniciales cargados correctamente.\n")

    con.close()


# ════════════════════════════════════════════════════════════
#  PUNTO DE ENTRADA
# ════════════════════════════════════════════════════════════
def main():
    print("""
  ╔══════════════════════════════════════════════════╗
  ║    🍽  CHEF-COSTOS — Control Gastronómico  🍽   ║
  ║         Reto 2: Gastronomía y Costos            ║
  ╚══════════════════════════════════════════════════╝
    """)
    print(f"  📂  Base de datos : {DB_PATH}")

    # 1. Inicializar BD
    crear_base_de_datos()

    # 2. Lanzar interfaz gráfica
    print("  🖥   Iniciando interfaz gráfica...\n")
    from interfaz import iniciar
    iniciar()


if __name__ == "__main__":
    main()
