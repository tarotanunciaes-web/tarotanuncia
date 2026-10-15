import os
import re
import json
import html
import urllib.parse
import urllib.request
from pathlib import Path
import xml.etree.ElementTree as ET

# CONFIGURACIÓN
BASE = "https://tarotanuncia.es/"
API = os.environ["SUPABASE_URL"].rstrip("/")
KEY = os.environ["SUPABASE_ANON_KEY"]

# Misma imagen utilizada en anuncios.html
LOGO = "/file_000000003c088210be49f3122608d83d.png"

PROFILES_DIR = Path("profesionales")
ADS_DIR = Path("anuncios")
PROFILES_DIR.mkdir(exist_ok=True)
ADS_DIR.mkdir(exist_ok=True)


def fetch(table, params):
    result = []

    for start in range(0, 100000, 1000):
        query = urllib.parse.urlencode(params)
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
                f"Respuesta inválida de {table}"
            )

        result.extend(batch)

        if len(batch) < 1000:
            return result

    raise RuntimeError("Demasiados resultados")


def clean(value):
    return html.escape(
        str(value or ""), quote=True
    )


def val(data, key):
    return str(data.get(key) or "").strip()


def uid(value):
    return bool(
        re.fullmatch(
            r"[0-9a-fA-F-]{36}", value
        )
    )


def picture(value):
    parsed = urllib.parse.urlparse(value)
    if parsed.scheme == "https" and parsed.netloc:
        return value
    return ""


def phone(value):
    return re.sub(r"[^+0-9]", "", value)


def categories(data):
    value = data.get("categories") or []

    if isinstance(value, list):
        return [str(item) for item in value]

    return [
        item.strip()
        for item in str(value).split(",")
        if item.strip()
    ]


def summary(value, length=155):
    return " ".join(value.split())[:length]


def structured_data(value):
    return json.dumps(
        value, ensure_ascii=False
    ).replace("<", "\\u003c")


# ESTILOS DE TAROTANUNCIA
CSS = """
:root {
    --gold: #d89400;
    --gold-light: #efb326;
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
}

body {
    margin: 0;
    background: #fbfaf6;
    color: var(--ink);
    font-family: Arial, system-ui, sans-serif;
    font-size: 15px;
    line-height: 1.55;
}

a {
    color: #79500c;
}

.site-header {
    background: #fffcf6;
    border-bottom: 1px solid #eee4d6;
    position: sticky;
    top: 0;
    z-index: 50;
}

.nav {
    max-width: 1240px;
    margin: auto;
    min-height: 68px;
    padding: 10px 18px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 14px;
}

.brand {
    display: flex;
    align-items: center;
    gap: 9px;
    color: var(--ink);
    text-decoration: none;
    white-space: nowrap;
}

.brand-logo {
    width: 43px;
    height: 43px;
    object-fit: contain;
    flex-shrink: 0;
}

.brand-name {
    font: 700 25px Georgia, serif;
}

.brand-name span {
    color: #b97800;
}

.brand-subtitle {
    display: block;
    font-size: 8px;
    letter-spacing: 1.2px;
    color: #6c626a;
}

.nav-links {
    display: flex;
    align-items: center;
    gap: 18px;
}

.nav-links a {
    text-decoration: none;
    color: #302833;
    font-size: 13px;
    font-weight: 600;
}

.nav-links a:hover {
    color: #b97800;
}

.menu-toggle {
    display: none;
    background: transparent;
    border: 0;
    color: #211b22;
    font: 800 14px Arial, sans-serif;
    padding: 10px;
    cursor: pointer;
}

.mobile-links[hidden] {
    display: none !important;
}

.mobile-links {
    display: none;
}

main {
    width: min(900px, calc(100% - 30px));
    margin: 25px auto 40px;
}

.panel {
    background: #fff;
    border: 1px solid #e6d8c2;
    border-top: 4px solid #d5ae55;
    border-radius: 17px;
    padding: 25px;
    box-shadow: 0 5px 16px rgba(50,35,20,.07);
    overflow: hidden;
}

.intro {
    text-align: center;
}

.avatar {
    display: block;
    width: 115px;
    height: 115px;
    object-fit: contain;
    padding: 8px;
    background: var(--cream);
    border: 2px solid #ead5a3;
    border-radius: 50%;
    margin: 0 auto;
}

.placeholder {
    display: grid;
    place-items: center;
    font-size: 46px;
    color: #b78b39;
}

h1 {
    font: 800 clamp(23px, 3.4vw, 31px)/1.25 Georgia, serif;
    margin: 15px 0 12px;
    overflow-wrap: anywhere;
}

h2 {
    font: 800 21px Georgia, serif;
    margin: 24px 0 12px;
}

h3 {
    font: 800 17px Georgia, serif;
    margin: 0 0 8px;
}

.description {
    font-size: 15px;
    line-height: 1.6;
    white-space: pre-line;
    overflow-wrap: anywhere;
    color: #433a43;
    margin: 15px 0;
}

.location,
.detail-meta {
    color: #655d65;
    font-size: 14px;
    margin: 10px 0;
}

.tag {
    display: inline-block;
    margin: 4px;
    padding: 6px 10px;
    border-radius: 25px;
    background: #f7eaf5;
    color: var(--purple);
    font-size: 12px;
}

.photo {
    display: block;
    width: 100%;
    max-height: 340px;
    object-fit: contain;
    background: #fbf7f0;
    border: 1px solid var(--line);
    border-radius: 12px;
    padding: 8px;
    margin-bottom: 18px;
}

.buttons {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 10px;
    margin: 20px 0;
}

.button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    background: linear-gradient(
        135deg,
        var(--gold-light),
        var(--gold)
    );
    color: #fff;
    text-decoration: none;
    border-radius: 12px;
    padding: 12px 19px;
    font-size: 14px;
    font-weight: 800;
    min-height: 45px;
}

.button.secondary {
    background: #fffaf1;
    color: #79550b;
    border: 1px solid #d5a43c;
}

.ad-list {
    display: grid;
    grid-template-columns: repeat(2, minmax(0,1fr));
    gap: 12px;
}

.ad {
    background: #fffdf9;
    border: 1px solid var(--line);
    border-radius: 12px;
    padding: 14px;
    min-width: 0;
}

.ad a {
    color: var(--purple);
    text-decoration: none;
}

.ad p {
    font-size: 13px;
    line-height: 1.55;
    white-space: pre-line;
    overflow-wrap: anywhere;
    margin: 8px 0 0;
}

.links {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 9px;
    margin-top: 20px;
    padding-top: 16px;
    border-top: 1px solid var(--line);
}

.links a {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    background: var(--cream);
    border: 1px solid var(--line);
    border-radius: 10px;
    padding: 9px 12px;
    font-size: 12px;
    font-weight: 700;
    text-decoration: none;
}

footer {
    background: #fff7eb;
    border-top: 1px solid #eadcc3;
    padding: 25px 14px;
    text-align: center;
    font-size: 13px;
    color: #786d71;
}

@media (max-width: 900px) {
    .nav {
        min-height: 66px;
        padding: 10px 14px;
    }

    .nav-links {
        display: none;
    }

    .menu-toggle {
        display: block;
        margin-left: auto;
        white-space: nowrap;
    }

    .mobile-links:not([hidden]) {
        display: grid;
        gap: 2px;
        background: #fffdf9;
        border-top: 1px solid var(--line);
        padding: 9px 15px 15px;
    }

    .mobile-links a {
        display: block;
        padding: 12px;
        border-radius: 9px;
        text-decoration: none;
        font-size: 14px;
        font-weight: 700;
        color: #302833;
    }

    .mobile-links a:hover {
        background: #fff5df;
    }
}

@media (max-width: 600px) {
    .brand-logo {
        width: 37px;
        height: 37px;
    }

    .brand-name {
        font-size: 21px;
    }

    .brand-subtitle {
        font-size: 7px;
    }

    .menu-toggle {
        font-size: 12px;
        padding: 7px;
    }

    main {
        width: calc(100% - 24px);
        margin: 16px auto 28px;
    }

    .panel {
        padding: 16px;
        border-radius: 15px;
    }

    h1 {
        font-size: 23px;
    }

    h2 {
        font-size: 19px;
    }

    .description {
        font-size: 14px;
        line-height: 1.55;
    }

    .photo {
        max-height: 280px;
    }

    .ad-list {
        grid-template-columns: 1fr;
    }

    .button {
        width: 100%;
    }

    .links a {
        flex: 1 1 120px;
    }
}
"""


# CABECERA Y MENÚ
def header_html():
    return f"""
<header class="site-header">
  <div class="nav">

    <a class="brand" href="/">
      <img class="brand-logo"
           src="{clean(LOGO)}"
           alt="Logo TarotAnuncia">

      <span>
        <span class="brand-name">
          Tarot<span>Anuncia</span>
        </span>
        <small class="brand-subtitle">
          TAROTISTAS CERCA DE TI
        </small>
      </span>
    </a>

    <button class="menu-toggle"
            type="button"
            aria-expanded="false"
            aria-controls="ta-mobile-menu"
            onclick="taToggleMenu(this)">
      ☰ MENÚ
    </button>

    <nav class="nav-links"
         aria-label="Navegación">
      <a href="/">Inicio</a>
      <a href="/anuncios.html">Anuncios</a>
      <a href="/tarotistas.html">Tarotistas</a>
      <a href="/tienda-esoterica.html">
        Tienda esotérica
      </a>
    </nav>

  </div>

  <nav class="mobile-links"
       id="ta-mobile-menu"
       aria-label="Menú móvil"
       hidden>
    <a href="/">Inicio</a>
    <a href="/anuncios.html">Anuncios</a>
    <a href="/tarotistas.html">Tarotistas</a>
    <a href="/tienda-esoterica.html">
      Tienda esotérica
    </a>
  </nav>
</header>
"""


SCRIPT = """
<script>
function taToggleMenu(button) {
    const menu = document.getElementById(
        "ta-mobile-menu"
    );

    const opening = menu.hasAttribute("hidden");

    if (opening) {
        menu.removeAttribute("hidden");
    } else {
        menu.setAttribute("hidden", "");
    }

    button.setAttribute(
        "aria-expanded",
        String(opening)
    );
}
</script>
"""


def document(title, meta, url, schema, content):
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport"
      content="width=device-width,initial-scale=1">
<title>{clean(title)}</title>
<meta name="description" content="{clean(meta)}">
<meta name="robots" content="index,follow">
<link rel="canonical" href="{clean(url)}">
<script type="application/ld+json">{schema}</script>
<style>{CSS}</style>
</head>
<body>
{header_html()}
{content}
<footer>
  TarotAnuncia · Directorio de profesionales del tarot
</footer>
{SCRIPT}
</body>
</html>
"""


# OBTENER DATOS DE SUPABASE
published = fetch(
    "ta_professional_profiles",
    {
        "select": "*",
        "is_public": "eq.true",
    },
)

ads = fetch(
    "tarotist_ads",
    {
        "select": "*",
        "status": "eq.approved",
    },
)

people = {}

for ad in ads:
    owner = val(ad, "owner_id")

    if uid(owner):
        people.setdefault(
            owner,
            {"profile": None, "ads": []},
        )["ads"].append(ad)

for profile in published:
    owner = val(profile, "owner_id")

    if uid(owner):
        people.setdefault(
            owner,
            {"profile": None, "ads": []},
        )["profile"] = profile


# GENERAR PERFILES
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
            "Consulta este perfil en TarotAnuncia.",
        )
    )

    city = val(profile, "city")
    province = val(profile, "province")

    location = ", ".join(
        item
        for item in (city, province)
        if item
    )

    specialties = categories(profile)

    photo = picture(
        val(profile, "profile_photo_url")
    )

    if not photo:
        photo = next(
            (
                url
                for ad in data["ads"]
                if (
                    url := picture(
                        val(ad, "profile_photo_url")
                    )
                )
            ),
            "",
        )

    number = phone(val(profile, "phone"))
    whatsapp = phone(val(profile, "whatsapp"))

    url = (
        BASE + "profesionales/"
        + owner + ".html"
    )

    title = (
        f"{name} | Tarotista en "
        f"{location or 'España'} | TarotAnuncia"
    )

    prefix = (
        f"{name} | Tarot en {location}. "
        if location
        else f"{name} | TarotAnuncia. "
    )

    meta = summary(prefix + description)

    if photo:
        photo_html = (
            f'<img class="avatar" '
            f'src="{clean(photo)}" '
            f'alt="Foto de {clean(name)}">'
        )
    else:
        photo_html = (
            '<div class="avatar placeholder">✦</div>'
        )

    tags_html = "".join(
        f'<span class="tag">{clean(item)}</span>'
        for item in specialties[:8]
    )

    buttons = []

    if number:
        buttons.append(
            f'<a class="button" '
            f'href="tel:{clean(number)}">'
            f'Llamar</a>'
        )

    if whatsapp:
        wa = whatsapp.lstrip("+")

        buttons.append(
            f'<a class="button secondary" '
            f'href="https://wa.me/{clean(wa)}" '
            f'rel="noopener noreferrer">'
            f'WhatsApp</a>'
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

        ad_cards.append(
            f"""
            <article class="ad">
              <h3>
                <a href="/anuncios/{clean(ad_id)}.html">
                  {clean(ad_title)}
                </a>
              </h3>
              <p>
                {clean(val(ad, "description")[:600])}
              </p>
            </article>
            """
        )

    ads_section = ""

    if ad_cards:
        ads_section = (
            '<h2>Sus anuncios</h2>'
            '<div class="ad-list">'
            + "".join(ad_cards)
            + '</div>'
        )

    modality = val(profile, "modality")

    location_text = clean(
        location or "España"
    )

    if modality:
        location_text += " · " + clean(modality)

    schema = structured_data({
        "@context": "https://schema.org",
        "@type": "ProfilePage",
        "url": url,
        "name": name,
        "description": meta,
        "mainEntity": {
            "@type": "Person",
            "name": name,
            "description": description[:400],
        },
    })

    content = f"""
<main>
  <article class="panel">

    <div class="intro">
      {photo_html}

      <h1>{clean(name)}</h1>

      <p class="location">
        {location_text}
      </p>

      <div>{tags_html}</div>
    </div>

    <h2>Sobre este profesional</h2>

    <div class="description">
      {clean(description)}
    </div>

    <div class="buttons">
      {''.join(buttons)}
    </div>

    {ads_section}

    <div class="links">
      <a href="/tarotistas.html?perfil={clean(owner)}">
        Ver ficha completa y valoraciones
      </a>

      <a href="/tarotistas.html">
        Más profesionales
      </a>

      <a href="/anuncios.html">
        Ver anuncios
      </a>
    </div>

  </article>
</main>
"""

    page = document(
        title, meta, url, schema, content
    )

    (PROFILES_DIR / (owner + ".html")).write_text(
        page, encoding="utf-8"
    )

    profile_links.append(url)


# ELIMINAR PERFILES ANTIGUOS
valid_profiles = {
    url.rsplit("/", 1)[-1]
    for url in profile_links
}

for file in PROFILES_DIR.glob("*.html"):
    if (
        file.name not in valid_profiles
        and re.fullmatch(
            r"[0-9a-fA-F-]{36}\.html",
            file.name,
        )
    ):
        file.unlink()


# GENERAR ANUNCIOS INDIVIDUALES
ad_links = []

for ad in ads:

    ad_id = val(ad, "id")

    if not uid(ad_id):
        continue

    title_ad = (
        val(ad, "title")
        or "Consulta de tarot"
    )

    name_ad = (
        val(ad, "display_name")
        or "Profesional del tarot"
    )

    description_ad = (
        val(ad, "description")
        or "Descubre este anuncio en TarotAnuncia."
    )

    city_ad = val(ad, "city")

    url_ad = (
        BASE + "anuncios/"
        + ad_id + ".html"
    )

    original_ad = (
        BASE + "anuncios.html?anuncio="
        + urllib.parse.quote(ad_id)
    )

    summary_ad = summary(description_ad)

    photo_ad = picture(
        val(ad, "profile_photo_url")
    )

    if not photo_ad:
        photo_urls = ad.get("photo_urls") or []

        if isinstance(photo_urls, list):
            photo_ad = next(
                (
                    url
                    for item in photo_urls
                    if (
                        url := picture(str(item))
                    )
                ),
                "",
            )

    image_html = ""

    if photo_ad:
        image_html = (
            f'<img class="photo" '
            f'src="{clean(photo_ad)}" '
            f'alt="{clean(title_ad)}">'
        )

    owner_ad = val(ad, "owner_id")

    profile_html = ""

    if uid(owner_ad) and owner_ad in people:
        profile_html = (
            f'<a href="/profesionales/'
            f'{clean(owner_ad)}.html">'
            f'Ver perfil profesional</a>'
        )

    schema_ad = structured_data({
        "@context": "https://schema.org",
        "@type": "WebPage",
        "url": url_ad,
        "name": title_ad,
        "description": summary_ad,
    })

    location_ad = (
        " · " + clean(city_ad)
        if city_ad
        else ""
    )

    content_ad = f"""
<main>
  <article class="panel">

    {image_html}

    <h1>{clean(title_ad)}</h1>

    <p class="detail-meta">
      <strong>{clean(name_ad)}</strong>
      {location_ad}
    </p>

    <div class="description">
      {clean(description_ad)}
    </div>

    <div class="buttons">
      <a class="button"
         href="{clean(original_ad)}">
        Ver anuncio completo y contactar
      </a>
    </div>

    <div class="links">
      {profile_html}

      <a href="/anuncios.html">
        Ver más anuncios de tarot
      </a>

      <a href="/tarotistas.html">
        Explorar profesionales
      </a>
    </div>

  </article>
</main>
"""

    page_ad = document(
        title_ad + " | TarotAnuncia",
        summary_ad,
        url_ad,
        schema_ad,
        content_ad,
    )

    (ADS_DIR / (ad_id + ".html")).write_text(
        page_ad,
        encoding="utf-8",
    )

    ad_links.append(url_ad)


# ELIMINAR ANUNCIOS ANTIGUOS
valid_ads = {
    url.rsplit("/", 1)[-1]
    for url in ad_links
}

for file in ADS_DIR.glob("*.html"):
    if (
        file.name not in valid_ads
        and re.fullmatch(
            r"[0-9a-fA-F-]{36}\.html",
            file.name,
        )
    ):
        file.unlink()


# ACTUALIZAR SITEMAP
namespace = (
    "http://www.sitemaps.org/"
    "schemas/sitemap/0.9"
)

ET.register_namespace("", namespace)

root = ET.Element(
    "{" + namespace + "}urlset"
)

urls = [
    BASE,
    BASE + "anuncios.html",
    BASE + "tarotistas.html",
    BASE + "tienda-esoterica.html",
]

urls += profile_links
urls += ad_links

for url in urls:
    elem
