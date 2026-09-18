"""
Tables de calcul de la rentabilité potentielle d'une tontine.

*** DONNÉES D'EXEMPLE, PAS LES VRAIES VALEURS ***
Les tables ci-dessous sont des données FICTIVES qui ne servent qu'à faire
fonctionner l'interface pendant le développement. Elles doivent être
remplacées par les deux tableaux Excel de Mickaël :

1. COEFFICIENTS_RENTABILITE[durée][âge] = coefficient à appliquer au montant
   placé pour obtenir la répartition potentielle reçue (tableau des
   rentabilités passées des tontines).
2. TARIFS_ASSURANCE_10000[durée][âge] = coût de l'assurance de la tontine,
   pour un placement de référence de 10 000 €. Pour un autre montant, on
   applique un simple produit en croix : tarif = TARIFS_ASSURANCE_10000 *
   (montant / 10000).

Ne jamais livrer de simulation client tant que ces tables n'ont pas été
remplacées par les vraies données.
"""

DONNEES_EXEMPLE = True  # passer à False une fois les vraies tables saisies

# durée (années) -> âge -> coefficient multiplicateur du montant placé
COEFFICIENTS_RENTABILITE: dict[int, dict[int, float]] = {
    10: {50: 1.15, 60: 1.22, 70: 1.35},
    15: {50: 1.35, 60: 1.48, 70: 1.70},
    20: {50: 1.60, 60: 1.85, 70: 2.20},
    25: {50: 1.95, 60: 2.35, 70: 2.90},
}

# durée (années) -> âge -> coût assurance pour 10 000 € placés
TARIFS_ASSURANCE_10000: dict[int, dict[int, float]] = {
    10: {50: 120.0, 60: 180.0, 70: 310.0},
    15: {50: 160.0, 60: 240.0, 70: 420.0},
    20: {50: 210.0, 60: 320.0, 70: 560.0},
    25: {50: 260.0, 60: 410.0, 70: 720.0},
}


def durees_disponibles() -> list[int]:
    return sorted(COEFFICIENTS_RENTABILITE.keys())


def ages_disponibles(duree: int) -> list[int]:
    return sorted(COEFFICIENTS_RENTABILITE.get(duree, {}).keys())


class DonneesManquantesError(Exception):
    pass


def _lookup(table: dict[int, dict[int, float]], duree: int, age: int) -> float:
    par_duree = table.get(duree)
    if par_duree is None or age not in par_duree:
        raise DonneesManquantesError(
            f"Pas de donnée pour durée={duree} ans, âge={age} ans."
        )
    return par_duree[age]


def calculer_rentabilite(montant: float, age: int, duree: int) -> dict:
    if montant <= 0:
        raise ValueError("Le montant doit être positif.")

    coefficient = _lookup(COEFFICIENTS_RENTABILITE, duree, age)
    tarif_10000 = _lookup(TARIFS_ASSURANCE_10000, duree, age)

    repartition_potentielle = montant * coefficient
    cout_assurance = tarif_10000 * (montant / 10000)
    gain_potentiel = repartition_potentielle - montant

    return {
        "montant": montant,
        "age": age,
        "duree": duree,
        "coefficient": coefficient,
        "repartition_potentielle": round(repartition_potentielle, 2),
        "gain_potentiel": round(gain_potentiel, 2),
        "cout_assurance": round(cout_assurance, 2),
        "donnees_exemple": DONNEES_EXEMPLE,
    }
