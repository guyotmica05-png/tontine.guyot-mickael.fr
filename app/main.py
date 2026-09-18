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

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import RedirectResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import auth, data
from .pdf import render_pdf_rentabilite

app = FastAPI(title="Tontine — Guyot Mickaël", docs_url=None, redoc_url=None)

templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "static")), name="static")


@app.get("/api/health")
def health():
    return {"status": "ok"}


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        return forwarded.split(",")[-1].strip()
    return request.client.host if request.client else "unknown"


def require_session(request: Request) -> None:
    if not auth.is_valid_session(request.cookies.get(auth.SESSION_COOKIE)):
        raise HTTPException(status_code=303, headers={"Location": "/login"})


@app.exception_handler(HTTPException)
async def redirect_on_auth(request: Request, exc: HTTPException):
    if exc.status_code == 303 and exc.headers and exc.headers.get("Location") == "/login":
        return RedirectResponse("/login", status_code=303)
    raise exc


# --- Authentification ---------------------------------------------------


@app.get("/login")
def login_form(request: Request):
    if auth.is_valid_session(request.cookies.get(auth.SESSION_COOKIE)):
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse(request, "login.html", {"error": None})


@app.post("/login")
def login_submit(request: Request, username: str = Form(...), password: str = Form(...)):
    ip = _client_ip(request)
    if auth.is_locked_out(ip):
        return templates.TemplateResponse(
            request,
            "login.html",
            {"error": "Trop de tentatives, réessaie dans quelques minutes."},
            status_code=429,
        )
    if auth.check_credentials(username, password):
        auth.clear_failures(ip)
        token = auth.create_session()
        response = RedirectResponse("/", status_code=303)
        response.set_cookie(
            auth.SESSION_COOKIE, token, httponly=True, secure=True, samesite="lax", path="/"
        )
        return response
    auth.register_failure(ip)
    return templates.TemplateResponse(
        request, "login.html", {"error": "Identifiants incorrects."}, status_code=401
    )


@app.post("/logout")
def logout(request: Request):
    auth.destroy_session(request.cookies.get(auth.SESSION_COOKIE))
    response = RedirectResponse("/login", status_code=303)
    response.delete_cookie(auth.SESSION_COOKIE, path="/")
    return response


# --- Pages ----------------------------------------------------------------


@app.get("/")
def home(request: Request, _: None = Depends(require_session)):
    return RedirectResponse("/rentabilite", status_code=303)


@app.get("/rentabilite")
def page_rentabilite(request: Request, _: None = Depends(require_session)):
    return templates.TemplateResponse(
        request,
        "rentabilite.html",
        {
            "durees": data.durees_disponibles(),
            "donnees_exemple": data.DONNEES_EXEMPLE,
        },
    )


@app.get("/fiscalite")
def page_fiscalite(request: Request, _: None = Depends(require_session)):
    return templates.TemplateResponse(request, "fiscalite.html", {})


# --- API rentabilité (calcul + PDF) ---------------------------------------


@app.get("/api/ages-disponibles")
def api_ages(duree: int, _: None = Depends(require_session)):
    return {"ages": data.ages_disponibles(duree)}


@app.post("/api/calcul-rentabilite")
async def api_calcul_rentabilite(request: Request, _: None = Depends(require_session)):
    payload = await request.json()
    try:
        montant = float(payload.get("montant"))
        age = int(payload.get("age"))
        duree = int(payload.get("duree"))
        resultat = data.calculer_rentabilite(montant, age, duree)
    except (data.DonneesManquantesError, ValueError, TypeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return resultat


@app.post("/api/pdf-rentabilite")
async def api_pdf_rentabilite(request: Request, _: None = Depends(require_session)):
    payload = await request.json()
    try:
        montant = float(payload.get("montant"))
        age = int(payload.get("age"))
        duree = int(payload.get("duree"))
        resultat = data.calculer_rentabilite(montant, age, duree)
    except (data.DonneesManquantesError, ValueError, TypeError) as exc:
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
