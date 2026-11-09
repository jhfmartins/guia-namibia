#!/usr/bin/env python3
"""Extrai os dias do index.html para JSON, para alimentar o roadbook."""
import re, json, html

s = open('index.html', encoding='utf-8').read()
marc = [m.start() for m in re.finditer(r'<div class="day-num">', s)]
dias = []
for k, i in enumerate(marc):
    fim = marc[k+1] if k+1 < len(marc) else s.index('<section', i)
    b = s[i:fim]

    def txt(x):
        x = re.sub(r'<[^>]+>', ' ', x)
        return html.unescape(re.sub(r'\s+', ' ', x)).strip()

    num = txt(re.search(r'<div class="day-num">(.*?)</div>', b, re.S).group(1))
    h3 = txt(re.search(r'<h3>(.*?)</h3>', b, re.S).group(1))
    leg = [txt(x) for x in re.findall(r'<span>(.*?)</span>', b, re.S)]
    intro_m = re.search(r'</div>\s*<p>(.*?)</p>', b, re.S)
    intro = txt(intro_m.group(1)) if intro_m else ''
    rows = []
    for tr in re.findall(r'<tr><td class="num">.*?</tr>', b, re.S):
        cels = re.findall(r'<td[^>]*>(.*?)</td>', tr, re.S)
        if len(cels) < 3:
            continue
        mapa = ''
        mm = re.search(r'<a href="([^"]+)"[^>]*title="([^"]*)"', tr)
        if mm:
            mapa = {'url': mm.group(1), 'name': mm.group(2)}
        rows.append({'hora': txt(cels[0]), 'oque': txt(cels[1]), 'nota': txt(cels[2]), 'mapa': mapa})
    notas = []
    for n in re.findall(r'<div class="note[^"]*"[^>]*>(.*?)</div>\s*(?=<div|<p|</div>)', b, re.S):
        lbl = re.search(r'<span class="lbl">(.*?)</span>', n, re.S)
        corpo = re.sub(r'<span class="lbl">.*?</span>', '', n, flags=re.S)
        notas.append({'titulo': txt(lbl.group(1)) if lbl else '', 'texto': txt(corpo)})
    sono, sono_lbl, sono_nome, sono_desc = '', '', '', ''
    sm = re.search(r'<div class="sleep">(.*?)</div>', b, re.S)
    if sm:
        bloco = sm.group(1)
        lm = re.search(r'<span class="lbl">(.*?)</span>', bloco, re.S)
        sono_lbl = txt(lm.group(1)) if lm else ''
        resto = bloco[lm.end():] if lm else bloco
        bm = re.search(r'<b>(.*?)</b>', resto, re.S)
        if bm:
            sono_nome = txt(bm.group(1))
            sono_desc = txt(resto[bm.end():])
        else:
            sono_desc = txt(resto)
        sono = txt(bloco)
    dias.append({'num': num, 'titulo': h3, 'leg': leg, 'intro': intro,
                 'rows': rows, 'notas': notas, 'dormir': sono,
                 'dormir_lbl': sono_lbl, 'dormir_nome': sono_nome, 'dormir_desc': sono_desc})

json.dump(dias, open('days.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

print(f"dias: {len(dias)}")
tot = sum(len(d['rows']) for d in dias)
print(f"linhas: {tot}")
pois = []
for d in dias:
    for r in d['rows']:
        if r['mapa']:
            pois.append(r['mapa']['name'])
print(f"POIs com link: {len(pois)} únicos: {len(set(pois))}")
for d in dias:
    print(f"  {d['num'][:22]:<24} {d['titulo'][:44]:<46} {len(d['rows']):>2} linhas")
