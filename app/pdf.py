"""Génération du PDF de simulation de rentabilité tontine (WeasyPrint, aucune IA)."""
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

from .logo import LOGO_GREY_B64
from .timeline import frise_svg

_env = Environment(loader=FileSystemLoader(str(Path(__file__).parent / "templates")))


def render_pdf_rentabilite(resultat: dict, client_nom: str = "") -> bytes:
    template = _env.get_template("pdf_rentabilite.html")
    html = template.render(
        r=resultat,
        frise=frise_svg(resultat),
        durees_simulees=any(t["duree"] > 20 or t["age"] > 70 for t in resultat["tranches"]),
        client_nom=client_nom.strip(),
        logo_b64=LOGO_GREY_B64,
        date_str=datetime.now().strftime("%d/%m/%Y"),
    )
    return HTML(string=html).write_pdf()
