
import os
import re
import json
import html
import urllib.parse
import urllib.request
from pathlib import Path
import xml.etree.ElementTree as ET


# ==========================================
# TAROTANUNCIA
# GENERADOR DE FICHAS Y SITEMAP
# ==========================================

BASE = "https://tarotanuncia.es/"

API = os.environ["SUPABASE_URL"].rstrip("/")
KEY = os.environ["SUPABASE_ANON_KEY"]

LOGO = (
    "/file_000000003c088210be49f3122608d83d.png"
)

PROFILE_DIR = Path("profesionales")
AD_DIR = Path("anuncios")

PROFILE_DIR.mkdir(exist_ok=True)
AD_DIR.mkdir(exist_ok=True)


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
    return html.escape(
        str(value or ""), quote=True
    )


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

    if (
        parsed.scheme == "https"
        and parsed.netloc
    ):
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
        str(value).split()
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


# ==========================================
# DISEÑO COMPLETO
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
    width: min(280px, 85vw);
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
    width: min(850px, calc(100% - 24px));
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

/* ANUNCIOS DEL PROFESIONAL */

.ad-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0,1fr));
    gap: 12px;
}

.ad-card {
    background: #fffdf9;
    border: 1px solid var(--line);
    border-radius: 13px;
    padding: 14px;
    min-width: 0;
}

.ad-card a {
    text-decoration: none;
    color: var(--purple);
}

.ad-card p {
    font-size: 13px;
    color: #625961;
    line-height: 1.5;
    margin: 8px 0 0;
    white-space: pre-line;
    overflow-wrap: anywhere;
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

/* TABLET Y MÓVIL */

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
# CABECERA
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


# ==========================================
# JAVASCRIPT DEL MENÚ
# ==========================================

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


# ==========================================
# PIE DE PÁGINA
# ==========================================

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


# ==========================================
# DOCUMENTO HTML
# ==========================================

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
# CONSULTAR SUPABASE
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
# GENERAR PERFILES PROFESIONALES
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

    ad_cards = []

    for ad in data["ads"]:

        ad_id = val(ad, "id")

        if not uid(ad_id):
            continue

        ad_title = (
            val(ad, "title")
            or "Consulta de tarot"
        )

        ad_description = (
            val(ad, "description")[:400]
        )

        ad_cards.append(f"""
        <article class="ad-card">
          <h3>
            <a href="/anuncios/{esc(ad_id)}.html">
              {esc(ad_title)}
            </a>
          </h3>

          <p>{esc(ad_description)}</p>
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
# GENERAR ANUNCIOS INDIVIDUALES
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
# ELIMINAR FICHAS ANTIGUAS
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
        *profile_links,
        *ad_links,
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
    f"Sitemap: {len(urls)} URLs"
)
