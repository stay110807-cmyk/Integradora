"""Colores y utilidades compartidas por todas las vistas (paleta de los mockups)."""
import flet as ft

# --- Base ---
FONDO = "#F8FAFC"
TARJETA = "#FFFFFF"
BORDE = "#E2E8F0"
TINTA = "#111827"
TINTA_SUAVE = "#475569"
BLANCO = "#FFFFFF"
FILA_ALTERNA = "#F8FAFC"

# --- Campos ---
CAMPO_BORDE = "#64748B"
CAMPO_SOLO_LECTURA = "#F1F5F9"

# --- Encabezado del panel ---
HERO_PILDORA = "#1F2937"
HERO_TEXTO = "#E2E8F0"
VERDE_PUNTO = "#22C55E"

# --- Estados ---
OK_FONDO, OK_TEXTO = "#DCFCE7", "#166534"
AVISO_FONDO, AVISO_BORDE, AVISO_TEXTO = "#FEF3C7", "#D97706", "#92400E"
ERROR_FONDO, ERROR_BORDE, ERROR_TEXTO = "#FEE2E2", "#B91C1C", "#991B1B"
ROJO = "#B91C1C"


def dinero(valor):
    """1200 -> '$1,200.00'"""
    return f"${valor:,.2f}"


def borde_campo():
    """Borde de los campos de texto: gris normal, negro y más grueso al enfocarlo."""
    return {
        ft.ControlState.DEFAULT: ft.OutlineInputBorder(
            border_radius=6, side=ft.BorderSide(width=1, color=CAMPO_BORDE)),
        ft.ControlState.FOCUSED: ft.OutlineInputBorder(
            border_radius=6, side=ft.BorderSide(width=2, color=TINTA)),
    }
