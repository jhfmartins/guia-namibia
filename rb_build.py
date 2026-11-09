#!/usr/bin/env python3
"""Constrói roadbook.html a partir de days.json + photos.json + o CSS do index.html."""
import json, re, html, os

dias = json.load(open('days.json', encoding='utf-8'))
fotos = json.load(open('photos.json', encoding='utf-8'))
src = open('index.html', encoding='utf-8').read()

# CSS do guia, para o roadbook ser indistinguível dele
css = re.search(r'<style>(.*?)</style>', src, re.S).group(1)

EXTRA = """
  .rb-cover{padding:56px 0 40px;border-bottom:1px solid var(--line)}
  .rb-kicker{font:600 11px/1 var(--sans);letter-spacing:.18em;text-transform:uppercase;color:var(--accent);margin:0 0 14px}
  .rb-cover h1{font:600 clamp(30px,5vw,52px)/1.05 var(--serif);margin:0 0 14px;letter-spacing:-.01em}
  .rb-cover .rb-lede{font:400 16px/1.65 var(--sans);color:var(--ink-soft);max-width:62ch;margin:0 0 22px}
  .rb-facts{display:flex;flex-wrap:wrap;gap:10px;margin:0}
  .rb-facts span{font:500 11.5px/1 var(--sans);letter-spacing:.08em;text-transform:uppercase;color:var(--ink-soft);
    border:1px solid var(--line);border-radius:999px;padding:8px 13px;background:var(--surface)}
  .rb-nav{position:sticky;top:0;z-index:9;background:color-mix(in srgb,var(--bg) 88%,transparent);
    backdrop-filter:blur(12px);border-bottom:1px solid var(--line);padding:9px 0;margin:0 0 8px;
    display:flex;gap:6px;overflow-x:auto;scrollbar-width:none}
  .rb-nav::-webkit-scrollbar{display:none}
  .rb-nav a{flex:0 0 auto;font:600 11.5px/1 var(--sans);letter-spacing:.04em;color:var(--ink-soft);
    text-decoration:none;padding:7px 10px;border-radius:7px;border:1px solid transparent}
  .rb-nav a:hover{color:var(--ink);background:var(--surface);border-color:var(--line)}
  .rb-day{padding:44px 0 8px;border-bottom:1px solid var(--line-soft);scroll-margin-top:64px}
  .rb-day:last-of-type{border-bottom:0}
  .rb-head{display:flex;flex-wrap:wrap;align-items:baseline;gap:14px;margin:0 0 6px}
  .rb-badge{font:700 11px/1 var(--mono);letter-spacing:.1em;color:#fff;background:var(--accent);
    border-radius:6px;padding:7px 9px}
  .rb-head h2{font:600 clamp(21px,3vw,30px)/1.2 var(--serif);margin:0;letter-spacing:-.01em}
  .rb-date{font:500 12px/1 var(--sans);letter-spacing:.1em;text-transform:uppercase;color:var(--ink-faint)}
  .rb-stats{display:flex;flex-wrap:wrap;gap:16px;margin:10px 0 16px;font:500 12.5px/1 var(--sans);color:var(--ink-soft)}
  .rb-stats b{color:var(--ink)}
  .rb-intro{font:400 15.5px/1.7 var(--sans);color:var(--ink);max-width:76ch;margin:0 0 20px}
  .rb-strip{display:flex;gap:10px;overflow-x:auto;padding:2px 0 12px;margin:0 0 8px;scroll-snap-type:x mandatory}
  .rb-strip{scrollbar-width:none}
  .rb-strip::-webkit-scrollbar{display:none}
  .rb-shot{flex:0 0 auto;width:290px;scroll-snap-align:start;margin:0}
  .rb-shot a{display:block;text-decoration:none}
  .rb-shot img{width:290px;height:186px;object-fit:cover;border-radius:9px;display:block;
    border:1px solid var(--line);background:var(--surface-2)}
  .rb-shot figcaption{font:500 11px/1.35 var(--sans);color:var(--ink-soft);margin:7px 0 0}
  .rb-shot figcaption b{display:block;color:var(--ink);font-size:12px;margin:0 0 2px}
  .rb-sleep{display:flex;gap:16px;align-items:flex-start;flex-wrap:wrap;background:var(--surface);
    border:1px solid var(--line);border-radius:11px;padding:14px;margin:18px 0 6px}
  .rb-sleep img{width:190px;height:124px;object-fit:cover;border-radius:8px;flex:0 0 auto;border:1px solid var(--line)}
  .rb-sleep .rb-txt{flex:1 1 300px;min-width:240px}
  .rb-sleep .lbl{font:600 10.5px/1 var(--sans);letter-spacing:.14em;text-transform:uppercase;color:var(--accent);display:block;margin:0 0 7px}
  .rb-sleep p{margin:0;font:400 14px/1.6 var(--sans);color:var(--ink-soft)}
  .rb-sleep b{color:var(--ink)}
  .rb-credits{padding:40px 0 60px}
  .rb-credits h2{font:600 20px/1.2 var(--serif);margin:0 0 6px}
  .rb-credits p{font:400 13px/1.6 var(--sans);color:var(--ink-soft);max-width:70ch}
  .rb-credits ol{columns:2;column-gap:34px;font:400 11.5px/1.55 var(--sans);color:var(--ink-faint);
    padding-left:18px;margin:14px 0 0}
  @media(max-width:640px){.rb-shot,.rb-shot img{width:240px}.rb-shot img{height:156px}
    .rb-sleep img{width:100%;height:170px}.rb-credits ol{columns:1}}
"""


def esc(t):
    return html.escape(t, quote=False)


def attr(t):
    return html.escape(t, quote=True)


# fotos por POI
por_poi = {k: v['fotos'] for k, v in fotos.items()}

# fotos de dormida: nome do alojamento -> ficheiro
DORMIR = {
    'Hardap': 'img/kalahari.jpg',
    'Quiver Tree': 'img/quiver.jpg',
    'Hobas': 'img/fishriver.jpg',
    'Shalom': 'img/luderitz.jpg',
    'Sesriem': 'img/sesriem.jpg',
    'Alternative Space': 'img/walvis.jpg',
    'Spitzkoppe': 'img/spitzkoppe.jpg',
    'Madisa': 'img/twyfelfontein.jpg',
    'Okaukuejo': 'img/etosha.jpg',
    'Halali': 'img/etosha2.jpg',
    'Waterberg': 'img/spitzkoppe.jpg',
    'Hahn': 'img/hero.jpg',
    'Frankfurt': 'img/hero.jpg',
    'Windhoek': 'img/hero.jpg',
}

CIDADE = {
    'Alternative Space B&B': 'Swakopmund — a cidade (imagem da vila, não do alojamento)',
    'Shalom': 'Lüderitz — a vila',
}

usados = []      # (ficheiro, autor, licenca, titulo, pagina)
vistos = set()


AREAS = {
    'dia-00': ['img/hero.jpg', 'img/kalahari.jpg'],
    'dia-01': ['img/kalahari.jpg', 'img/horses.jpg'],
    'dia-03': ['img/fishriver.jpg', 'img/quiver.jpg'],
    'dia-08': ['img/sesriem.jpg', 'img/dune45.jpg', 'img/solitaire.jpg'],
    'dia-13': ['img/etosha2.jpg', 'img/etosha.jpg'],
    'dia-15': ['img/hero.jpg', 'img/kalahari.jpg', 'img/solitaire.jpg'],
}
AREACAP = {
    'img/hero.jpg': ('Sossusvlei, o cartão de visita do país', 'Diego Delso', 'CC BY-SA 4.0'),
    'img/kalahari.jpg': ('O Kalahari a caminho do sul', 'Henning Sidow', 'CC BY-SA 4.0'),
    'img/horses.jpg': ('Cavalos do deserto em Garub', 'Raymond June', 'CC BY 2.0'),
    'img/fishriver.jpg': ('O meandro do Fish River Canyon', 'Thomas Schoch', 'CC BY-SA 3.0'),
    'img/quiver.jpg': ('Quiver Tree Forest, Keetmanshoop', 'Le Grand Portage', 'CC BY 2.0'),
    'img/sesriem.jpg': ('Sesriem e o acesso a Sossusvlei', 'Diego Delso', 'CC BY-SA 4.0'),
    'img/dune45.jpg': ('Duna 45, ao amanhecer', 'Diego Delso', 'CC BY-SA 4.0'),
    'img/solitaire.jpg': ('Solitaire, no cruzamento do Namib', 'Diego Delso', 'CC BY-SA 3.0'),
    'img/etosha.jpg': ('Etosha, os panos brancos', 'Diego Delso', 'CC BY-SA 4.0'),
    'img/etosha2.jpg': ('Etosha, a hora dourada', 'Diego Delso', 'CC BY-SA 4.0'),
}


def registar(f):
    if f['ficheiro'] not in vistos:
        vistos.add(f['ficheiro'])
        usados.append(f)


blocos = []
nav = []
for d in dias:
    num = d['num']                      # "Dia 07 · 20 dez · ⭐ Deserto"
    partes = [p.strip() for p in num.split('·')]
    dia = partes[0]
    data = partes[1] if len(partes) > 1 else ''
    tema = partes[2] if len(partes) > 2 else ''
    anc = re.sub(r'[^a-z0-9]+', '-', dia.lower()).strip('-')
    nav.append(f'<a href="#{anc}">{esc(dia.replace("Dia ", "D"))}</a>')

    # fotos do dia: POIs que aparecem nas linhas deste dia
    nomes = []
    for r in d['rows']:
        if r['mapa'] and r['mapa']['name'] not in nomes:
            nomes.append(r['mapa']['name'])
    figs = []
    for n in nomes:
        for f in por_poi.get(n, [])[:1]:
            if f['ficheiro'] in vistos:
                continue
            registar(f)
            rotulo = CIDADE.get(n, n)
            figs.append(
                f'<figure class="rb-shot"><a href="{attr(f["pagina"] or "#")}" target="_blank" rel="noopener">'
                f'<img src="{attr(f["ficheiro"])}" alt="{attr(rotulo)}" loading="lazy"></a>'
                f'<figcaption><b>{esc(rotulo)}</b><i>{esc(f["titulo"].replace("File:", ""))}</i> — {esc(f["autor"] or "autor não indicado")} · {esc(f["licenca"])}</figcaption></figure>')
            if len(figs) >= 10:
                break
        if len(figs) >= 10:
            break
    if len(figs) < 3:
        for caminho in AREAS.get(anc, []):
            if len(figs) >= 3 or not os.path.exists(caminho):
                break
            leg, aut, lic = AREACAP.get(caminho, ('', '', ''))
            figs.append(
                f'<figure class="rb-shot"><img src="{attr(caminho)}" alt="{attr(leg)}" loading="lazy">'
                f'<figcaption><b>{esc(leg)}</b><i>imagem da região</i> — {esc(aut)} · {esc(lic)}</figcaption></figure>')
    strip = f'<div class="rb-strip">{"".join(figs)}</div>' if figs else ''

    def limpa(x):
        x = x.replace('🚗', 'Km · ').replace('⏱', 'Tempo · ')
        x = re.sub(r'[\U0001F300-\U0001FAFF\u2600-\u27BF\uFE0F]', '', x)
        return re.sub(r'\s+', ' ', x).strip(' ·')
    leg = [limpa(x) for x in d['leg'][:3] if limpa(x)]
    stats = ' '.join(f'<span>{esc(x)}</span>' for x in leg)

    linhas = ''.join(
        f'<tr><td class="num">{esc(r["hora"])}</td><td>{esc(r["oque"])}</td><td>{esc(r["nota"])}</td></tr>'
        for r in d['rows'])

    notas = ''.join(
        f'<div class="note{" warn" if "aten" in n["titulo"].lower() or "!" in n["titulo"] else ""}">'
        f'<span class="lbl">{esc(n["titulo"])}</span>{esc(n["texto"])}</div>'
        for n in d['notas'] if n['titulo'])

    sp = ''
    if d['dormir']:
        texto_d = d.get('dormir_desc') or d['dormir']
        nome_d = d.get('dormir_nome') or (d.get('dormir_lbl') or '').replace('Dormir · ', '') or 'Sem cama'
        foto_d = ''
        for chave, caminho in DORMIR.items():
            if chave.lower() in (nome_d + ' ' + d['dormir']).lower() and os.path.exists(caminho):
                foto_d = caminho
                break
        texto_d = re.sub(r'^[\s,;.·—-]+', '', texto_d).strip()
        if texto_d and texto_d[0].islower():
            texto_d = texto_d[0].upper() + texto_d[1:]
        img_d = f'<img src="{attr(foto_d)}" alt="{attr(nome_d)}" loading="lazy">' if foto_d else ''
        sp = (f'<div class="rb-sleep">{img_d}<div class="rb-txt"><span class="lbl">Dormir · {esc(nome_d)}</span>'
              f'<p>{esc(texto_d)}</p></div></div>')

    blocos.append(f'''
      <section class="rb-day" id="{anc}">
        <div class="rb-head">
          <span class="rb-badge">{esc(dia.upper())}</span>
          <h2>{esc(d["titulo"])}</h2>
          <span class="rb-date">{esc(data)}{(" · " + esc(tema)) if tema else ""}</span>
        </div>
        <div class="rb-stats">{stats}</div>
        <p class="rb-intro">{esc(d["intro"])}</p>
        {strip}
        <div class="tablewrap" style="margin:16px 0 0">
          <table><thead><tr><th>Hora</th><th>O quê</th><th>Notas</th></tr></thead>
          <tbody>{linhas}</tbody></table>
        </div>
        {notas}
        {sp}
      </section>''')

creditos = ''.join(
    f'<li>{esc(f["titulo"].replace("File:", ""))} — {esc(f["autor"] or "autor não indicado")}, {esc(f["licenca"] or "ver ficheiro")}</li>'
    for f in usados)

html_out = f'''<!doctype html>
<html lang="pt-PT">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Namíbia 2026 — Roadbook</title>
<style>{css}{EXTRA}</style>
</head>
<body>
<div class="wrap">

  <header class="rb-cover">
    <p class="rb-kicker">Roadbook · 13 a 29 de dezembro de 2026 · <a href="index.html" style="color:var(--accent-ink);text-decoration:none">← dossier completo</a></p>
    <h1>Namíbia, dia a dia,<br>com os sítios à frente</h1>
    <p class="rb-lede">Um loop anti-horário a partir de Windhoek: Kalahari, Fish River, Kolmanskop, a costa dos ventos,
      Sossusvlei, o granito do Spitzkoppe, a pré-história do Damaraland e duas noites em Etosha. Cada dia traz as horas,
      o que se vê e as fotografias dos locais — para reconhecer no terreno o que se planou em casa.</p>
    <div class="rb-facts">
      <span>3 viajantes · 2 condutores</span>
      <span>16 dias · 15 noites</span>
      <span>1 Hilux 4x4 com 2 tendas de tejadilho</span>
      <span>{len(usados)} fotografias de {len({f["titulo"].split(":")[0] for f in usados})} autores</span>
    </div>
  </header>

  <nav class="rb-nav">{"".join(nav)}<a href="#creditos">Créditos</a></nav>
{"".join(blocos)}

  <section class="rb-credits" id="creditos">
    <h2>Créditos das fotografias</h2>
    <p>Todas as imagens vêm do Wikimedia Commons, sob as licenças indicadas. Os nomes dos ficheiros ligam à página
      original, onde estão a licença completa e o histórico. Onde a fotografia é da região e não do alojamento,
      a legenda di-lo — nenhuma imagem foi apresentada como sendo de um sítio que não é.</p>
    <ol>{creditos}</ol>
  </section>

</div>
</body>
</html>
'''

open('roadbook.html', 'w', encoding='utf-8').write(html_out)
print(f"roadbook.html: {len(html_out)/1024:.0f} KB | fotos usadas: {len(usados)} | dias: {len(blocos)}")
faltam = [k for k in por_poi if not por_poi[k]]
print("POIs sem foto:", faltam)
