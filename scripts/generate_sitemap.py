
name: Actualizar sitemap de TarotAnuncia

on:
  schedule:
    - cron: '0 */6 * * *'
  workflow_dispatch:

permissions:
  contents: write

jobs:
  actualizar:
    runs-on: ubuntu-latest

    steps:
      - name: Descargar repositorio
        uses: actions/checkout@v4

      - name: Preparar Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Aplicar mejoras SEO
        run: |
          python - <<'PY'
          from pathlib import Path

          archivo = Path("scripts/generate_sitemap.py")
          codigo = archivo.read_text(encoding="utf-8")

          cambios = [
              (
                  "<h1>Perfil profesional</h1>",
                  "<p>Perfil profesional</p>"
              ),
              (
                  "<h1>Anuncios de tarot</h1>",
                  "<p>Anuncios de tarot</p>"
              ),
              (
                  'title + " | TarotAnuncia",',
                  'f"{title} | {name} | TarotAnuncia",'
              )
          ]

          for original, nuevo in cambios:
              cantidad = codigo.count(original)

              if cantidad == 1:
                  codigo = codigo.replace(original, nuevo)
              elif cantidad == 0 and nuevo in codigo:
                  print("Mejora SEO ya aplicada")
              else:
                  raise RuntimeError(
                      "No se pudo verificar el cambio SEO: "
                      + original
                  )

          archivo.write_text(
              codigo,
              encoding="utf-8"
          )

          print("Mejoras SEO aplicadas correctamente")
          PY

      - name: Generar perfiles, anuncios, provincias y sitemap
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_ANON_KEY: ${{ secrets.SUPABASE_ANON_KEY }}
        run: python scripts/generate_sitemap.py

      - name: Guardar cambios
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"

          git add -A \
            scripts/generate_sitemap.py \
            sitemap.xml \
            profesionales/ \
            anuncios/ \
            tarotistas/

          if ! git diff --cached --quiet; then
            git commit -m "Actualizar SEO, perfiles, anuncios y sitemap"
            git push
          fi
