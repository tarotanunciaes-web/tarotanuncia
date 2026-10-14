
import os
import json
import re
import html
import urllib.parse
import urllib.request
from pathlib import Path
import xml.etree.ElementTree as ET

BASE = 'https://tarotanuncia.es/'
API = os.environ['SUPABASE_URL'].rstrip('/')
KEY = os.environ['SUPABASE_ANON_KEY']

DEST = Path('profesionales')
DEST.mkdir(exist_ok=True)


def fetch(table, params):
    result = []
    for start in range(0, 100000, 1000):
        query = urllib.parse.urlencode(params)
        req = urllib.request.Request(
            f'{API}/rest/v1/{table}?{query}',
            headers={
                'apikey': KEY,
                'Authorization': 'Bearer ' + KEY,
                'Range-Unit': 'items',
                'Range': f'{start}-{start+999}'
            }
        )
        with urllib.request.urlopen(req, timeout=45) as response:
            batch = json.load(response)
        if not isinstance(batch, list):
            raise RuntimeError(f'Respuesta inválida de {table}')
        result.extend(batch)
        if len(batch) < 1000:
            return result
    raise RuntimeError('Demasiados resultados')


def clean(s):
    return html.escape(str(s or ''), quote=True)


def val(d, k):
    return str(d.get(k) or '').strip()


def cats(d):
    x = d.get('categories') or []
    if isinstance(x, list):
        return [str(z) for z in x]
    return [z.strip() for z in str(x).split(',') if z.strip()]


def phone(s):
    return re.sub(r'[^+0-9]', '', s)


def picture(s):
    u = urllib.parse.urlparse(s)
    return s if u.scheme == 'https' and u.netloc else ''


def uid(s):
    return bool(re.fullmatch(r'[0-9a-fA-F-]{36}', s))


published = fetch(
    'ta_professional_profiles',
    {'select': '*', 'is_public': 'eq.true'}
)

ads = fetch(
    'tarotist_ads',
    {'select': '*', 'status': 'eq.approved'}
)

people = {}

for a in ads:
    owner = val(a, 'owner_id')
    if uid(owner):
        people.setdefault(
            owner, {'profile': None, 'ads': []}
        )['ads'].append(a)

for p in published:
    owner = val(p, 'owner_id')
    if uid(owner):
        people.setdefault(
            owner, {'profile': None, 'ads': []}
        )['profile'] = p

links = []

for owner, data in sorted(people.items()):
    p = data['profile'] or (
        data['ads'][0] if data['ads'] else {}
    )

    name = val(p, 'display_name') or 'Profesional del tarot'

    description = val(p, 'description') or next(
        (
            val(a, 'description')
            for a in data['ads']
            if val(a, 'description')
        ),
        'Consulta el perfil de este profesional en TarotAnuncia.'
    )

    city = val(p, 'city')
    province = val(p, 'province')
    location = ', '.join(
        x for x in (city, province) if x
    )

    specialties = cats(p)

    photo = picture(val(p, 'profile_photo_url')) or next(
        (
            u for a in data['ads']
            if (u := picture(val(a, 'profile_photo_url')))
        ),
        ''
    )

    number = phone(val(p, 'phone'))
    whatsapp = phone(val(p, 'whatsapp'))

    url = BASE + 'profesionales/' + owner + '.html'

    title = (
        f'{name} | Tarotista en '
        f'{location or "España"} | TarotAnuncia'
    )

    summary = ' '.join(description.split())
    prefix = (
        f'{name} | Tarot en {location}. '
        if location else
        f'{name} | TarotAnuncia. '
    )
    meta = (prefix + summary)[:155]

    ad_html = ''.join(
        f'<article class="ad">'
        f'<h3><a href="/anuncios/{clean(val(a, "id"))}.html">{clean(val(a, "title") or "Consulta de tarot")}</a></h3>'
        f'<p>{clean(val(a, "description")[:600])}</p>'
        f'</article>'
        for a in data['ads']
    )

    tags = ''.join(
        f'<span class="tag">{clean(c)}</span>'
        for c in specialties[:8]
    )

    buttons = ''.join([
        (
            f'<a class="button" href="tel:{clean(number)}">'
            f'Llamar</a>'
        ) if number else '',
        (
            f'<a class="button" '
            f'href="https://wa.me/{clean(whatsapp.lstrip("+"))}" '
            f'rel="noopener noreferrer">WhatsApp</a>'
        ) if whatsapp else ''
    ])

    photo_html = (
        f'<img class="avatar" src="{clean(photo)}" '
        f'alt="Foto de {clean(name)}">'
        if photo else
        '<div class="avatar placeholder">✦</div>'
    )

    schema_data = {
        '@context': 'https://schema.org',
        '@type': 'ProfilePage',
        'url': url,
        'name': name,
        'description': meta,
        'mainEntity': {
            '@type': 'Person',
            'name': name,
            'description': description[:400]
        }
    }

    if location:
        schema_data['contentLocation'] = {
            '@type': 'Place',
            'name': location
        }

    structured = json.dumps(
        schema_data, ensure_ascii=False
    ).replace('<', '\\u003c')

    page = f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{clean(title)}</title>
<meta name="description" content="{clean(meta)}">
<meta name="robots" content="index,follow">
<link rel="canonical" href="{clean(url)}">
<script type="application/ld+json">{structured}</script>
<style>
*{{box-sizing:border-box}}
body{{margin:0;background:#fbfaf6;color:#241a28;font-family:Arial,sans-serif}}
header{{background:#fffaf1;border-bottom:1px solid #ead9bd;padding:18px}}
header a{{font:bold 25px Georgia,serif;color:#7e5109;text-decoration:none}}
main{{max-width:760px;margin:30px auto;padding:0 16px}}
.panel{{background:white;border:1px solid #e4d3b8;border-top:4px solid #d5ae55;border-radius:20px;padding:28px;box-shadow:0 8px 24px #3a271a14}}
.intro{{text-align:center}}
.avatar{{width:125px;height:125px;object-fit:contain;padding:12px;background:#fffaf1;border-radius:50%;border:3px solid #ead5a3;margin:auto}}
.placeholder{{display:grid;place-items:center;font-size:50px;color:#b78b39}}
h1{{font:800 32px Georgia,serif;margin:14px 0}}
h2{{font:800 23px Georgia,serif;margin-top:26px}}
p{{line-height:1.65;overflow-wrap:anywhere;white-space:pre-wrap}}
.location{{color:#766c72}}
.tag{{display:inline-block;margin:5px;padding:6px 10px;border-radius:25px;background:#f7eaf5;color:#702d6b;font-size:12px}}
.button{{display:inline-block;background:#e7a91b;color:white;text-decoration:none;border-radius:11px;padding:12px 20px;margin:6px;font-weight:bold}}
.ad{{border:1px solid #eadfce;border-radius:12px;padding:12px;margin:10px 0}}
.ad h3{{margin:0}}
footer{{text-align:center;padding:28px;font-size:13px;color:#786d71}}
a{{color:#785010}}
@media(max-width:500px){{.panel{{padding:19px}}h1{{font-size:27px}}}}
</style>
</head>
<body>
<header><a href="/">✦ TarotAnuncia</a></header>
<main>
<article class="panel">
<div class="intro">
{photo_html}
<h1>{clean(name)}</h1>
<p class="location">{clean(location or 'España')}{' · '+clean(val(p,'modality')) if val(p,'modality') else ''}</p>
{tags}
</div>
<h2>Sobre este profesional</h2>
<p>{clean(description)}</p>
<div class="intro">{buttons}</div>
{'<h2>Sus anuncios</h2>'+ad_html if ad_html else ''}
<p><a href="/tarotistas.html?perfil={clean(owner)}">Ver ficha completa y valoraciones en TarotAnuncia →</a></p>
<p><a href="/tarotistas.html">Descubrir más profesionales</a> · <a href="/anuncios.html">Ver todos los anuncios</a></p>
</article>
</main>
<footer>TarotAnuncia · Directorio de profesionales del tarot</footer>
</body>
</html>'''

    (DEST / (owner + '.html')).write_text(
        page, encoding='utf-8'
    )

    links.append(url)

# Eliminar páginas antiguas que ya no son públicas
valid = {u.rsplit('/', 1)[-1] for u in links}

for file in DEST.glob('*.html'):
    if (
        file.name not in valid
        and re.fullmatch(r'[0-9a-fA-F-]{36}\.html', file.name)
    ):
        file.unlink()

# Crear páginas individuales, legibles por Google, de anuncios aprobados.
AD_DEST = Path('anuncios')
AD_DEST.mkdir(exist_ok=True)
ad_links = []

for a in ads:
    ad_id = val(a, 'id')
    if not uid(ad_id):
        continue

    title_ad = val(a, 'title') or 'Consulta de tarot'
    name_ad = val(a, 'display_name') or 'Profesional del tarot'
    description_ad = val(a, 'description') or 'Descubre este anuncio en TarotAnuncia.'
    city_ad = val(a, 'city')
    url_ad = BASE + 'anuncios/' + ad_id + '.html'
    original_ad = BASE + 'anuncios.html?anuncio=' + urllib.parse.quote(ad_id)
    summary_ad = ' '.join(description_ad.split())[:155]
    photo_ad = picture(val(a, 'profile_photo_url'))

    if not photo_ad:
        photos_ad = a.get('photo_urls') or []
        if isinstance(photos_ad, list):
            photo_ad = next(
                (u for x in photos_ad if (u := picture(str(x)))),
                ''
            )

    image_html = (
        f'<img class="photo" src="{clean(photo_ad)}" alt="{clean(title_ad)}">'
        if photo_ad else ''
    )

    owner_ad = val(a, 'owner_id')
    profile_html = (
        f'<p><a href="/profesionales/{clean(owner_ad)}.html">Ver perfil profesional</a></p>'
        if uid(owner_ad) and owner_ad in people else ''
    )

    schema_ad = json.dumps({
        '@context': 'https://schema.org',
        '@type': 'WebPage',
        'url': url_ad,
        'name': title_ad,
        'description': summary_ad,
    }, ensure_ascii=False).replace('<', '\\u003c')

    page_ad = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{clean(title_ad)} | TarotAnuncia</title>
<meta name="description" content="{clean(summary_ad)}">
<meta name="robots" content="index,follow">
<link rel="canonical" href="{clean(url_ad)}">
<script type="application/ld+json">{schema_ad}</script>
<style>
*{{box-sizing:border-box}}
body{{margin:0;background:#fbfaf6;color:#241a28;font-family:Arial,sans-serif}}
header{{background:#fffaf1;border-bottom:1px solid #ead9bd;padding:18px}}
header a{{font:bold 25px Georgia,serif;color:#7e5109;text-decoration:none}}
main{{max-width:760px;margin:30px auto;padding:0 16px}}
article{{background:#fff;border:1px solid #e4d3b8;border-top:4px solid #d5ae55;border-radius:20px;padding:28px}}
h1{{font:800 30px Georgia,serif}}
p{{line-height:1.65;white-space:pre-wrap;overflow-wrap:anywhere}}
.photo{{width:100%;max-height:360px;object-fit:contain;background:#fffaf1;border-radius:12px}}
.button{{display:inline-block;background:#bd8520;color:#fff;text-decoration:none;border-radius:11px;padding:13px 20px;font-weight:bold}}
a{{color:#785010}}
</style>
</head>
<body>
<header><a href="/">✦ TarotAnuncia</a></header>
<main><article>
{image_html}
<h1>{clean(title_ad)}</h1>
<p><strong>{clean(name_ad)}</strong>{' · ' + clean(city_ad) if city_ad else ''}</p>
<p>{clean(description_ad)}</p>
{profile_html}
<p><a class="button" href="{clean(original_ad)}">Ver anuncio completo y contactar</a></p>
<p><a href="/anuncios.html">Ver más anuncios de tarot</a> · <a href="/tarotistas.html">Explorar profesionales</a></p>
</article></main>
</body>
</html>"""

    (AD_DEST / (ad_id + '.html')).write_text(
        page_ad, encoding='utf-8'
    )
    ad_links.append(url_ad)

# Eliminar páginas individuales de anuncios pausados, rechazados o borrados.
valid_ads = {u.rsplit('/', 1)[-1] for u in ad_links}

for file in AD_DEST.glob('*.html'):
    if (
        file.name not in valid_ads
        and re.fullmatch(r'[0-9a-fA-F-]{36}\.html', file.name)
    ):
        file.unlink()

# Actualizar sitemap
ns = 'http://www.sitemaps.org/schemas/sitemap/0.9'
ET.register_namespace('', ns)
root = ET.Element('{' + ns + '}urlset')

for url in [
    BASE,
    BASE + 'anuncios.html',
    BASE + 'tarotistas.html',
    BASE + 'tienda-esoterica.html'
] + links + ad_links:
    e = ET.SubElement(root, '{' + ns + '}url')
    ET.SubElement(e, '{' + ns + '}loc').text = url

ET.indent(root, space='  ')

ET.ElementTree(root).write(
    'sitemap.xml',
    encoding='utf-8',
    xml_declaration=True
)

print(
    f'Generadas {len(links)} páginas de profesionales. '
    f'Generados {len(ad_links)} anuncios aprobados. '
    f'Sitemap: {4+len(links)+len(ad_links)} URLs.'
)
