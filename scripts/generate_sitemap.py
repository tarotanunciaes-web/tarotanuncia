
import os
import re
import json
import html
import urllib.parse
import urllib.request
import unicodedata
from pathlib import Path
import xml.etree.ElementTree as ET


# ==========================================
# TAROTANUNCIA
# GENERADOR DE FICHAS Y SITEMAP
# ==========================================

BASE = "https://tarotanuncia.es/"

API = os.environ["SUPABASE_URL"].rstrip("/")
KEY = os.environ["SUPABASE_ANON_KEY"]

LOGO = "/file_000000003c088210be49f3122608d83d.png"

PROFILE_DIR = Path("profesionales")
AD_DIR = Path("anuncios")
PROVINCE_DIR = Path("tarotistas")

PROFILE_DIR.mkdir(exist_ok=True)
AD_DIR.mkdir(exist_ok=True)
PROVINCE_DIR.mkdir(exist_ok=True)


# ==========================================
# FUNCIONES
# ==========================================

def fetch(table, params):
    results = []
    query = urllib.parse.urlencode(params)

    for start in range(0, 100000, 1000):
        request = urllib.request.Request(
            f"{API}/rest/v1/{table}?{query}",
            headers={
                "apikey": KEY,
                "Authorization": "Bearer " + KEY,
                "Range-Unit": "items",
                "Range": f"{start}-{start + 999}",
            },
        )

        with urllib.request.urlopen(
            request, timeout=45
        ) as response:
            batch = json.load(response)

        if not isinstance(batch, list):
            raise RuntimeError(
                f"Respuesta inválida: {table}"
            )

        results.extend(batch)

        if len(batch) < 1000:
            return results

    raise RuntimeError(
        "Se ha superado el límite de resultados"
    )


def val(data, key):
    return str(data.get(key) or "").strip()


def esc(value):
    return html.escape(str(value or ""), quote=True)


def uid(value):
    return bool(
        re.fullmatch(
            r"[0-9a-fA-F-]{36}",
            str(value)
        )
    )


def image_url(value):
    value = str(value or "").strip()
    parsed = urllib.parse.urlparse(value)

    if parsed.scheme == "https" and parsed.netloc:
        return value

    return ""


def phone(value):
    return re.sub(
        r"[^+0-9]",
        "",
        str(value or "")
    )


def wa_phone(value):
    return re.sub(
        r"\D",
        "",
        str(value or "")
    )


def summary(value, limit=155):
    return " ".join(
        str(value or "").split()
    )[:limit]


def categories(data):
    value = data.get("categories") or []

    if isinstance(value, list):
        return [
            str(x)
            for x in value
            if x
        ]

    return [
        x.strip()
        for x in str(value).split(",")
        if x.strip()
    ]


def schema(data):
    return json.dumps(
        data,
        ensure_ascii=False
    ).replace("<", "\\u003c")


def short_description(value, limit=110):
    text = " ".join(str(value or "").split())

    if len(text) <= limit:
        return text

    shortened = text[:limit].rsplit(" ", 1)[0]

    return shortened.rstrip(".,;: ") + "…"


# ==========================================
# DISEÑO
# ==========================================

CSS = """
:root {
    --gold: #d89400;
    --gold2: #efb326;
    --purple: #702d6b;
    --ink: #171526;
    --cream: #fffaf1;
    --line: #eadfce;
}

* {
    box-sizing: border-box;
}

html {
    -webkit-text-size-adjust: 100%;
    text-size-adjust: 100%;
    overflow-x: clip;
}

body {
    margin: 0;
    background: #fbfaf6;
    color: var(--ink);
    font-family: Arial, system-ui, sans-serif;
    font-size: 14px;
    line-height: 1.5;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
}

a {
    color: var(--purple);
}

button {
    font: inherit;
}

/* CABECERA */

header {
    background: #fffcf6;
    border-bottom: 1px solid #eee4d6;
    position: sticky;
    top: 0;
    z-index: 100;
}

.top {
    width: min(1240px, calc(100% - 30px));
    min-height: 66px;
    margin: auto;
    display: flex;
    align-items: center;
    gap: 15px;
}

.brand {
    display: flex;
    align-items: center;
    gap: 9px;
    text-decoration: none;
    color: var(--ink);
    margin-right: auto;
}

.logo {
    width: 42px;
    height: 42px;
    object-fit: contain;
}

.brand-name {
    font: 700 24px Georgia, serif;
}

.brand-name span {
    color: #b97800;
}

.tagline {
    display: block;
    font-size: 8px;
    letter-spacing: 1.1px;
    color: #70656d;
}

.desktop-nav {
    display: flex;
    gap: 18px;
    align-items: center;
}

.desktop-nav a {
    font-size: 12px;
    font-weight: 700;
    color: #302833;
    text-decoration: none;
}

.desktop-nav a:hover {
    color: #b97800;
}

.menu-button {
    display: none;
    border: 0;
    background: transparent;
    font-weight: 800;
    cursor: pointer;
    color: #302833;
}

/* MENÚ MÓVIL */

.overlay[hidden],
.drawer[hidden] {
    display: none !important;
}

.overlay {
    position: fixed;
    inset: 0;
    z-index: 150;
    background: rgba(15,10,20,.45);
}

.drawer {
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
    z-index: 151;
    width: min(280px,85vw);
    background: linear-gradient(
        180deg,
        #fffdf9,
        #fbf5eb
    );
    box-shadow: 8px 0 30px #0002;
    padding: 17px 13px;
    overflow: auto;
}

.drawer-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--line);
    padding-bottom: 12px;
    margin-bottom: 12px;
}

.drawer-head strong {
    font: 800 21px Georgia, serif;
}

.drawer-close {
    background: white;
    border: 1px solid var(--line);
    border-radius: 9px;
    font-size: 24px;
    width: 37px;
    height: 37px;
    cursor: pointer;
}

.drawer nav {
    display: grid;
    gap: 6px;
}

.drawer nav a {
    display: block;
    padding: 12px;
    border-radius: 11px;
    background: white;
    color: #302833;
    text-decoration: none;
    font-weight: 700;
    font-size: 14px;
}

/* CONTENIDO */

.hero {
    text-align: center;
    padding: 20px 15px 8px;
}

.hero h1 {
    font: 800 23px/1.25 Georgia, serif;
    margin: 0 0 7px;
}

.hero p {
    margin: 0;
    color: #756a70;
    font-size: 12px;
}

main {
    flex: 1;
    width: min(850px,calc(100% - 24px));
    margin: 12px auto 30px;
}

.panel {
    background: white;
    border: 1px solid #e6d8c2;
    border-top: 4px solid #d5ae55;
    border-radius: 17px;
    padding: 22px;
    box-shadow: 0 5px 16px #32231412;
    overflow: hidden;
}

.panel h1 {
    font: 800 26px/1.25 Georgia, serif;
    margin: 0 0 10px;
    overflow-wrap: anywhere;
}

h2 {
    font: 800 20px Georgia, serif;
    margin: 22px 0 11px;
}

h3 {
    font: 800 16px Georgia, serif;
    margin: 0 0 7px;
    overflow-wrap: anywhere;
}

.meta {
    font-size: 13px;
    color: #70666c;
    margin: 8px 0 13px;
}

/* FOTOGRAFÍAS */

.photo-box {
    background: #fbf7f0;
    border: 1px solid #e3d4bc;
    border-radius: 14px;
    padding: 8px;
    margin-bottom: 15px;
    text-align: center;
}

.photo {
    display: block;
    width: 100%;
    max-height: 290px;
    object-fit: contain;
    margin: auto;
}

.intro {
    text-align: center;
}

.avatar {
    display: block;
    width: 108px;
    height: 108px;
    object-fit: contain;
    border-radius: 50%;
    border: 2px solid #ead5a3;
    background: var(--cream);
    padding: 8px;
    margin: 0 auto 13px;
}

.avatar-empty {
    display: grid;
    place-items: center;
    font-size: 44px;
    color: #b78b39;
}

/* DESCRIPCIONES */

.description {
    font-size: 14px;
    line-height: 1.55;
    color: #443b43;
    white-space: pre-line;
    overflow-wrap: anywhere;
    margin: 12px 0;
}

/* ESPECIALIDADES */

.tags {
    display: flex;
    flex-wrap: wrap;
    gap: 7px;
    justify-content: center;
}

.tag {
    background: #f7eaf5;
    color: var(--purple);
    border-radius: 99px;
    padding: 5px 10px;
    font-size: 12px;
}

/* BOTONES */

.buttons {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    justify-content: center;
    margin: 17px 0;
}

.btn {
    display: inline-flex;
    justify-content: center;
    align-items: center;
    text-align: center;
    min-height: 43px;
    padding: 10px 15px;
    border-radius: 12px;
    background: linear-gradient(
        135deg,
        var(--gold2),
        var(--gold)
    );
    color: white;
    font-size: 13px;
    font-weight: 800;
    text-decoration: none;
}

.btn.secondary {
    background: #fffaf1;
    color: #79550b;
    border: 1px solid #d5a43c;
}

.btn:hover {
    filter: brightness(.97);
}

/* TARJETAS COMPACTAS */

.ad-grid {
    display: grid;
    grid-template-columns: repeat(2,minmax(0,1fr));
    gap: 12px;
}

.ad-card {
    background: #fffdf9;
    border: 1px solid var(--line);
    border-radius: 13px;
    padding: 15px;
    min-width: 0;
    display: flex;
    flex-direction: column;
}

.ad-card h3 {
    font-size: 16px;
    line-height: 1.3;
    margin-bottom: 8px;
}

.ad-card p {
    font-size: 13px;
    color: #625961;
    line-height: 1.5;
    margin: 0 0 14px;
    overflow-wrap: anywhere;
}

.ad-view-button {
    display: block;
    margin-top: auto;
    padding: 10px 14px;
    border-radius: 10px;
    background: #fff4da;
    border: 1px solid #d5a43c;
    color: #79550b;
    font-size: 13px;
    font-weight: 700;
    text-align: center;
    text-decoration: none;
}

.ad-view-button:hover {
    background: #fce8ba;
}

/* ENLACES INFERIORES */

.links {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 8px;
    margin-top: 17px;
    padding-top: 14px;
    border-top: 1px solid var(--line);
}

.links a {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 9px 11px;
    border: 1px solid var(--line);
    border-radius: 10px;
    background: var(--cream);
    color: #785010;
    font-size: 12px;
    font-weight: 700;
    text-decoration: none;
}

/* PIE DE PÁGINA */

footer {
    background: #fff7eb;
    border-top: 1px solid #eadcc3;
    padding: 20px 14px;
    text-align: center;
    color: #786d71;
    font-size: 12px;
}

footer strong {
    display: block;
    color: #b97800;
    font: 800 21px Georgia, serif;
    margin-bottom: 6px;
}

footer a {
    color: #785010;
}

/* RESPONSIVE */

@media (max-width: 900px) {
    .desktop-nav {
        display: none;
    }

    .menu-button {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        padding: 10px 5px;
        font-size: 13px;
    }
}

@media (max-width: 600px) {
    .top {
        min-height: 64px;
    }

    .logo {
        width: 37px;
        height: 37px;
    }

    .brand-name {
        font-size: 21px;
    }

    .tagline {
        font-size: 7px;
    }

    .hero {
        padding: 17px 12px 7px;
    }

    .hero h1 {
        font-size: 21px;
    }

    main {
        width: calc(100% - 22px);
        margin: 11px auto 26px;
    }

    .panel {
        padding: 15px;
        border-radius: 15px;
    }

    .panel h1 {
        font-size: 22px;
        line-height: 1.25;
    }

    h2 {
        font-size: 18px;
    }

    .description {
        font-size: 13px;
        line-height: 1.5;
        margin: 11px 0;
    }

    .photo {
        max-height: 270px;
    }

    .photo-box {
        padding: 7px;
        margin-bottom: 14px;
    }

    .buttons .btn {
        width: 100%;
    }

    .ad-grid {
        grid-template-columns: 1fr;
    }

    .ad-card {
        padding: 13px;
    }

    .ad-card h3 {
        font-size: 15px;
    }

    .ad-card p {
        font-size: 12px;
    }

    .links a {
        flex: 1 1 125px;
        font-size: 11px;
    }

    footer {
        padding: 18px 12px;
        font-size: 11px;
    }
}
"""


# ==========================================
# CABECERA Y MENÚ
# ==========================================

def header():
    return f"""
<header>
  <div class="top">
    <a class="brand" href="/">
      <img class="logo"
           src="{esc(LOGO)}"
           alt="Logo de TarotAnuncia"
           onerror="this.style.display='none'">

      <span>
        <span class="brand-name">
          Tarot<span>Anuncia</span>
        </span>
        <small class="tagline">
          TAROTISTAS CERCA DE TI
        </small>
      </span>
    </a>

    <nav class="desktop-nav"
         aria-label="Navegación">
      <a href="/">Inicio</a>
      <a href="/anuncios.html">Anuncios</a>
      <a href="/tarotistas.html">Tarotistas</a>
      <a href="/tienda-esoterica.html">
        Tienda esotérica
      </a>
    </nav>

    <button class="menu-button"
            id="ta-menu-button"
            type="button"
            aria-label="Abrir menú"
            aria-expanded="false"
            aria-controls="ta-drawer"
            onclick="taMenu(true)">
      ☰ MENÚ
    </button>
  </div>
</header>

<div class="overlay"
     id="ta-overlay"
     onclick="taMenu(false)"
     hidden></div>

<aside class="drawer"
       id="ta-drawer"
       aria-label="Menú móvil"
       hidden>

  <div class="drawer-head">
    <strong>TarotAnuncia</strong>

    <button class="drawer-close"
            type="button"
            aria-label="Cerrar menú"
            onclick="taMenu(false)">×</button>
  </div>

  <nav>
    <a href="/">Inicio</a>
    <a href="/anuncios.html">Anuncios</a>
    <a href="/tarotistas.html">Tarotistas</a>
    <a href="/tienda-esoterica.html">
      Tienda esotérica
    </a>
  </nav>
</aside>
"""


MENU_JS = """
<script>
function taMenu(open) {
    const drawer = document.getElementById(
        "ta-drawer"
    );

    const overlay = document.getElementById(
        "ta-overlay"
    );

    const button = document.getElementById(
        "ta-menu-button"
    );

    drawer.hidden = !open;
    overlay.hidden = !open;

    button.setAttribute(
        "aria-expanded",
        String(open)
    );

    document.body.style.overflow =
        open ? "hidden" : "";
}

document.addEventListener(
    "keydown",
    function(event) {
        if (event.key === "Escape") {
            taMenu(false);
        }
    }
);
</script>
"""


def footer():
    return """
<footer>
  <strong>TarotAnuncia</strong>
  Encuentra profesionales del tarot en toda España

  <p>
    <a href="/">Inicio</a> ·
    <a href="/anuncios.html">Anuncios</a> ·
    <a href="/tarotistas.html">Tarotistas</a>
  </p>
</footer>
"""


def document(
    title,
    description,
    canonical,
    data,
    body
):
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport"
      content="width=device-width,initial-scale=1">

<title>{esc(title)}</title>

<meta name="description"
      content="{esc(description)}">

<meta name="robots"
      content="index,follow,max-image-preview:large">

<link rel="canonical"
      href="{esc(canonical)}">

<script type="application/ld+json">
{schema(data)}
</script>

<style>
{CSS}
</style>
</head>

<body>
{header()}
{body}
{footer()}
{MENU_JS}
</body>
</html>
"""


# ==========================================
# DATOS DE SUPABASE
# ==========================================

profiles = fetch(
    "ta_professional_profiles",
    {
        "select": "*",
        "is_public": "eq.true"
    }
)

ads = fetch(
    "tarotist_ads",
    {
        "select": "*",
        "status": "eq.approved"
    }
)

people = {}

for ad in ads:
    owner = val(ad, "owner_id")

    if uid(owner):
        people.setdefault(
            owner,
            {
                "profile": None,
                "ads": []
            }
        )["ads"].append(ad)

for profile in profiles:
    owner = val(profile, "owner_id")

    if uid(owner):
        people.setdefault(
            owner,
            {
                "profile": None,
                "ads": []
            }
        )["profile"] = profile


# ==========================================
# PERFILES PROFESIONALES
# ==========================================

profile_links = []

for owner, data in sorted(people.items()):

    profile = data["profile"] or (
        data["ads"][0]
        if data["ads"]
        else {}
    )

    name = (
        val(profile, "display_name")
        or "Profesional del tarot"
    )

    description = (
        val(profile, "description")
        or next(
            (
                val(ad, "description")
                for ad in data["ads"]
                if val(ad, "description")
            ),
            "Consulta este perfil en TarotAnuncia."
        )
    )

    # Se mantienen localidad y provincia,
    # aunque tengan el mismo nombre.
    location = ", ".join(
        x
        for x in (
            val(profile, "city"),
            val(profile, "province")
        )
        if x
    )

    photo = image_url(
        val(profile, "profile_photo_url")
    )

    if not photo:
        photo = next(
            (
                img
                for ad in data["ads"]
                if (
                    img := image_url(
                        val(ad, "profile_photo_url")
                    )
                )
            ),
            ""
        )

    url = (
        BASE
        + "profesionales/"
        + owner
        + ".html"
    )

    title = (
        f"{name} | Tarotista en "
        f"{location or 'España'} "
        f"| TarotAnuncia"
    )

    meta = summary(
        f"{name}. {description}"
    )

    if photo:
        avatar = (
            f'<img class="avatar" '
            f'src="{esc(photo)}" '
            f'alt="Foto de {esc(name)}">'
        )
    else:
        avatar = (
            '<div class="avatar avatar-empty">'
            '✦'
            '</div>'
        )

    tags = "".join(
        f'<span class="tag">{esc(x)}</span>'
        for x in categories(profile)[:8]
    )

    buttons = []

    number = phone(
        val(profile, "phone")
    )

    whatsapp = wa_phone(
        val(profile, "whatsapp")
    )

    if number:
        buttons.append(
            f'<a class="btn" '
            f'href="tel:{esc(number)}">'
            'Llamar al profesional'
            '</a>'
        )

    if whatsapp:
        buttons.append(
            f'<a class="btn secondary" '
            f'href="https://wa.me/{esc(whatsapp)}">'
            'Contactar por WhatsApp'
            '</a>'
        )

    # TARJETAS COMPACTAS CON BOTÓN
    ad_cards = []

    for ad in data["ads"]:

        ad_id = val(ad, "id")

        if not uid(ad_id):
            continue

        ad_title = (
            val(ad, "title")
            or "Consulta de tarot"
        )

        ad_description = short_description(
            val(ad, "description"),
            110
        )

        ad_cards.append(f"""
        <article class="ad-card">
          <h3>{esc(ad_title)}</h3>

          <p>{esc(ad_description)}</p>

          <a class="ad-view-button"
             href="/anuncios/{esc(ad_id)}.html">
            Ver anuncio
          </a>
        </article>
        """)

    ad_section = ""

    if ad_cards:
        ad_section = (
            "<h2>Sus anuncios</h2>"
            '<div class="ad-grid">'
            + "".join(ad_cards)
            + "</div>"
        )

    structured = {
        "@context": "https://schema.org",
        "@type": "ProfilePage",
        "url": url,
        "name": name,
        "description": meta,
        "mainEntity": {
            "@type": "Person",
            "name": name,
            "description": description[:400]
        }
    }

    body = f"""
<section class="hero">
  <h1>Perfil profesional</h1>
  <p>
    Conoce a este profesional en TarotAnuncia
  </p>
</section>

<main>
  <article class="panel">

    <div class="intro">
      {avatar}

      <h1>{esc(name)}</h1>

      <p class="meta">
        {esc(location or "España")}
      </p>

      <div class="tags">
        {tags}
      </div>
    </div>

    <h2>Sobre este profesional</h2>

    <div class="description">
      {esc(description)}
    </div>

    <div class="buttons">
      {''.join(buttons)}
    </div>

    {ad_section}

    <nav class="links"
         aria-label="Más información">

      <a href="/tarotistas.html?perfil={esc(owner)}">
        Ver ficha completa y valoraciones
      </a>

      <a href="/tarotistas.html">
        Más profesionales
      </a>

      <a href="/anuncios.html">
        Ver anuncios
      </a>

    </nav>

  </article>
</main>
"""

    page = document(
        title,
        meta,
        url,
        structured,
        body
    )

    (
        PROFILE_DIR
        / (owner + ".html")
    ).write_text(
        page,
        encoding="utf-8"
    )

    profile_links.append(url)


# ==========================================
# ANUNCIOS INDIVIDUALES
# ==========================================

ad_links = []

for ad in ads:

    ad_id = val(ad, "id")

    if not uid(ad_id):
        continue

    title = (
        val(ad, "title")
        or "Consulta de tarot"
    )

    name = (
        val(ad, "display_name")
        or "Profesional del tarot"
    )

    description = (
        val(ad, "description")
        or "Descubre este anuncio en TarotAnuncia."
    )

    url = (
        BASE
        + "anuncios/"
        + ad_id
        + ".html"
    )

    contact_url = (
        BASE
        + "anuncios.html?anuncio="
        + urllib.parse.quote(ad_id)
    )

    photo = image_url(
        val(ad, "profile_photo_url")
    )

    if not photo:
        photos = (
            ad.get("photo_urls")
            or []
        )

        if isinstance(photos, list):
            photo = next(
                (
                    img
                    for item in photos
                    if (
                        img := image_url(item)
                    )
                ),
                ""
            )

    image_html = ""

    if photo:
        image_html = f"""
        <div class="photo-box">
          <img class="photo"
               src="{esc(photo)}"
               alt="{esc(title)}"
               loading="eager">
        </div>
        """

    owner = val(
        ad,
        "owner_id"
    )

    profile_link = ""

    if (
        uid(owner)
        and owner in people
    ):
        profile_link = (
            f'<a href="/profesionales/'
            f'{esc(owner)}.html">'
            'Ver perfil profesional'
            '</a>'
        )

    city = val(ad, "city")
    province = val(ad, "province")

    location = ", ".join(
        x
        for x in (
            city,
            province
        )
        if x
    )

    meta = summary(description)

    structured = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "url": url,
        "name": title,
        "description": meta
    }

    body = f"""
<section class="hero">
  <h1>Anuncios de tarot</h1>
  <p>
    Encuentra profesionales y contacta directamente
  </p>
</section>

<main>
  <article class="panel">

    {image_html}

    <h1>{esc(title)}</h1>

    <p class="meta">
      <strong>{esc(name)}</strong>
      {(" · " + esc(location)) if location else ""}
    </p>

    <div class="description">
      {esc(description)}
    </div>

    <div class="buttons">
      <a class="btn"
         href="{esc(contact_url)}">
        Ver anuncio completo y contactar
      </a>
    </div>

    <nav class="links"
         aria-label="Más opciones">

      {profile_link}

      <a href="/anuncios.html">
        Más anuncios
      </a>

      <a href="/tarotistas.html">
        Explorar profesionales
      </a>

    </nav>

  </article>
</main>
"""

    page = document(
        title + " | TarotAnuncia",
        meta,
        url,
        structured,
        body
    )

    (
        AD_DIR
        / (ad_id + ".html")
    ).write_text(
        page,
        encoding="utf-8"
    )

    ad_links.append(url)


# ==========================================
# LIMPIEZA DE FICHAS ANTIGUAS
# ==========================================

def clean_old(directory, urls):

    valid = {
        url.rsplit("/", 1)[-1]
        for url in urls
    }

    for file in directory.glob("*.html"):

        if (
            file.name not in valid
            and re.fullmatch(
                r"[0-9a-fA-F-]{36}\.html",
                file.name
            )
        ):
            file.unlink()


clean_old(
    PROFILE_DIR,
    profile_links
)

clean_old(
    AD_DIR,
    ad_links
)



# ==========================================
# PÁGINAS SEO POR PROVINCIA
# Solo anuncios aprobados, agrupados por profesional
# ==========================================

def province_slug(name):
    normalized = unicodedata.normalize("NFKD", name)
    normalized = "".join(
        ch for ch in normalized if not unicodedata.combining(ch)
    ).lower()
    normalized = re.sub(r"[^a-z0-9]+", "-", normalized).strip("-")
    return normalized


province_groups = {}
for ad in ads:
    province = val(ad, "province")
    owner = val(ad, "owner_id")
    ad_id = val(ad, "id")
    if not province or not uid(owner) or not uid(ad_id):
        continue
    key = province.casefold()
    group = province_groups.setdefault(
        key, {"name": province, "owners": {}}
    )
    group["owners"].setdefault(owner, []).append(ad)

province_links = []
province_files = set()
used_slugs = set()

# Diseño de las fichas del directorio tarotistas.html, aislado para no
# modificar el aspecto de las fichas individuales ni de los anuncios.
PROVINCE_CARD_CSS = """
<style>
.ta-prov-wrap{width:min(1240px,calc(100% - 32px));margin:18px auto 36px}
.ta-prov-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:24px;align-items:stretch}
.ta-prov-card{background:linear-gradient(180deg,#fffdf9,#fff);border:1px solid #e2d2b8;border-top:3px solid #d5ae55;border-radius:20px;box-shadow:0 8px 24px rgba(58,39,26,.08);padding:15px 13px 16px;text-align:center;display:flex;flex-direction:column;align-items:center;min-width:0}
.ta-prov-photo{width:126px;height:126px;border-radius:50%;border:3px solid #ead5a3;background:#fbf7f0;overflow:hidden;margin:0 auto 13px;display:flex;align-items:center;justify-content:center;box-shadow:0 4px 14px rgba(112,45,107,.10)}
.ta-prov-photo img{width:100%;height:100%;object-fit:contain}
.ta-prov-name{font:800 21px Georgia,serif;color:#241a28;margin:3px 0 7px;overflow-wrap:anywhere}
.ta-prov-location{font-size:12px;color:#71666d;line-height:1.4;margin-bottom:9px}
.ta-prov-tags{display:flex;justify-content:center;flex-wrap:wrap;gap:5px;margin:2px 0 11px}
.ta-prov-tags span{font-size:9px;padding:4px 7px;background:#f7eaf5;border:1px solid #ecd8e9;color:#702d6b;border-radius:999px;font-weight:700}
.ta-prov-count{width:100%;padding-top:10px;border-top:1px solid #eee3d2;color:#776b70;font-size:11px;margin-top:auto;margin-bottom:10px}
.ta-prov-view{display:block;width:100%;min-height:42px;background:linear-gradient(135deg,#fffaf0,#fff5dc);border:1px solid #d4ae55;border-radius:10px;color:#704f0b;padding:10px 12px;font-size:13px;font-weight:900;text-align:center;text-decoration:none}
.ta-prov-ad-links{display:flex;flex-direction:column;align-items:center;justify-content:flex-start;gap:8px;margin-top:11px;font-size:11px;width:100%;min-height:66px}
.ta-prov-ad-links a{display:flex;align-items:center;justify-content:center;width:100%;min-height:38px;padding:9px 10px;box-sizing:border-box;border:1px solid #dfc990;border-radius:10px;background:#fffaf0;color:#64491c;text-decoration:none;font-weight:700;line-height:1.35;overflow-wrap:anywhere;text-align:center;transition:background .15s,border-color .15s}.ta-prov-ad-links a:hover,.ta-prov-ad-links a:focus-visible{background:#f9eed5;border-color:#c9a54e}.ta-prov-ad-links a:focus-visible{outline:2px solid #8d6b2c;outline-offset:2px}
.ta-prov-hero{max-width:950px;margin:18px auto 14px;padding:24px 18px 18px;text-align:center;background:linear-gradient(180deg,#fffdf8,#fbf7f1);border:1px solid #eee2cf;border-radius:20px}.ta-prov-hero h1{margin:0 0 10px;font-size:clamp(26px,4vw,39px);line-height:1.18}.ta-prov-hero p{max-width:680px;margin:0 auto;color:#655c62;font-size:15px;line-height:1.6}.ta-prov-hero .ta-prov-note{margin-top:9px;color:#806536;font-size:13px}.ta-prov-ad-links{min-height:110px}
@media(max-width:900px){.ta-prov-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}}
@media(max-width:700px){.ta-prov-wrap{width:calc(100% - 22px)}.ta-prov-card{padding:13px 8px 12px;border-radius:16px}.ta-prov-photo{width:90px;height:90px;margin-bottom:10px}.ta-prov-name{font-size:16px}.ta-prov-location{font-size:9px}.ta-prov-tags span{font-size:8px;padding:3px 5px}.ta-prov-count{font-size:9px}.ta-prov-ad-links{min-height:86px}.ta-prov-view{font-size:10px;min-height:36px;padding:7px}}
</style>
"""

for group in sorted(province_groups.values(), key=lambda g: g["name"].casefold()):
    province = group["name"]
    slug = province_slug(province)
    if not slug or slug in used_slugs:
        raise RuntimeError(f"Provincia con identificador duplicado o inválido: {province}")
    used_slugs.add(slug)

    url = BASE + "tarotistas/" + slug + ".html"
    cards = []
    for owner, owner_ads in sorted(group["owners"].items()):
        profile = people.get(owner, {}).get("profile") or owner_ads[0]
        name = val(profile, "display_name") or val(owner_ads[0], "display_name") or "Profesional del tarot"
        city = val(profile, "city") or val(owner_ads[0], "city")
        modality = val(profile, "modality") or val(owner_ads[0], "modality")
        location = ", ".join(x for x in (city, province) if x)
        profile_url = "/tarotistas.html?perfil=" + urllib.parse.quote(owner)
        tags = categories(profile)
        if not tags:
            tags = list(dict.fromkeys(
                category for ad in owner_ads for category in categories(ad)
            ))
        tags_html = "".join(f"<span>{esc(tag)}</span>" for tag in tags[:3])
        # Igual que tarotistas.html: foto, avatar o logo del profesional.
        # Si no existe, mostrar el logo oficial de TarotAnuncia.
        photo = next((image_url(val(item, field))
                      for item in [profile] + owner_ads
                      for field in ("profile_photo_url", "avatar_url", "logo_url", "photo_url")
                      if image_url(val(item, field))), "") or LOGO
        ad_links_html = "".join(
            f'<a href="/anuncios/{esc(val(ad, "id"))}.html">{esc(val(ad, "title") or "Ver anuncio")}</a>'
            for ad in owner_ads
        )
        count = len(owner_ads)
        cards.append(
            '<article class="ta-prov-card">'
            f'<div class="ta-prov-photo"><img src="{esc(photo)}" alt="{esc(name)}" loading="lazy"></div>'
            f'<h2 class="ta-prov-name">{esc(name)}</h2>'
            f'<div class="ta-prov-location">{esc(location)}'
            + (f' · {esc(modality)}' if modality else '') + '</div>'
            f'<div class="ta-prov-tags">{tags_html}</div>'
            f'<div class="ta-prov-count">{count} {"anuncio publicado" if count == 1 else "anuncios publicados"}</div>'
            f'<a class="ta-prov-view" href="{esc(profile_url)}">Ver perfil completo →</a>'
            f'<div class="ta-prov-ad-links">{ad_links_html}</div>'
            '</article>'
        )

    description = (
        f"Encuentra tarotistas y profesionales en {province}. "
        "Consulta sus anuncios aprobados y contacta directamente desde TarotAnuncia."
    )
    body = (
        PROVINCE_CARD_CSS
         + '<div class="ta-prov-wrap"><section class="ta-prov-hero">'
        f'<h1>Tarotistas y videntes en {esc(province)}</h1>'
        f'<p>Encuentra profesionales del tarot en {esc(province)}, consulta sus especialidades y accede directamente a sus perfiles y anuncios.</p>'
        '<p class="ta-prov-note">Compara profesionales y elige el que mejor se adapte a tu consulta.</p>'
        '</section>'
        '<div class="ta-prov-grid">' + "".join(cards) + '</div>'
        '<nav class="links"><a href="/tarotistas.html">Ver tarotistas de toda España</a>'
        '<a href="/anuncios.html">Ver todos los anuncios</a></nav></div>'
    )
    structured = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": f"Tarotistas en {province}",
        "url": url,
        "description": description,
    }
    page = document(
        f"Tarotistas en {province} | TarotAnuncia",
        description, url, structured, body
    )
    filename = slug + ".html"
    (PROVINCE_DIR / filename).write_text(
        "<!-- TAROTANUNCIA_PROVINCIA_GENERADA -->\n" + page,
        encoding="utf-8"
    )
    province_files.add(filename)
    province_links.append(url)

# Solo elimina páginas antiguas generadas por este sistema.
for file in PROVINCE_DIR.glob("*.html"):
    if file.name not in province_files:
        if file.read_text(encoding="utf-8").startswith(
            "<!-- TAROTANUNCIA_PROVINCIA_GENERADA -->"
        ):
            file.unlink()


# ==========================================
# GENERAR SITEMAP
# ==========================================

namespace = (
    "http://www.sitemaps.org/"
    "schemas/sitemap/0.9"
)

ET.register_namespace(
    "",
    namespace
)

root = ET.Element(
    "{" + namespace + "}urlset"
)

urls = list(
    dict.fromkeys([
        BASE,
        BASE + "anuncios.html",
        BASE + "tarotistas.html",
        BASE + "tienda-esoterica.html",
        BASE + "foro.html",
        *profile_links,
        *ad_links,
        *province_links,
    ])
)

for url in urls:

    item = ET.SubElement(
        root,
        "{" + namespace + "}url"
    )

    ET.SubElement(
        item,
        "{" + namespace + "}loc"
    ).text = url

ET.indent(
    root,
    space="  "
)

ET.ElementTree(root).write(
    "sitemap.xml",
    encoding="utf-8",
    xml_declaration=True
)

print(
    f"Perfiles: {len(profile_links)} | "
    f"Anuncios: {len(ad_links)} | "
    f"Provincias: {len(province_links)} | "
    f"Sitemap: {len(urls)} URLs"
)
