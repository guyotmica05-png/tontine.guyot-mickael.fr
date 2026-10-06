"""
Backend tontine.guyot-mickael.fr — 2 outils déterministes, aucun appel IA :
1. /rentabilite : simulation de rentabilité potentielle d'une tontine (âge,
   durée, montant) + génération PDF.
2. /fiscalite : matrice de décision fiscale à la sortie (IR barème vs
   prélèvement forfaitaire non libératoire), calculée en JavaScript pur côté
   navigateur (pas d'appel serveur).

Règles :
- Aucune écriture disque, tout en mémoire (io.BytesIO), rien n'est conservé
  entre deux requêtes.
- Aucun appel LLM. Calculs déterministes uniquement (app/data.py).
"""
import io
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import data
from .pdf import render_pdf_rentabilite
from .timeline import frise_svg

app = FastAPI(title="Tontine — Guyot Mickaël", docs_url=None, redoc_url=None)

templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "static")), name="static")


@app.get("/api/health")
def health():
    return {"status": "ok"}


# --- Authentification : contrôlée en amont par Traefik (forwardAuth -> gm-auth) ----
# Aucun accès n'arrive ici sans session valide ; la connexion et la déconnexion
# se font sur guyot-mickael.fr, avec un seul identifiant pour tous les sites.


@app.post("/logout")
def logout():
    return RedirectResponse("https://guyot-mickael.fr/logout", status_code=303)


# --- Pages ----------------------------------------------------------------


@app.get("/")
def home(request: Request):
    cible = "/rentabilite" + ("?" + request.url.query if request.url.query else "")
    return RedirectResponse(cible, status_code=303)


@app.get("/rentabilite")
def page_rentabilite(request: Request):
    return templates.TemplateResponse(request, "rentabilite.html", {})


@app.get("/fiscalite")
def page_fiscalite(request: Request):
    return templates.TemplateResponse(request, "fiscalite.html", {})


# --- API rentabilité (calcul + PDF) ---------------------------------------


@app.get("/api/durees-disponibles")
def api_durees(age: int):
    return {"durees": data.durees_disponibles_pour_age(age)}


def _parse_cascade_payload(payload: dict) -> dict:
    age = int(payload.get("age"))
    tranches = payload.get("tranches") or []
    if not isinstance(tranches, list) or not tranches:
        raise ValueError("Au moins une tranche est requise.")
    tranches_norm = [{"montant": float(t["montant"]), "duree": int(t["duree"])} for t in tranches]
    situation = "couple" if payload.get("situation") == "couple" else "seul"
    encours_total = float(payload.get("encours_total") or 0)
    return data.calculer_cascade(age, tranches_norm, situation=situation, encours_total=encours_total)


@app.post("/api/calcul-rentabilite")
async def api_calcul_rentabilite(request: Request):
    payload = await request.json()
    try:
        resultat = _parse_cascade_payload(payload)
    except (data.DonneesManquantesError, ValueError, TypeError, KeyError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    resultat["frise_svg"] = frise_svg(resultat)
    return resultat


@app.post("/api/pdf-rentabilite")
async def api_pdf_rentabilite(request: Request):
    payload = await request.json()
    try:
        resultat = _parse_cascade_payload(payload)
    except (data.DonneesManquantesError, ValueError, TypeError, KeyError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    client_nom = str(payload.get("client_nom") or "")
    try:
        pdf_bytes = render_pdf_rentabilite(resultat, client_nom)
    except Exception:
        raise HTTPException(status_code=500, detail="Erreur lors de la génération du PDF.")

    buffer = io.BytesIO(pdf_bytes)
    filename = "simulation_tontine.pdf"
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.exception_handler(Exception)
async def catch_all(request: Request, exc: Exception):
    from fastapi.responses import JSONResponse

    return JSONResponse(status_code=500, content={"detail": "Erreur interne."})
