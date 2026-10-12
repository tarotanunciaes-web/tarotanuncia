
import os
import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

BASE = "https://tarotanuncia.es/"
URL = os.environ["SUPABASE_URL"].rstrip("/")
KEY = os.environ["SUPABASE_ANON_KEY"]

def obtener_perfiles(tabla, filtro):
    perfiles = []
    inicio = 0
    tamano = 1000

    while True:
        params = urllib.parse.urlencode({
            "select": "owner_id",
            **filtro
        })
        peticion = urllib.request.Request(
            f"{URL}/rest/v1/{tabla}?{params}",
            headers={
                "apikey": KEY,
                "Authorization": f"Bearer {KEY}",
                "Range-Unit": "items",
                "Range": f"{inicio}-{inicio + tamano - 1}"
            }
        )
        with urllib.request.urlopen(peticion, timeout=30) as respuesta:
            datos = json.load(respuesta)

        perfiles.extend(datos)
        if len(datos) < tamano:
            break
        inicio += tamano

    return perfiles

identificadores = set()

for perfil in obtener_perfiles(
    "ta_professional_profiles",
    {"is_public": "eq.true"}
):
    if perfil.get("owner_id"):
        identificadores.add(perfil["owner_id"])

for anuncio in obtener_perfiles(
    "tarotist_ads",
    {"status": "eq.approved"}
):
    if anuncio.get("owner_id"):
        identificadores.add(anuncio["owner_id"])

ns = "http://www.sitemaps.org/schemas/sitemap/0.9"
ET.register_namespace("", ns)
raiz = ET.Element(f"{{{ns}}}urlset")

paginas = [
    BASE,
    BASE + "anuncios.html",
    BASE + "tarotistas.html",
    BASE + "tienda-esoterica.html"
]

for identificador in sorted(identificadores):
    paginas.append(
        BASE + "tarotistas.html?perfil="
        + urllib.parse.quote(identificador, safe="")
    )

for pagina in paginas:
    elemento = ET.SubElement(raiz, f"{{{ns}}}url")
    ET.SubElement(elemento, f"{{{ns}}}loc").text = pagina

ET.indent(raiz, space="  ")
ET.ElementTree(raiz).write(
    "sitemap.xml",
    encoding="utf-8",
    xml_declaration=True
)

print(f"Sitemap actualizado: {len(paginas)} URLs")
