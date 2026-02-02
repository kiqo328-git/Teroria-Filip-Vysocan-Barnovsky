# Terroria 🌍

Terroria je 2D procedurálne generovaná sandbox hra inšpirovaná Terrariou, napísaná v jazyku Python s využitím knižnice Pygame. Projekt sa zameriava na vlastnú implementáciu generovania terénu, fyziky a chunk systému.

![Game Screenshot](screenshot.png) *(Nezabudni pridať screenshot hry do repozitára)*

## 🎮 Vlastnosti

*   **Procedurálne generovanie:** Nekonečný svet využívajúci Value Noise, FBM pre jaskyne a smoothstep interpoláciu.
*   **Optimalizácia:** Výpočtovo náročné funkcie (generovanie šumu) sú akcelerované pomocou **Numba (@njit)**.
*   **Chunk Systém:** Dynamické načítavanie a ukladanie sveta pre plynulý beh.
*   **Fyzika:** Vlastná implementácia gravitácie, kolízií (AABB) a pohybu postavy.
*   **Stavanie a ťaženie:** Možnosť ničiť bloky a stavať nové (vrátane vegetácie a pozadia).
*   **Modulárna postava:** Systém skladania tela (hlava, trup, končatiny) pre jednoduchú animáciu.

## 🛠️ Technológie

*   **Jazyk:** Python 3.x
*   **Engine:** Pygame
*   **Matematika & Polia:** NumPy
*   **Kompilácia:** Numba (JIT compiler pre zrýchlenie Pythonu)

## 🚀 Inštalácia a Spustenie

1.  **Naklonuj si repozitár:**
    ```bash
    git clone https://github.com/tvoje-meno/terroria.git
    cd terroria
    ```

2.  **Nainštaluj závislosti:**
    Odporúčame použiť virtuálne prostredie (`venv`).
    ```bash
    pip install -r requirements.txt
    ```
    *Ak nemáš `requirements.txt`, nainštaluj manuálne:*
    ```bash
    pip install pygame numpy numba
    ```

3.  **Spusti hru:**
    ```bash
    python main.py
    ```

## 🕹️ Ovládanie

*   **W / A / S / D**: Pohyb postavy
*   **Medzerník**: Skok
*   **Ľavé tlačidlo myši**: Ťaženie blokov
*   **Pravé tlačidlo myši**: Pokladanie blokov
