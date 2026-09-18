"""
Tables de calcul de la rentabilité potentielle d'une tontine.

Sources (fournies par Mickaël le 18/09/2026, Les Associations Mutuelles Le
Conservateur) :

1. COEFFICIENTS_RENTABILITE[durée][âge] = coefficient multiplicateur des
   sommes versées, pour une adhésion à une tontine à prime unique avec
   contrat de prévoyance des tontiniers en complément.
   "LA TONTINE PRIME UNIQUE — Coefficients 2006-2026" (T16 - 04/2026 - 1 - B).
   Attention (mention du document) : les coefficients pour durées > 20 ans
   et âges à l'adhésion > 70 ans / âges au terme > 80 ans sont des
   coefficients simulés, pas des coefficients constatés.

2. TARIFS_ASSURANCE_10000[durée][âge] = coût de l'assurance Prévoyance
   Décès - PTIA Toutes Causes (Convention 1325/A - Sérénité Protection
   Patrimoine), pour 10 000 € de capital de base, avec revalorisation
   annuelle du capital de base de 0,5 % (T27 - 10/2020 - B).
   Pour un autre montant, produit en croix : tarif = TARIFS_ASSURANCE_10000
   * (montant / 10000).

Les deux tables ont des étendues différentes (la table de coefficients est
plus restreinte : âge 20-74, durée 10-25) ; c'est elle qui borne les
combinaisons proposées côté site, la table de tarifs (âge 12-76, durée
9-30) couvre toujours plus large.
"""
from datetime import date

DONNEES_EXEMPLE = False

# --- Table 1 : coefficients de répartition (âge à l'adhésion -> par durée) ---
# Une ligne par âge, valeurs dans l'ordre des durées à partir de 10 ans
# (le nombre de valeurs diminue au-delà de 60 ans car âge + durée <= 85).
_COEF_DUREE_DEBUT = 10
_COEF_ROWS_BRUT: dict[int, str] = {
    20: "1,38 1,45 1,53 1,61 1,70 1,79 1,89 1,99 2,10 2,21 2,33 2,46 2,59 2,73 2,88 3,03",
    21: "1,38 1,45 1,53 1,61 1,70 1,79 1,89 1,99 2,10 2,21 2,33 2,46 2,59 2,73 2,88 3,04",
    22: "1,38 1,45 1,53 1,61 1,70 1,79 1,89 1,99 2,10 2,21 2,33 2,46 2,59 2,73 2,88 3,04",
    23: "1,38 1,45 1,53 1,61 1,70 1,79 1,89 1,99 2,10 2,21 2,33 2,46 2,59 2,73 2,88 3,04",
    24: "1,38 1,45 1,53 1,61 1,70 1,79 1,89 1,99 2,10 2,21 2,33 2,46 2,59 2,74 2,88 3,04",
    25: "1,38 1,45 1,53 1,61 1,70 1,79 1,89 1,99 2,10 2,21 2,33 2,46 2,60 2,74 2,89 3,04",
    26: "1,38 1,45 1,53 1,61 1,70 1,79 1,89 1,99 2,10 2,22 2,34 2,46 2,60 2,74 2,89 3,05",
    27: "1,38 1,45 1,53 1,61 1,70 1,79 1,89 1,99 2,10 2,22 2,34 2,46 2,60 2,74 2,89 3,05",
    28: "1,38 1,45 1,53 1,61 1,70 1,79 1,89 1,99 2,10 2,22 2,34 2,47 2,60 2,74 2,89 3,05",
    29: "1,38 1,45 1,53 1,62 1,70 1,80 1,89 2,00 2,10 2,22 2,34 2,47 2,60 2,75 2,90 3,06",
    30: "1,38 1,45 1,53 1,62 1,70 1,80 1,89 2,00 2,11 2,22 2,34 2,47 2,61 2,75 2,90 3,06",
    31: "1,38 1,45 1,53 1,62 1,70 1,80 1,89 2,00 2,11 2,22 2,34 2,47 2,61 2,75 2,90 3,06",
    32: "1,38 1,45 1,53 1,62 1,70 1,80 1,90 2,00 2,11 2,22 2,35 2,47 2,61 2,75 2,91 3,07",
    33: "1,38 1,46 1,53 1,62 1,71 1,80 1,90 2,00 2,11 2,23 2,35 2,48 2,61 2,76 2,91 3,07",
    34: "1,38 1,46 1,53 1,62 1,71 1,80 1,90 2,00 2,11 2,23 2,35 2,48 2,62 2,76 2,91 3,08",
    35: "1,38 1,46 1,54 1,62 1,71 1,80 1,90 2,00 2,11 2,23 2,35 2,48 2,62 2,77 2,92 3,08",
    36: "1,38 1,46 1,54 1,62 1,71 1,80 1,90 2,01 2,12 2,23 2,36 2,49 2,62 2,77 2,92 3,09",
    37: "1,38 1,46 1,54 1,62 1,71 1,80 1,90 2,01 2,12 2,23 2,36 2,49 2,63 2,77 2,93 3,09",
    38: "1,38 1,46 1,54 1,62 1,71 1,80 1,90 2,01 2,12 2,24 2,36 2,49 2,63 2,78 2,94 3,10",
    39: "1,38 1,46 1,54 1,62 1,71 1,81 1,91 2,01 2,12 2,24 2,36 2,50 2,64 2,78 2,94 3,11",
    40: "1,38 1,46 1,54 1,62 1,71 1,81 1,91 2,01 2,13 2,24 2,37 2,50 2,64 2,79 2,95 3,12",
    41: "1,38 1,46 1,54 1,63 1,71 1,81 1,91 2,02 2,13 2,25 2,37 2,51 2,65 2,80 2,96 3,12",
    42: "1,39 1,46 1,54 1,63 1,72 1,81 1,91 2,02 2,13 2,25 2,38 2,51 2,65 2,80 2,96 3,13",
    43: "1,39 1,46 1,54 1,63 1,72 1,81 1,91 2,02 2,13 2,25 2,38 2,52 2,66 2,81 2,97 3,14",
    44: "1,39 1,46 1,54 1,63 1,72 1,82 1,92 2,02 2,14 2,26 2,39 2,52 2,67 2,82 2,98 3,16",
    45: "1,39 1,46 1,55 1,63 1,72 1,82 1,92 2,03 2,14 2,26 2,39 2,53 2,67 2,83 2,99 3,17",
    46: "1,39 1,47 1,55 1,63 1,72 1,82 1,92 2,03 2,15 2,27 2,40 2,54 2,68 2,84 3,01 3,19",
    47: "1,39 1,47 1,55 1,64 1,73 1,82 1,93 2,04 2,15 2,27 2,41 2,54 2,69 2,85 3,03 3,22",
    48: "1,39 1,47 1,55 1,64 1,73 1,83 1,93 2,04 2,16 2,28 2,41 2,55 2,71 2,87 3,05 3,24",
    49: "1,39 1,47 1,55 1,64 1,73 1,83 1,94 2,05 2,16 2,29 2,42 2,57 2,72 2,89 3,08 3,27",
    50: "1,39 1,47 1,56 1,64 1,74 1,84 1,94 2,05 2,17 2,30 2,43 2,58 2,74 2,92 3,10 3,31",
    51: "1,40 1,47 1,56 1,65 1,74 1,84 1,94 2,06 2,18 2,31 2,45 2,60 2,76 2,94 3,14 3,34",
    52: "1,40 1,48 1,56 1,65 1,74 1,84 1,95 2,06 2,19 2,32 2,46 2,62 2,79 2,97 3,17 3,39",
    53: "1,40 1,48 1,56 1,65 1,75 1,85 1,96 2,07 2,20 2,34 2,48 2,64 2,82 3,01 3,21 3,43",
    54: "1,40 1,48 1,57 1,66 1,75 1,85 1,96 2,08 2,21 2,36 2,51 2,67 2,85 3,04 3,25 3,48",
    55: "1,40 1,48 1,57 1,66 1,76 1,86 1,98 2,10 2,23 2,38 2,53 2,70 2,88 3,08 3,30 3,54",
    56: "1,41 1,49 1,57 1,67 1,76 1,87 1,99 2,12 2,25 2,40 2,56 2,73 2,92 3,13 3,36 3,61",
    57: "1,41 1,49 1,58 1,67 1,77 1,88 2,00 2,13 2,27 2,42 2,59 2,77 2,97 3,18 3,42 3,68",
    58: "1,41 1,50 1,58 1,68 1,79 1,90 2,02 2,15 2,30 2,45 2,62 2,81 3,01 3,24 3,49 3,77",
    59: "1,42 1,50 1,59 1,69 1,80 1,91 2,04 2,18 2,32 2,49 2,66 2,85 3,07 3,31 3,57 3,87",
    60: "1,42 1,51 1,60 1,70 1,81 1,93 2,06 2,20 2,35 2,52 2,70 2,91 3,13 3,38 3,67 3,98",
    61: "1,43 1,52 1,61 1,72 1,83 1,95 2,08 2,23 2,39 2,56 2,75 2,97 3,20 3,47 3,77",
    62: "1,44 1,53 1,63 1,73 1,85 1,97 2,11 2,26 2,42 2,61 2,81 3,03 3,29 3,57",
    63: "1,45 1,54 1,64 1,75 1,87 2,00 2,14 2,30 2,47 2,66 2,87 3,11 3,38",
    64: "1,46 1,55 1,66 1,77 1,89 2,02 2,17 2,33 2,52 2,72 2,94 3,20",
    65: "1,47 1,57 1,67 1,79 1,92 2,06 2,21 2,38 2,57 2,79 3,03",
    66: "1,48 1,58 1,69 1,81 1,94 2,09 2,25 2,43 2,64 2,87",
    67: "1,50 1,60 1,71 1,84 1,98 2,13 2,30 2,49 2,71",
    68: "1,51 1,62 1,74 1,87 2,01 2,18 2,36 2,56",
    69: "1,53 1,64 1,77 1,90 2,06 2,23 2,42",
    70: "1,55 1,67 1,80 1,94 2,10 2,28",
    71: "1,57 1,69 1,83 1,98 2,15",
    72: "1,59 1,72 1,86 2,03",
    73: "1,62 1,75 1,91",
    74: "1,65 1,79",
}

# --- Table 2 : tarif assurance Décès/PTIA pour 10 000 € (âge -> par durée 9-30) ---
_TARIF_DUREE_DEBUT = 9
_TARIF_ROWS_BRUT: dict[int, str] = {
    12: "110 125 141 156 172 187 203 219 237 254 272 290 308 327 345 364 384 403 424 444 466 489",
    13: "121 136 151 167 182 198 214 232 249 267 285 303 321 340 358 378 397 417 438 460 482 506",
    14: "130 145 161 176 192 208 225 243 261 278 296 315 333 352 371 390 410 431 453 475 499 523",
    15: "138 154 169 185 201 218 235 253 271 289 307 325 344 363 382 402 423 444 466 490 515 541",
    16: "144 160 175 191 208 226 243 261 279 297 315 334 352 372 392 412 434 456 479 504 530 557",
    17: "148 163 179 196 213 231 249 266 284 302 321 340 359 379 399 421 443 466 490 516 543 573",
    18: "149 165 182 199 216 234 252 270 288 306 325 344 364 384 405 427 451 475 501 528 557 588",
    19: "149 166 183 201 218 236 254 272 290 309 328 348 368 389 411 434 458 484 511 540 571 605",
    20: "150 167 185 202 220 237 255 274 292 311 331 351 372 394 417 441 467 494 523 554 588 625",
    21: "152 169 187 204 222 240 258 277 296 315 335 356 378 401 425 450 477 506 537 571 608 648",
    22: "154 171 189 206 224 242 261 280 299 319 340 362 385 409 434 461 490 520 554 591 631 673",
    23: "157 174 191 209 227 246 265 284 304 325 346 369 393 418 445 474 504 538 574 614 657 701",
    24: "159 177 195 213 231 250 269 289 310 331 354 378 403 430 458 489 522 558 598 640 685 732",
    25: "162 179 197 216 235 254 274 294 316 338 362 387 414 442 472 506 542 581 623 668 715 765",
    26: "165 183 201 219 239 258 279 300 323 346 372 398 426 456 490 526 565 607 651 698 748 801",
    27: "168 186 204 224 243 264 285 307 331 356 382 410 440 473 510 549 590 635 682 731 784 839",
    28: "171 189 208 228 248 269 292 315 340 366 394 424 457 493 532 574 618 664 714 766 821 879",
    29: "173 192 211 232 253 275 298 323 349 377 407 440 476 515 556 600 646 696 748 802 860 921",
    30: "175 195 215 236 258 281 306 332 360 390 422 458 497 538 582 628 677 729 784 841 902 965",
    31: "178 198 219 241 264 289 315 343 372 405 440 479 520 564 610 659 711 765 822 882 945 1012",
    32: "181 202 224 247 272 298 325 355 387 423 461 502 546 592 640 692 746 803 863 926 992 1061",
    33: "185 207 230 255 281 308 338 370 405 444 484 528 574 622 673 727 784 844 907 972 1041 1112",
    34: "190 213 238 263 291 320 352 388 426 466 510 555 604 655 709 765 825 887 953 1021 1092 1166",
    35: "196 220 246 273 303 335 370 408 448 491 537 585 636 690 746 806 868 933 1001 1072 1146 1223",
    36: "203 228 256 285 317 352 390 430 473 518 566 617 671 727 786 848 913 981 1051 1125 1202 1281",
    37: "211 238 267 299 334 371 412 454 500 547 598 651 707 766 828 893 960 1031 1104 1181 1260 1341",
    38: "220 249 281 315 353 393 436 481 528 579 632 688 746 808 872 940 1010 1083 1159 1238 1320 1404",
    39: "230 262 296 334 374 416 461 509 559 612 668 726 788 852 919 989 1062 1138 1216 1297 1381 1468",
    40: "243 277 315 355 397 442 489 539 592 647 706 767 831 898 967 1040 1116 1194 1275 1358 1445 1533",
    41: "257 295 335 377 421 468 518 571 626 684 745 809 876 945 1018 1093 1171 1252 1335 1421 1509 1599",
    42: "274 314 356 400 447 497 550 605 663 723 787 853 923 995 1070 1148 1228 1311 1397 1485 1575 1681",
    43: "292 334 378 425 475 527 582 640 700 764 830 899 971 1046 1123 1204 1286 1372 1459 1549 1655 1772",
    44: "312 356 403 452 504 559 616 677 740 806 875 947 1021 1098 1178 1261 1346 1433 1523 1628 1745 1875",
    45: "332 378 428 480 534 592 652 715 781 849 921 995 1072 1152 1234 1319 1406 1495 1601 1717 1847 1990",
    46: "353 402 454 509 566 626 689 754 823 894 968 1045 1125 1207 1291 1378 1467 1572 1688 1817 1961 2121",
    47: "376 427 482 539 599 661 727 795 866 940 1017 1096 1178 1262 1349 1437 1542 1658 1787 1930 2089 2268",
    48: "399 453 510 569 632 697 765 836 910 987 1066 1147 1231 1318 1406 1511 1626 1754 1897 2056 2234 2434",
    49: "422 479 538 600 666 734 804 878 954 1033 1114 1198 1284 1373 1477 1592 1720 1863 2021 2199 2398 2621",
    50: "445 504 566 631 699 770 843 919 998 1079 1163 1249 1337 1441 1556 1684 1826 1984 2161 2360 2583 2833",
    51: "467 529 594 662 733 806 882 960 1041 1125 1211 1299 1403 1518 1645 1787 1945 2122 2320 2542 2792 3071",
    52: "491 555 623 693 767 842 921 1002 1085 1171 1259 1362 1477 1604 1746 1904 2080 2278 2500 2749 3028 3341",
    53: "514 582 652 725 801 879 960 1043 1129 1217 1320 1435 1562 1703 1861 2037 2235 2456 2705 2983 3296 3647",
    54: "538 609 682 757 835 916 999 1085 1172 1276 1390 1517 1658 1816 1992 2189 2411 2659 2937 3249 3599 3990",
    55: "563 636 711 789 870 953 1039 1126 1229 1344 1470 1611 1769 1945 2142 2363 2611 2889 3201 3551 3941 4373",
    56: "588 663 741 822 905 990 1077 1181 1295 1421 1562 1719 1895 2092 2313 2561 2839 3151 3500 3890 4321 4794",
    57: "612 690 771 854 939 1027 1130 1244 1370 1511 1668 1844 2041 2262 2509 2787 3099 3448 3837 4269 4741 5253",
    58: "637 718 801 886 973 1076 1191 1317 1458 1615 1790 1987 2208 2455 2733 3045 3394 3783 4214 4687 5198 5743",
    59: "662 745 830 918 1021 1135 1261 1402 1559 1735 1931 2152 2400 2677 2989 3338 3727 4158 4630 5142 5687 6257",
    60: "687 772 859 962 1077 1203 1344 1501 1676 1873 2094 2342 2619 2931 3280 3669 4100 4573 5084 5629 6200 6786",
    61: "711 798 902 1016 1142 1283 1440 1616 1813 2034 2281 2559 2871 3220 3609 4041 4513 5025 5570 6141 6727 7318",
    62: "735 838 953 1079 1220 1377 1553 1750 1971 2219 2497 2808 3158 3548 3979 4452 4964 5509 6081 6667 7259 7848",
    63: "772 887 1013 1154 1311 1487 1685 1906 2154 2432 2744 3094 3484 3916 4389 4901 5447 6019 6606 7198 7788 8370",
    64: "818 945 1086 1243 1419 1617 1838 2086 2365 2677 3027 3418 3850 4324 4837 5384 5956 6544 7137 7727 8309 8878",
    65: "873 1015 1172 1349 1547 1768 2017 2296 2608 2959 3350 3783 4258 4771 5319 5892 6480 7074 7665 8248 8817 9364",
    66: "941 1099 1276 1474 1696 1945 2224 2537 2888 3280 3714 4189 4703 5252 5826 6415 7010 7602 8186 8756 9304 9823",
    67: "1023 1200 1398 1621 1870 2150 2464 2816 3208 3643 4119 4634 5183 5759 6349 6945 7538 8123 8694 9243 9763 10246",
    68: "1122 1320 1543 1793 2074 2388 2741 3134 3569 4047 4563 5113 5690 6282 6879 7473 8060 8632 9182 9703 10187 10628",
    69: "1240 1463 1714 1995 2310 2664 3058 3494 3972 4490 5042 5620 6213 6811 7407 7995 8568 9120 9642 10127 10569 10964",
    70: "1381 1632 1914 2230 2584 2980 3417 3897 4415 4969 5548 6143 6743 7340 7929 8504 9057 9580 10067 10510 10906 11252",
    71: "1548 1831 2148 2503 2899 3338 3819 4339 4894 5475 6071 6673 7272 7863 8439 8994 9518 10006 10451 10848 11195 11490",
    72: "1734 2052 2409 2807 3247 3730 4253 4810 5393 5992 6596 7198 7791 8370 8927 9454 9944 10390 10789 11137 11434 11681",
    73: "1946 2304 2705 3147 3633 4158 4718 5304 5906 6514 7119 7715 8297 8857 9386 9879 10328 10728 11078 11377 11626 11827",
    74: "2189 2592 3037 3526 4054 4618 5208 5814 6425 7034 7634 8220 8783 9317 9812 10264 10667 11020 11320 11570 11773 11933",
    75: "2465 2915 3407 3940 4508 5103 5713 6329 6943 7548 8138 8706 9243 9743 10198 10605 10960 11263 11515 11719 11881 12004",
    76: "2777 3274 3812 4386 4986 5603 6224 6844 7455 8050 8624 9166 9670 10130 10540 10899 11204 11459 11666 11828 11953 12046",
}


def _build_table(rows_brut: dict[int, str], duree_debut: int, decimal_comma: bool) -> dict[int, dict[int, float]]:
    """Transpose des lignes 'par âge' vers la structure [durée][âge] utilisée par le site."""
    table: dict[int, dict[int, float]] = {}
    for age, ligne in rows_brut.items():
        valeurs = ligne.split()
        for i, brut in enumerate(valeurs):
            duree = duree_debut + i
            valeur = float(brut.replace(",", ".")) if decimal_comma else float(brut)
            table.setdefault(duree, {})[age] = valeur
    return table


COEFFICIENTS_RENTABILITE: dict[int, dict[int, float]] = _build_table(
    _COEF_ROWS_BRUT, _COEF_DUREE_DEBUT, decimal_comma=True
)
TARIFS_ASSURANCE_10000: dict[int, dict[int, float]] = _build_table(
    _TARIF_ROWS_BRUT, _TARIF_DUREE_DEBUT, decimal_comma=False
)


def durees_disponibles() -> list[int]:
    return sorted(COEFFICIENTS_RENTABILITE.keys())


def ages_disponibles(duree: int) -> list[int]:
    return sorted(COEFFICIENTS_RENTABILITE.get(duree, {}).keys())


def durees_disponibles_pour_age(age: int) -> list[int]:
    """Durées pour lesquelles une tontine est souscriptible à cet âge (une tranche de cascade)."""
    return [d for d in durees_disponibles() if age in COEFFICIENTS_RENTABILITE.get(d, {})]


class DonneesManquantesError(Exception):
    pass


def _lookup(table: dict[int, dict[int, float]], duree: int, age: int) -> float:
    par_duree = table.get(duree)
    if par_duree is None or age not in par_duree:
        raise DonneesManquantesError(
            f"Pas de donnée pour durée={duree} ans, âge={age} ans."
        )
    return par_duree[age]


# Fiscalité de sortie (art. 125-0 A CGI, primes post 27/09/2017), voir /fiscalite
# pour le détail et l'arbitrage IR barème vs PFNL. Constantes reprises ici pour
# donner une estimation indicative directement dans la simulation de rentabilité.
ABATTEMENT_SEUL = 4600
ABATTEMENT_COUPLE = 9200
SEUIL_ENCOURS_PFNL = 150000
TAUX_PFNL_BAS = 0.075
TAUX_PFNL_HAUT = 0.128


def calculer_rentabilite(montant: float, age: int, duree: int) -> dict:
    if montant <= 0:
        raise ValueError("Le montant doit être positif.")

    coefficient = _lookup(COEFFICIENTS_RENTABILITE, duree, age)
    tarif_10000 = _lookup(TARIFS_ASSURANCE_10000, duree, age)

    repartition_potentielle = montant * coefficient
    cout_assurance = tarif_10000 * (montant / 10000)
    gain_potentiel = repartition_potentielle - montant
    investissement_total = montant + cout_assurance
    benefices = repartition_potentielle - investissement_total
    mensuel = repartition_potentielle / 12

    return {
        "montant": montant,
        "age": age,
        "duree": duree,
        "coefficient": coefficient,
        "repartition_potentielle": round(repartition_potentielle, 2),
        "mensuel": round(mensuel, 2),
        "gain_potentiel": round(gain_potentiel, 2),
        "cout_assurance": round(cout_assurance, 2),
        "investissement_total": round(investissement_total, 2),
        "benefices": round(benefices, 2),
        "donnees_exemple": DONNEES_EXEMPLE,
    }


def calculer_cascade(
    age: int,
    tranches: list[dict],
    situation: str = "seul",
    encours_total: float = 0,
) -> dict:
    """Cascade = plusieurs tontines de durées différentes souscrites en même temps par le même client.

    La fiscalité estimée par tranche est indicative : PFNL forfaitaire (7,5 % ou
    12,8 % selon encours), abattement annuel appliqué par tranche car chaque
    tranche se dénoue une année différente. Pour l'arbitrage complet avec le
    barème progressif selon la TMI du client, voir /fiscalite.
    """
    if not tranches:
        raise ValueError("Au moins une tranche est requise.")

    abattement = ABATTEMENT_COUPLE if situation == "couple" else ABATTEMENT_SEUL
    taux_pfnl = TAUX_PFNL_HAUT if encours_total > SEUIL_ENCOURS_PFNL else TAUX_PFNL_BAS

    annee_placement = date.today().year
    resultats = []
    for t in tranches:
        montant = float(t["montant"])
        duree = int(t["duree"])
        r = calculer_rentabilite(montant, age, duree)
        r["age_perception"] = age + duree
        r["annee_placement"] = annee_placement
        r["annee_perception"] = annee_placement + duree
        fiscalite_estimee = max(0.0, r["gain_potentiel"] - abattement) * taux_pfnl
        r["fiscalite_estimee"] = round(fiscalite_estimee, 2)
        r["benefices_net"] = round(r["benefices"] - fiscalite_estimee, 2)
        resultats.append(r)

    resultats.sort(key=lambda r: r["duree"])

    def total(cle: str) -> float:
        return round(sum(r[cle] for r in resultats), 2)

    return {
        "age": age,
        "situation": situation,
        "encours_total": encours_total,
        "taux_pfnl_applique": taux_pfnl,
        "abattement_applique": abattement,
        "annee_placement": annee_placement,
        "tranches": resultats,
        "total_montant": total("montant"),
        "total_repartition_potentielle": total("repartition_potentielle"),
        "total_mensuel": total("mensuel"),
        "total_gain_potentiel": total("gain_potentiel"),
        "total_cout_assurance": total("cout_assurance"),
        "total_investissement_total": total("investissement_total"),
        "total_benefices": total("benefices"),
        "total_fiscalite_estimee": total("fiscalite_estimee"),
        "total_benefices_net": total("benefices_net"),
        "cascade": len(resultats) > 1,
        "donnees_exemple": DONNEES_EXEMPLE,
    }
