#!/usr/bin/env python3
"""Vai buscar fotos de licença livre ao Wikimedia Commons para cada POI do roteiro."""
import json, re, os, math, time, urllib.parse, urllib.request

UA = "NamibiaRoadbook/1.0 (personal trip guide; contact jhf.martins@gmail.com)"
API = "https://commons.wikimedia.org/w/api.php"
OUT = "img/rb"
os.makedirs(OUT, exist_ok=True)

BAD = re.compile(r'(map|karte|diagram|logo|flag|coat|chart|plan\b|svg|graph|schema|banner|screenshot'
                 r'|iss0|view of earth|license plate|licence plate|kennzeichen|schild|nummerschild'
                 r'|passport|banknote|coin\b|stamp\b|document|poster|book cover)', re.I)
OK_MIME = ('image/jpeg', 'image/png')


def get(params):
    params.update({'format': 'json', 'formatversion': '2'})
    url = API + '?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    for tent in range(3):
        try:
            with urllib.request.urlopen(req, timeout=45) as f:
                return json.load(f)
        except Exception:
            time.sleep(2 + tent * 2)
    return {}


def info(titles):
    if not titles:
        return {}
    d = get({'action': 'query', 'titles': '|'.join(titles), 'prop': 'imageinfo',
             'iiprop': 'url|extmetadata|size|mime', 'iiurlwidth': '1500'})
    out = {}
    for p in (d.get('query', {}) or {}).get('pages', []) or []:
        ii = (p.get('imageinfo') or [{}])[0]
        if not ii:
            continue
        out[p['title']] = ii
    return out


def search_text(q, limit=8):
    d = get({'action': 'query', 'generator': 'search', 'gsrsearch': q,
             'gsrnamespace': '6', 'gsrlimit': str(limit), 'prop': 'imageinfo|coordinates',
             'iiprop': 'url|extmetadata|size|mime', 'iiurlwidth': '1500'})
    return [p for p in (d.get('query', {}) or {}).get('pages', []) or []]


def search_geo(lat, lon, radius=4000, limit=15):
    d = get({'action': 'query', 'generator': 'geosearch', 'ggscoord': f'{lat}|{lon}',
             'ggsradius': str(radius), 'ggslimit': str(limit), 'ggsnamespace': '6',
             'prop': 'imageinfo|coordinates', 'iiprop': 'url|extmetadata|size|mime', 'iiurlwidth': '1500'})
    return [p for p in (d.get('query', {}) or {}).get('pages', []) or []]


def clean(v):
    if not v:
        return ''
    v = re.sub(r'<[^>]+>', '', v)
    return re.sub(r'\s+', ' ', v).strip()


def hav(a, b):
    R = 6371.0
    p1, p2 = math.radians(a[0]), math.radians(b[0])
    dp, dl = p2 - p1, math.radians(b[1] - a[1])
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))


def geo_ok(p, lat, lon, maxkm=6.0):
    c = (p.get('coordinates') or [{}])[0]
    if not c.get('lat'):
        return None
    return hav((lat, lon), (c['lat'], c['lon'])) <= maxkm


STOP = {'foto', 'file', 'the', 'and', 'namibia', 'namibie', 'namibias', 'view', 'vista',
        'panoramio', 'africa', 'south', 'west', 'park', 'national'}


def token_ok(p, nome):
    def toks(t):
        t = re.sub(r'[^a-zA-ZÀ-ÿ0-9 ]+', ' ', t.lower())
        return {w for w in t.split() if len(w) > 3 and w not in STOP}
    return bool(toks(nome) & toks(p['title']))


BINOM = re.compile(r'\b[A-Z][a-z]{3,}\s+[a-z]{3,}\b')


def parece_nome_cientifico(t):
    return bool(BINOM.search(t.replace('File:', '')))


def search_cats(q, limit=8):
    d = get({'action': 'query', 'list': 'search', 'srsearch': q,
             'srnamespace': '14', 'srlimit': str(limit)})
    return [x['title'] for x in (d.get('query', {}) or {}).get('search', []) or []]


def cat_files(cat, limit=25):
    d = get({'action': 'query', 'generator': 'categorymembers', 'gcmtitle': cat,
             'gcmtype': 'file', 'gcmlimit': str(limit), 'prop': 'imageinfo|coordinates',
             'iiprop': 'url|extmetadata|size|mime', 'iiurlwidth': '1500'})
    return [p for p in (d.get('query', {}) or {}).get('pages', []) or []]


def usable(p):
    ii = (p.get('imageinfo') or [{}])[0]
    if not ii:
        return False
    if ii.get('mime') not in OK_MIME:
        return False
    if (ii.get('width') or 0) < 1100:
        return False
    if BAD.search(p['title']):
        return False
    if parece_nome_cientifico(p['title']):
        return False
    return True


def slug(t):
    t = re.sub(r'[^a-zA-Z0-9]+', '-', t).strip('-').lower()
    return t[:48]


def download(url, path):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=90) as f:
        data = f.read()
    open(path, 'wb').write(data)
    return len(data)


def main():
    dias = json.load(open('days.json', encoding='utf-8'))
    pois = {}
    for d in dias:
        for r in d['rows']:
            m = r['mapa']
            if not m:
                continue
            c = re.search(r'query=([-\d.]+),([-\d.]+)', m['url'])
            if not c:
                continue
            pois.setdefault(m['name'], {'lat': float(c.group(1)), 'lon': float(c.group(2)),
                                        'dia': d['num'][:6]})
    print(f"POIs: {len(pois)}")
    OVERRIDE = {
        'Organ Pipes e Burnt Mountain': 'Organ Pipes Twyfelfontein Damaraland',
        'Aus — depósito cheio': 'Aus Namibia',
        'Trópico de Capricórnio': 'Tropic of Capricorn Namibia',
        'Trópico de Capricórnio (C14)': 'Tropic of Capricorn sign Namibia',
        'Canyon Roadhouse': 'Canyon Roadhouse Fish River Namibia',
    }
    FORCE_CAT = {
        'Sesriem Camp': 'Category:Sesriem Camp Site',
        'Portão interior de Sesriem': 'Category:Sesriem Camp Site',
        'Walvis Bay — lagoa': 'Category:Walvis Bay',
        'Uis': 'Category:Uis, Namibia',
        'Outjo': 'Category:Outjo',
        'Namutoni': 'Category:Namutoni, Namibia',
        'Diaz Point ao pôr do sol': 'Category:Diaz Point',
        'Canyon Roadhouse': 'Category:Canyon Roadhouse',
        'Halali': 'Category:Halali Camp',
        'Halali Camp': 'Category:Halali Camp',
        'Garub — cavalos selvagens': 'Category:Namib Desert Horse',
        'Twyfelfontein': 'Category:Twyfelfontein',
        'Elim Dune': 'Category:Sossusvlei',
        'Windhoek — devolver o 4x4': 'Category:Windhoek',
        'Hosea Kutako — aterragem': 'Category:Hosea Kutako International Airport',
        'Spitzkoppe ticket office': 'Category:Spitzkoppe',
        'Spot fora da vedação': 'Category:Spitzkoppe',
        'Keetmanshoop': 'Category:Keetmanshoop',
        'Lüderitz, centro a pé': 'Category:Lüderitz',
        'Lüderitz: compras no Spar': 'Category:Lüderitz',
        'Aus': 'Category:Aus, Namibia',
        'Otjiwarongo': 'Category:Otjiwarongo',
        'Zeila': 'Category:Zeila (ship)',
        'Passo do Kuiseb': 'Category:Kuiseb',
        'Cape Cross': 'Category:Cape Cross',
        'Okaukuejo Camp': 'Category:Okaukuejo',
        'Waterberg Camp': 'Category:Waterberg Plateau Park',
        'Anderson Gate': 'Category:Etosha National Park',
    }
    MANUAL = {
        'Elim Dune': 'File:Duna Elim, Sossusvlei, Namibia, 2018-08-06, DD 163.jpg',
        'Zeila': 'File:Schiffswrack Zeila, Namibia 2014.jpg',
        'Keetmanshoop': 'File:Kirche Keetmanshoop.jpg',
        'Halali': 'File:Moringa Pan (Halali Camp, Etosha) 19990804 JoRoRe.jpg',
        'Halali Camp': 'File:Moringa Pan (Halali Camp, Etosha) 19990804 JoRoRe.jpg',
        'Shark Island': 'File:Shark Island 01.jpg',
        'Big Daddy — subida': 'File:BigDaddyDune.jpg',
        'Duna 45': 'File:006 Dune 45 in Sossusvlei at sunrise Photo by Giles Laurent.jpg',
        'Duna 7': 'File:Dune 7 (July 2018) 01.jpg',
        'Sesriem Canyon': 'File:Namibie Sesriem Canyon 01.JPG',
        'Solitaire': 'File:Solitaire, Namibia03.jpg',
        'Khorixas': 'File:Khorixas housing.jpg',
        'Waterberg Camp': 'File:Waterberg, Namibia Luftaufnahme von Osten.jpg',
        'Grosse Bucht': 'File:Luderitz, Diaz-Point, Grosse Bucht.jpg',
        'Organ Pipes e Burnt Mountain': 'File:NA Twy Orhan pipes.JPG',
        'Aus': 'File:Aus Namibia (2018).jpg',
        'Aus — depósito cheio': 'File:Aus Namibia (2018).jpg',
        'Lüderitz, centro a pé': 'File:Krabbenhöft & Lampe Building in Lüderitz, Namibia.jpg',
        'Lüderitz: compras no Spar': 'File:Berg Street (18636357723).jpg',
        'Campo de prisioneiros de 1915': 'File:Kirche in Aus Namibia.jpg',
    }
    res = {}
    for nome, meta in pois.items():
        cand, rejeitadas = [], 0
        qnome = OVERRIDE.get(nome, nome)
        if nome in MANUAL:
            d = info([MANUAL[nome]])
            for tit, ii in d.items():
                cand.append((0, {'title': tit, 'imageinfo': [ii]}))
        # (1) categoria forçada: curada à mão para os sítios onde a geo falha
        if nome in FORCE_CAT:
            fila = [p for p in cat_files(FORCE_CAT[nome], limit=50) if usable(p)]
            toks = {t for t in re.findall(r'[a-zà-ÿ]{4,}', qnome.lower()) if t not in STOP}
            fila.sort(key=lambda p: (sum(1 for x in toks if x in p['title'].lower()),
                                     -len(p['title'])), reverse=True)
            if fila:
                cand.append((0, fila[0]))
        # (2) categorias sugeridas pela pesquisa
        if not cand:
            for cat in search_cats(qnome.split(' — ')[0]):
                chave = [t for t in re.findall(r'[a-zà-ÿ]{4,}', qnome.lower())
                         if t in cat.lower()]
                if not chave:
                    continue
                fila = [p for p in cat_files(cat) if usable(p)]
                if not fila:
                    continue
                toks = {t for t in re.findall(r'[a-zà-ÿ]{4,}', qnome.lower())
                        if t not in STOP}
                def score(p):
                    t = p['title'].lower()
                    return sum(1 for x in toks if x in t)
                fila.sort(key=score, reverse=True)
                if score(fila[0]) == 0:
                    continue
                cand.append((0, fila[0]))
                break
        # (3) geolocalização, com token no título
        if not cand:
            for p in search_geo(meta['lat'], meta['lon']):
                if not usable(p):
                    continue
                ok = geo_ok(p, meta['lat'], meta['lon'])
                if ok is False or (ok is None and not token_ok(p, nome)):
                    rejeitadas += 1
                    continue
                cand.append((1, p))
        # (4) pesquisa textual
        if not cand:
            for p in search_text(qnome.split(' — ')[0]):
                if not usable(p) or p['title'] in {c[1]['title'] for c in cand}:
                    continue
                if not token_ok(p, qnome) or geo_ok(p, meta['lat'], meta['lon'], 30) is False:
                    rejeitadas += 1
                    continue
                cand.append((1, p))
        escolhidos, vistos = [], set()
        for rank, p in cand:
            if p['title'] in vistos:
                continue
            vistos.add(p['title'])
            ii = p['imageinfo'][0]
            em = ii.get('extmetadata', {})
            escolhidos.append({
                'titulo': p['title'],
                'thumb': ii.get('thumburl') or ii.get('url'),
                'pagina': ii.get('descriptionurl'),
                'autor': clean(em.get('Artist', {}).get('value', ''))[:90],
                'licenca': clean(em.get('LicenseShortName', {}).get('value', '')),
            })
            if len(escolhidos) >= 1:
                break
        ficheiros = []
        for n, e in enumerate(escolhidos, 1):
            fn = f"{slug(nome)}-{n}.jpg"
            path = os.path.join(OUT, fn)
            if not os.path.exists(path):
                try:
                    download(e['thumb'], path)
                except Exception as ex:
                    print(f"   ! falha {fn}: {ex}")
                    continue
            e['ficheiro'] = f"{OUT}/{fn}"
            ficheiros.append(e)
            time.sleep(0.2)
        res[nome] = {'dia': meta['dia'], 'fotos': ficheiros}
        print(f"  {meta['dia']} {nome[:34]:<36} {len(ficheiros)} fotos")
    json.dump(res, open('photos.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    total = sum(len(v['fotos']) for v in res.values())
    vazios = [k for k, v in res.items() if not v['fotos']]
    print(f"\ntotal imagens: {total} | POIs sem foto: {len(vazios)}")
    for v in vazios:
        print("   sem foto:", v)


if __name__ == '__main__':
    main()
