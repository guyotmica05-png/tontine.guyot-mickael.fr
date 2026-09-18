"""Frise de vie de la cascade de tontines : SVG pur, calculé en Python, aucun JS."""

NAVY = "#1A2744"
NAVY_MID = "#2D3F6B"
GOLD = "#B8983A"
NAVY_LIGHT = "#EEF1F8"


def _fmt_eur(v: float) -> str:
    return "{:,.0f} €".format(v).replace(",", " ")


def frise_svg(cascade: dict) -> str:
    tranches = cascade["tranches"]
    age_depart = cascade["age"]
    annee_depart = cascade["annee_placement"]

    left_margin = 190
    right_margin = 30
    top_margin = 24
    row_height = 58
    bar_height = 22
    axis_gap = 34

    plot_width = 560
    max_duree = max(t["duree"] for t in tranches)
    scale = plot_width / max_duree

    n = len(tranches)
    width = left_margin + plot_width + right_margin
    height = top_margin + n * row_height + axis_gap + 26

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" font-family="Arial, Helvetica, sans-serif">'
    ]

    axis_y = top_margin + n * row_height + 6

    for i, t in enumerate(tranches):
        row_y = top_margin + i * row_height
        bar_y = row_y + (row_height - bar_height) / 2
        x0 = left_margin
        x1 = left_margin + t["duree"] * scale
        mid_y = bar_y + bar_height / 2

        # ligne de rappel verticale jusqu'à l'axe
        parts.append(
            f'<line x1="{x0}" y1="{bar_y + bar_height}" x2="{x0}" y2="{axis_y}" '
            f'stroke="#ccc" stroke-width="1" stroke-dasharray="2,2" />'
        )
        parts.append(
            f'<line x1="{x1}" y1="{bar_y + bar_height}" x2="{x1}" y2="{axis_y}" '
            f'stroke="#ccc" stroke-width="1" stroke-dasharray="2,2" />'
        )

        # libellé de la tranche, à gauche
        parts.append(
            f'<text x="{left_margin - 14}" y="{mid_y - 6}" text-anchor="end" '
            f'font-size="13" fill="{NAVY}" font-weight="600">{t["duree"]} ans</text>'
        )
        parts.append(
            f'<text x="{left_margin - 14}" y="{mid_y + 10}" text-anchor="end" '
            f'font-size="11" fill="#555">{_fmt_eur(t["montant"])}</text>'
        )

        # barre
        parts.append(
            f'<rect x="{x0}" y="{bar_y}" width="{x1 - x0}" height="{bar_height}" '
            f'rx="4" fill="{NAVY_MID}" />'
        )

        # marqueur de départ
        parts.append(f'<circle cx="{x0}" cy="{mid_y}" r="4" fill="{NAVY}" />')
        # marqueur de sortie
        parts.append(f'<circle cx="{x1}" cy="{mid_y}" r="4" fill="{GOLD}" />')

        # texte à la sortie (âge, année, capital perçu)
        parts.append(
            f'<text x="{x1 + 10}" y="{mid_y - 2}" font-size="12" fill="{NAVY}" font-weight="600">'
            f'{t["age_perception"]} ans · {t["annee_perception"]}</text>'
        )
        parts.append(
            f'<text x="{x1 + 10}" y="{mid_y + 13}" font-size="11" fill="{GOLD}">'
            f'{_fmt_eur(t["repartition_potentielle"])}</text>'
        )

    # axe des années (départ + une sortie par tranche, dédupliquées)
    annees = sorted({annee_depart} | {t["annee_perception"] for t in tranches})
    parts.append(
        f'<line x1="{left_margin}" y1="{axis_y}" x2="{left_margin + plot_width}" y2="{axis_y}" '
        f'stroke="{NAVY}" stroke-width="1.5" />'
    )
    for an in annees:
        x = left_margin + (an - annee_depart) * scale
        parts.append(f'<line x1="{x}" y1="{axis_y - 4}" x2="{x}" y2="{axis_y + 4}" stroke="{NAVY}" stroke-width="1.5" />')
        parts.append(
            f'<text x="{x}" y="{axis_y + 20}" text-anchor="middle" font-size="11" fill="{NAVY_MID}">{an}</text>'
        )

    parts.append(
        f'<text x="{left_margin}" y="{height - 2}" font-size="10" fill="#888">'
        f'Aujourd\'hui — client {age_depart} ans</text>'
    )

    parts.append("</svg>")
    return "".join(parts)
