
import os
import json
import re
import html
import urllib.parse
import urllib.request
from pathlib import Path
import xml.etree.ElementTree as ET

BASE = "https://tarotanuncia.es/"
API = os.environ["SUPABASE_URL"].rstrip("/")
KEY = os.environ["SUPABASE_ANON_KEY"]

DEST = Path("profesionales")
AD_DEST = Path("anuncios")

DEST.mkdir(exist_ok=True)
AD_DEST.mkdir(exist_ok=True)


def fetch(table, params):
    result = []

    for start in range(0, 100000, 1000):
        query = urllib.parse.urlencode(params)

        req = urllib.request.Request(
            f"{API}/rest/v1/{table}?{query}",
            headers={
                "apikey": KEY,
                "Authorization": "Bearer " + KEY,
                "Range-Unit": "items",
                "Range": f"{start}-{start + 999}",
            },
        )

        with urllib.request.urlopen(req, timeout=45) as response:
            batch = json.load(response)

        if not isinstance(batch, list):
            raise RuntimeError(f"Respuesta inválida de {table}")

        result.extend(batch)

        if len(batch) < 1000:
            return result

    raise RuntimeError("Demasiados resultados")


def clean(value):
    return html.escape(str(value or ""), quote=True)


def val(data, key):
    return str(data.get(key) or "").strip()


def cats(data):
    value = data.get("categories") or []

    if isinstance(value, list):
        return [str(item) for item in value]

    return [
        item.strip()
        for item in str(value).split(",")
        if item.strip()
    ]


def phone(value):
    return re.sub(r"[^+0-9]", "", value)


def picture(value):
    parsed = urllib.parse.urlparse(value)

    if parsed.scheme == "https" and parsed.netloc:
        return value

    return ""


def uid(value):
    return bool(
        re.fullmatch(
            r"[0-9a-fA-F-]{36}",
            value,
        )
    )


def text_summary(value, length=155):
    return " ".join(value.split())[:length]


def make_schema(data):
    return json.dumps(
        data,
        ensure_ascii=False,
    ).replace("<", "\\u003c")


# --------------------------------------------------
# DISEÑO COMPARTIDO DE TAROTANUNCIA
# --------------------------------------------------

CSS = """
:root {
    --gold: #d89400;
    --gold2: #efb326;
    --ink: #171526;
    --cream: #fffaf1;
    --line: #eadfce;
    --purple: #702d6b;
}

* {
    box-sizing: border-box;
}

html {
    scroll-behavior: smooth;
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
    color: var(--purple);
}

.site-header {
    background: rgba(255,252,246,.97);
    border-bottom: 1px solid #eee4d6;
    box-shadow: 0 1px 0 rgba(123,84,24,.10);
}

.header-inner {
    max-width: 1240px;
    margin: auto;
    padding: 13px 22px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 16px;
}

.brand {
    text-decoration: none;
    color: var(--ink);
    display: inline-flex;
    align-items: center;
    gap: 9px;
}

.brand-symbol {
    font-size: 27px;
    color: #b97800;
}

.brand-name {
    font: 700 25px Georgia, serif;
    color: var(--ink);
}

.brand-name span {
    color: #b97800;
}

.brand-subtitle {
    display: block;
    font-size: 9px;
    letter-spacing: 1px;
    color: #766a70;
}

.header-nav {
    display: flex;
    gap: 19px;
    align-items: center;
    flex-wrap: wrap;
}

.header-nav a {
    text-decoration: none;
    color: #302833;
    font-size: 13px;
    font-weight: 700;
}

.header-nav a:hover {
    color: #b97800;
}

.hero {
    padding: 27px 18px 15px;
    text-align: center;
}

.hero h1 {
    font: 800 clamp(24px, 4vw, 34px)/1.2 Georgia, serif;
    margin: 0 0 9px;
    overflow-wrap: anywhere;
}

.hero p {
    color: #6c626a;
    margin: 0;
    font-size: 14px;
}

.container {
    width: min(850px, calc(100% - 30px));
    margin: 15px auto 40px;
}

.card {
    background: #fff;
    border: 1px solid #e6d8c2;
    border-top: 4px solid #d5ae55;
    border-radius: 18px;
    padding: 25px;
    box-shadow: 0 5px 16px rgba(50,35,20,.07);
    min-width: 0;
}

.profile-top {
    text-align: center;
}

.avatar {
    display: block;
    width: 115px;
    height: 115px;
    object-fit: contain;
    background: #fffaf1;
    border: 2px solid #ead5a3;
    border-radius: 50%;
    padding: 7px;
    margin: 0 auto 14px;
}

.placeholder {
    display: grid;
    place-items: center;
    color: #b78b39;
    font-size: 44px;
}

.ad-photo-box {
    background: #fbf7f0;
    border: 1px solid #e3d4bc;
    border-radius: 14px;
    padding: 12px;
    margin: 0 auto 19px;
    text-align: center;
}

.ad-photo {
    display: block;
    width: 100%;
    max-height: 360px;
    object-fit: contain;
    margin: auto;
    border-radius: 9px;
}

h1 {
    font: 800 clamp(24px, 4vw, 33px)/1.22 Georgia, serif;
    color: #281d30;
    overflow-wrap: anywhere;
    margin: 0 0 12px;
}

h2 {
    font: 800 21px Georgia, serif;
    color: #3c293e;
    margin: 25px 0 12px;
}

h3 {
    font: 800 17px Georgia, serif;
    margin: 0 0 9px;
}

.meta {
    font-size: 13px;
    color: #766c72;
    margin: 8px 0 15px;
}

.description {
    font-size: 15px;
    line-height: 1.65;
    color: #433a43;
    white-space: pre-line;
    overflow-wrap: anywhere;
}

.tags {
    display: flex;
    flex-wrap: wrap;
    gap: 7px;
    justify-content: center;
    margin: 12px 0;
}

.tag {
    background: #faeafa;
    color: #702d6b;
    padding: 5px 11px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 700;
}

.buttons {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 10px;
    margin: 22px 0;
}

.button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 12px 19px;
    border-radius: 12px;
    text-decoration: none;
    font-size: 14px;
    font-weight: 800;
    min-height: 46px;
    background: linear-gradient(
        135deg,
        var(--gold2),
        var(--gold)
    );
    color: #fff;
}

.button.secondary {
    background: #fffaf1;
    border: 1px solid #d5a43c;
    color: #79550b;
}

.button:hover {
    filter: brightness(.97);
}

.ad-list {
    display: grid;
    grid-template-columns: repeat(2, minmax(0,1fr));
    gap: 13px;
}

.ad-item {
    border: 1px solid #eadfce;
    border-radius: 13px;
    padding: 15px;
    background: #fffdf9;
    min-width: 0;
}

.ad-item a {
    color: #702d6b;
    text-decoration: none;
}

.ad-item a:hover {
    text-decoration: underline;
}

.ad-item p {
    color: #615762;
    font-size: 13px;
    line-height: 1.55;
    overflow-wrap: anywhere;
    white-space: pre-line;
    margin: 8px 0 0;
}

.extra-links {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 9px;
    margin-top: 24px;
    padding-top: 18px;
    border-top: 1px solid #eadfce;
}

.extra-links a {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 9px 12px;
    border-radius: 10px;
    border: 1px solid #eadfce;
    background: #fffaf1;
    color: #785010;
    text-decoration: none;
    font-size: 12px;
    font-weight: 700;
    text-align: center;
}

.extra-links a:hover {
    background: #fff1d3;
}

footer {
    background: #fff7eb;
    border-top: 1px solid #eadcc3;
    text-align: center;
    padding: 24px 15px;
    color: #786d71;
    font-size: 12px;
}

footer strong {
    display: block;
    font: 800 23px Georgia, serif;
    color: #b97800;
    margin-bottom: 7px;
}

footer a {
    color: #785010;
}

@media (max-width: 700px) {

    .header-inner {
        padding: 12px 15px;
        flex-direction: column;
        gap: 9px;
    }

    .brand-name {
        font-size: 23px;
    }

    .header-nav {
        justify-content: center;
        gap: 14px;
    }

    .header-nav a {
        font-size: 12px;
    }

    .hero {
        padding: 22px 15px 12px;
    }

    .hero h1 {
        font-size: 25px;
    }

    .container {
        width: calc(100% - 24px);
        margin: 12px auto 27px;
    }

    .card {
        padding: 17px 15px;
        border-radius: 16px;
    }

    h1 {
        font-size: 25px;
    }

    h2 {
        font-size: 20px;
    }

    .description {
        font-size: 14px;
        line-height: 1.6;
    }

    .ad-photo-box {
        padding: 9px;
    }

    .ad-photo {
        max-height: 300px;
    }

    .ad-list {
        grid-template-columns: 1fr;
    }

    .buttons {
        gap: 8px;
    }

    .button {
        width: 100%;
        font-size: 14px;
    }

    .extra-links {
        gap: 7px;
    }

    .extra-links a {
        flex: 1 1 120px;
        font-size: 11px;
        padding: 9px 7px;
    }
}
"""


def header_html():
    return """
<header class="site-header">
  <div class="header-inner">
    <a class="brand" href="/">
      <span class="brand-symbol">✦</span>
      <span>
        <span class="brand-name">
          Tarot<span>Anuncia</span>
        </span>
        <span class="brand-subtitle">
          TAROTISTAS CERCA DE TI
        </span>
      </span>
    </a>

    <nav class="header-nav" aria-label="Navegación">
      <a href="/">Inicio</a>
      <a href="/anuncios.html">Anuncios</a>
      <a href="/tarotistas.html">Tarotistas</a>
      <a href="/tienda-esoterica.html">Tienda esotérica</a>
    </nav>
  </div>
</header>
"""


def footer_html():
    return """
<footer>
  <strong>TarotAnuncia</strong>
  <div>Encuentra profesionales del tarot en toda España</div>
  <p>
    <a href="/aviso-legal.html">Aviso legal</a>
    ·
    <a href="/politica-privacidad.html">Privacidad</a>
    ·
    <a href="/contacto.html">Contacto</a>
  </p>
</footer>
"""


def document(title, meta, canonical, schema, content):
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport"
      content="width=device-width, initial-scale=1">
<title>{clean(title)}</title>
<meta name="description" content="{clean(meta)}">
<meta name="robots" content="index,follow">
<link rel="canonical" href="{clean(canonical)}">
<script type="application/ld+json">{schema}</script>
<style>
{CSS}
</style>
</head>
<body>
{header_html()}
{content}
{footer_html()}
</body>
</html>
"""


# --------------------------------------------------
# OBTENER PERFILES Y ANUNCIOS APROBADOS
# --------------------------------------------------

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
            {
                "profile": None,
                "ads": [],
            },
        )["ads"].append(ad)

for profile in published:
    owner = val(profile, "owner_id")

    if uid(owner):
        people.setdefault(
            owner,
            {
                "profile": None,
                "ads": [],
            },
        )["profile"] = profile


# --------------------------------------------------
# GENERAR PÁGINAS DE PROFESIONALES
# --------------------------------------------------

links = []

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
            "Consulta el perfil de este profesional en TarotAnuncia.",
        )
    )

    city = val(profile, "city")
    province = val(profile, "province")

    location = ", ".join(
        item
        for item in (city, province)
        if item
    )

    specialties = cats(profile)

    photo = (
        picture(val(profile, "profile_photo_url"))
        or next(
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
    )

    number = phone(val(profile, "phone"))
    whatsapp = phone(val(profile, "whatsapp"))

    url = (
        BASE
        + "profesionales/"
        + owner
        + ".html"
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

    meta = text_summary(
        prefix + description
    )

    tags_html = "".join(
        f'<span class="tag">{clean(category)}</span>'
        for category in specialties[:8]
    )

    ad_items = []

    for ad in data["ads"]:
        ad_id = val(ad, "id")

        if not uid(ad_id):
            continue

        ad_title = (
            val(ad, "title")
            or "Consulta de tarot"
        )

        ad_description = val(
            ad,
            "description",
        )[:250]

        ad_items.append(
            f"""
            <article class="ad-item">
              <h3>
                <a href="/anuncios/{clean(ad_id)}.html">
                  {clean(ad_title)}
                </a>
              </h3>
              <p>{clean(ad_description)}</p>
            </article>
            """
        )

    ad_html = "".join(ad_items)

    buttons = []

    if number:
        buttons.append(
            f"""
            <a class="button"
               href="tel:{clean(number)}">
              Llamar al profesional
            </a>
            """
        )

    if whatsapp:
        wa_number = clean(
            whatsapp.lstrip("+")
        )

        buttons.append(
            f"""
            <a class="button secondary"
               href="https://wa.me/{wa_number}"
               rel="noopener noreferrer">
              Contactar por WhatsApp
            </a>
            """
        )

    buttons_html = "".join(buttons)

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

    modality = val(profile, "modality")

    location_text = clean(
        location or "España"
    )

    if modality:
        location_text += (
            " · " + clean(modality)
        )

    schema_data = {
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
    }

    if location:
        schema_data["contentLocation"] = {
            "@type": "Place",
            "name": location,
        }

    structured = make_schema(schema_data)

    ads_section = ""

    if ad_html:
        ads_section = f"""
        <h2>Sus anuncios</h2>
        <div class="ad-list">
          {ad_html}
        </div>
        """

    content = f"""
<section class="hero">
  <h1>Perfil profesional</h1>
  <p>Descubre profesionales del tarot en TarotAnuncia</p>
</section>

<main class="container">
  <article class="card">

    <div class="profile-top">
      {photo_html}

      <h1>{clean(name)}</h1>

      <p class="meta">{location_text}</p>

      <div class="tags">
        {tags_html}
      </div>
    </div>

    <h2>Sobre este profesional</h2>

    <div class="description">
      {clean(description)}
    </div>

    <div class="buttons">
      {buttons_html}
    </div>

    {ads_section}

    <div class="extra-links">
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
        title,
        meta,
        url,
        structured,
        content,
    )

    (DEST / (owner + ".html")).write_text(
        page,
        encoding="utf-8",
    )

    links.append(url)


# --------------------------------------------------
# ELIMINAR PERFILES ANTIGUOS
# --------------------------------------------------

valid = {
    url.rsplit("/", 1)[-1]
    for url in links
}

for file in DEST.glob("*.html"):
    if (
        file.name not in valid
        and re.fullmatch(
            r"[0-9a-fA-F-]{36}\.html",
            file.name,
        )
    ):
        file.unlink()


# --------------------------------------------------
# GENERAR PÁGINAS INDIVIDUALES DE ANUNCIOS
# --------------------------------------------------

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
        BASE
        + "anuncios/"
        + ad_id
        + ".html"
    )

    original_ad = (
        BASE
        + "anuncios.html?anuncio="
        + urllib.parse.quote(ad_id)
    )

    summary_ad = text_summary(
        description_ad
    )

    photo_ad = picture(
        val(ad, "profile_photo_url")
    )

    if not photo_ad:

        photos_ad = (
            ad.get("photo_urls")
            or []
        )

        if isinstance(photos_ad, list):
            photo_ad = next(
                (
                    url
                    for item in photos_ad
                    if (
                        url := picture(
                            str(item)
                        )
                    )
                ),
                "",
            )

    if photo_ad:
        image_html = f"""
        <div class="ad-photo-box">
          <img class="ad-photo"
               src="{clean(photo_ad)}"
               alt="{clean(title_ad)}">
        </div>
        """
    else:
        image_html = ""

    owner_ad = val(ad, "owner_id")

    profile_html = ""

    if (
        uid(owner_ad)
        and owner_ad in people
    ):
        profile_html = f"""
        <a href="/profesionales/{clean(owner_ad)}.html">
          Ver perfil profesional
        </a>
        """

    schema_ad = make_schema({
        "@context": "https://schema.org",
        "@type": "WebPage",
        "url": url_ad,
        "name": title_ad,
        "description": summary_ad,
    })

    city_html = (
        " · " + clean(city_ad)
        if city_ad
        else ""
    )

    content_ad = f"""
<section class="hero">
  <h1>Anuncios de tarot</h1>
  <p>Contacta directamente con profesionales en España</p>
</section>

<main class="container">
  <article class="card">

    {image_html}

    <h1>{clean(title_ad)}</h1>

    <p class="meta">
      <strong>{clean(name_ad)}</strong>
      {city_html}
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

    <div class="extra-links">

      {profile_html}

      <a href="/anuncios.html">
        Más anuncios
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

    (AD_DEST / (ad_id + ".html")).write_text(
        page_ad,
        encoding="utf-8",
    )

    ad_links.append(url_ad)


# --------------------------------------------------
# ELIMINAR ANUNCIOS ANTIGUOS
# --------------------------------------------------

valid_ads = {
    url.rsplit("/", 1)[-1]
    for url in ad_links
}

for file in AD_DEST.glob("*.html"):
    if (
        file.name not in valid_ads
        and re.fullmatch(
            r"[0-9a-fA-F-]{36}\.html",
            file.name,
        )
    ):
        file.unlink()


# --------------------------------------------------
# GENERAR SITEMAP.XML
# --------------------------------------------------

ns = (
    "http://www.sitemaps.org/"
    "schemas/sitemap/0.9"
)

ET.register_namespace("", ns)

root = ET.Element(
    "{" + ns + "}urlset"
)

urls = [
    BASE,
    BASE + "anuncios.html",
    BASE + "tarotistas.html",
    BASE + "tienda-esoterica.html",
]

urls += links
urls += ad_links

for url in urls:
    element = ET.SubElement(
        root,
        "{" + ns + "}url",
    )

    ET.SubElement(
        element,
        "{" + ns + "}loc",
    ).text = url

ET.indent(
    root,
    space="  ",
)

ET.ElementTree(root).write(
    "sitemap.xml",
    encoding="utf-8",
    xml_declaration=True,
)


# --------------------------------------------------
# RESULTADO
# --------------------------------------------------

print(
    f"Generadas {len(links)} páginas de profesionales. "
    f"Generados {len(ad_links)} anuncios aprobados. "
    f"Sitemap: {len(urls)} URLs."
)
