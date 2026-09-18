"""
Authentification compte unique, partagée avec c20.guyot-mickael.fr et
pilotage.guyot-mickael.fr (même identifiant/mot de passe, sessions distinctes).

- Session en cookie sans Max-Age/Expires : le navigateur la supprime a la
  fermeture complete du navigateur (comportement demande par Mickael).
- Sessions gardees en memoire process : un redemarrage du conteneur force
  une reconnexion, ce qui est acceptable pour un site mono-utilisateur.
"""
import os
import secrets
import time

import bcrypt

SESSION_COOKIE = "tontine_session"
SESSION_TTL = 12 * 60 * 60  # duree de vie absolue, meme en usage continu

# Expiration par inactivite. Le cookie de session ne suffit pas : Chrome et Edge
# restaurent les cookies de session quand l'option "Continuer la ou vous vous
# etes arrete" est active, donc fermer la fenetre ne deconnecte pas toujours.
# Ce delai, lui, est verifie cote serveur et ne depend d'aucun reglage du
# navigateur.
IDLE_TIMEOUT = 4 * 60 * 60

MAX_ATTEMPTS = 5
WINDOW_S = 10 * 60

_sessions: dict[str, dict] = {}
_attempts: dict[str, dict] = {}


def is_locked_out(ip: str) -> bool:
    entry = _attempts.get(ip)
    if not entry:
        return False
    if time.time() - entry["first"] > WINDOW_S:
        _attempts.pop(ip, None)
        return False
    return entry["count"] >= MAX_ATTEMPTS


def register_failure(ip: str) -> None:
    entry = _attempts.get(ip)
    if not entry or time.time() - entry["first"] > WINDOW_S:
        _attempts[ip] = {"count": 1, "first": time.time()}
    else:
        entry["count"] += 1


def clear_failures(ip: str) -> None:
    _attempts.pop(ip, None)


def check_credentials(username: str, password: str) -> bool:
    expected_user = os.environ.get("AUTH_USERNAME", "")
    expected_hash = os.environ.get("AUTH_PASSWORD_HASH", "")
    if not expected_user or not expected_hash:
        return False
    if not secrets.compare_digest(username, expected_user):
        return False
    try:
        return bcrypt.checkpw(password.encode(), expected_hash.encode())
    except ValueError:
        return False


def create_session() -> str:
    token = secrets.token_urlsafe(32)
    now = time.time()
    _sessions[token] = {"created": now, "last_seen": now}
    return token


def is_valid_session(token: str | None) -> bool:
    entry = _sessions.get(token) if token else None
    if not entry:
        return False

    now = time.time()
    if now - entry["created"] > SESSION_TTL or now - entry["last_seen"] > IDLE_TIMEOUT:
        _sessions.pop(token, None)
        return False

    entry["last_seen"] = now
    return True


def destroy_session(token: str | None) -> None:
    if token:
        _sessions.pop(token, None)
