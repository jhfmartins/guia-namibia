#!/usr/bin/env python3
"""Reescreve a checklist de preparação por estado real: fechado, falta, véspera."""
import re

p = 'index.html'
s = open(p, encoding='utf-8').read()

ini = s.index('<!-- AX2 CHECKLIST PREP -->')
fim = s.index('</section>', ini)

def linha(texto, feito=False):
    marca = ' checked' if feito else ''
    return f'        <label><input type="checkbox"{marca}> {texto}</label>\n'

grupos = [
    ("Já está fechado", [
        ("<b>Voos dos três</b> — OPO 13 dez 07:20 → Hahn · Frankfurt 22:00 → Windhoek 14 dez 09:25 · regresso 28 dez 20:00, Hahn → OPO 29 dez", True),
        ("<b>Autocarro Hahn ↔ Frankfurt</b> — flibco, €131,94, 13 dez 12:15 e 29 dez 17:20", True),
        ("<b>4x4 Asco pago na totalidade</b> — €1.418,25, duas tendas de tejadilho, dois condutores nomeados. Super Cover recusado: franquia de N$40.000 assume-se", True),
        ("<b>Três vistos emitidos</b> — N$1.600 cada, válidos para as datas de entrada", True),
        ("<b>NWR liquidada</b> — N$11.520 pelas sete noites; factura e recibo recebidos a 9 de novembro, saldo zero", True),
        ("<b>Hardap N$660 e Madisa N$865,20 pagos</b> — Madisa com jantar de Natal incluído", True),
        ("<b>Kolmanskop</b> — três Day Pass, N$1.440. Não precisa de código: há segurança 24 h no portão", True),
        ("<b>Duas cartas internacionais</b> — emitidas a 25 de novembro em Ħal Lija, €66,50", True),
        ("<b>Seguros</b> — Cláudia e Sofia na Heymondo (apólice 2658815, €117,32); Henrique no Revolut Metal", True),
        ("<b>Shalom e Alternative Space</b> — reservados, pagam-se à chegada", True),
    ]),
    ("O que falta, por ordem de risco", [
        "<b>Consulta do viajante ×3 e receita da malária</b> (Malarone para 23 dez–3 jan). É o único item clínico em aberto e o único que depende de um médico — marcar para a semana de 1 de dezembro",
        "<b>Quiver Tree (15 dez)</b> — sem reserva, por decisão: paga-se em dinheiro à chegada, ~N$660",
        "<b>Certificado do Revolut</b> — o actual caduca a 8 de dezembro. Descarregar o novo <b>depois</b> dessa data e antes de 13, e guardá-lo offline",
        "<b>Plafond do cartão</b> — garantir N$40.000 (≈€2.143) livres a 14 de dezembro para o depósito da Asco, e um segundo cartão de rede diferente",
        "<b>Numerário</b> — N$11.000–12.000, porque as taxas de parque são só em dinheiro em vários portões",
    ]),
    ("Na véspera, 8 a 12 de dezembro", [
        "<b>Check-in dos três voos</b> e lugar marcado para quem quer janela",
        "<b>Cópias offline de tudo</b> — passaportes, cartas e IDPs, apólices, reservas, no iPad e no telemóvel",
        "<b>Mapas offline</b> — OsmAnd com a Namíbia descarregada, KML e GPX importados, testados em modo de avião",
        "<b>Avisar os bancos</b> das datas e destinos, para não bloquearem o cartão em Windhoek",
        "<b>Partilhar o itinerário</b> noite a noite com alguém em Portugal",
        "<b>Dividir tarefas</b> — quem cozinha, quem monta tendas, quem trata do carro e do abastecimento",
    ]),
]

novo = ['    <!-- AX2 CHECKLIST PREP -->\n    <section id="ax2">\n',
        '      <div class="sec-head"><span class="num">B</span><div><h2>Checklist de preparação</h2></div></div>\n',
        '      <div class="check">\n']
for titulo, itens in grupos:
    novo.append(f'        <div class="h">{titulo}</div>\n')
    for item in itens:
        if isinstance(item, tuple):
            novo.append(linha(item[0], item[1]))
        else:
            novo.append(linha(item))
novo.append('      </div>\n    </section>')

s = s[:ini] + ''.join(novo) + s[fim + len('</section>'):]

# nota anterior: já não se orçamenta seguro nem cartas
s = s.replace('Continuam por orçamentar o seguro de viagem, as vacinas e profilaxia, e as duas cartas internacionais.',
              'Seguros e cartas internacionais estão fechados; falta só a profilaxia da malária.')

open(p, 'w', encoding='utf-8').write(s)
print('checklist reescrita · itens:', sum(len(i) for _, i in grupos))
