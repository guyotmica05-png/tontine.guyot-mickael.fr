"""Mode test (outil ouvert depuis la base test du CRM) : ni logo ni mention « Le Conservateur » en pied de page des PDF."""
import re

from . import logo as _logo

# Début de chaque image de logo définie dans logo.py (gris, couleur…)
_LOGOS = [v[:200] for k, v in vars(_logo).items() if k.startswith("LOGO_") and isinstance(v, str) and len(v) > 200]
_IMG = re.compile(r"<img\b[^>]*>", re.I)
_VIDE = re.compile(r'<div class="(?:cover-logo|bandeau-logo)">\s*</div>')


def retirer_logo(html: str) -> str:
    html = _IMG.sub(lambda m: "" if any(k in m.group(0) for k in _LOGOS) or "Le Conservateur" in m.group(0) else m.group(0), html)
    html = _VIDE.sub("", html)
    # Pieds de page, signature de fin et page de garde : plus de mention « Le Conservateur »
    for avant, apres in (("Agence Guyot, réseau Le Conservateur", "Agence Guyot"),
                         ("Agence Guyot — Le Conservateur", "Agence Guyot")):
        html = html.replace(avant, apres)
    return html


def est_mode_test(headers) -> bool:
    return (headers.get("x-mode-test") or "") == "1"
