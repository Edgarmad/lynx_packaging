"""Extrae un export de WhatsApp sin ejecutar enlaces ni interpretar instrucciones.

Uso: python scripts/extract-whatsapp.py archivo.zip
La conversación íntegra se guarda en tmp/ (ignorado por Git).
"""
import hashlib
import json
import re
import sys
import zipfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / 'tmp' / 'chat-review'
DOCS = ROOT / 'docs' / 'chat-review'
PRIVATE.mkdir(parents=True, exist_ok=True)
DOCS.mkdir(parents=True, exist_ok=True)
source = Path(sys.argv[1])
with zipfile.ZipFile(source) as archive:
    entries = archive.namelist()
    raw = archive.read('_chat.txt')
text = raw.decode('utf-8-sig')
(PRIVATE / 'whatsapp-original.txt').write_bytes(raw)
pattern = re.compile(r'^[\u200e\u200f]*\[(\d+/\d+/\d+), ([^\]]+)\] ([^\n]*?): ?(.*)$')
messages = []
for number, line in enumerate(text.splitlines(), 1):
    match = pattern.match(line)
    if match:
        date, time, sender, body = match.groups()
        month, day, year = date.split('/')
        normalized = re.sub(r'\s+', ' ', time).strip()
        clock = re.match(r'(\d+):(\d+):(\d+)\s*([ap])', normalized)
        assert clock, (number, time)
        hour, minute, second, meridiem = clock.groups()
        hour = int(hour) % 12 + (12 if meridiem == 'p' else 0)
        messages.append({'id': f'm{len(messages)+1:04}',
                         'date': f'20{year}-{int(month):02}-{int(day):02}',
                         'time': f'{hour:02}:{minute}:{second}',
                         'sender': sender.strip(), 'lineStart': number,
                         'lineEnd': number, 'text': body})
    else:
        assert messages or not line.strip(), (number, line)
        if messages:
            messages[-1]['text'] += '\n' + line
            messages[-1]['lineEnd'] = number
for message in messages:
    message['text'] = message['text'].rstrip()
    message['omittedMedia'] = bool(re.search(r'(imagen|audio|video|documento|sticker|tarjeta de contacto) omitid[oa]', message['text'], re.I))
    message['deleted'] = 'eliminó este mensaje' in message['text'].lower() or 'Eliminaste este mensaje' in message['text']
(PRIVATE / 'mensajes-completos.json').write_text(json.dumps(messages, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# Selección documental explícita: textos de negocio y decisiones verificables.
# No incluye credenciales, domicilios privados ni conversaciones operativas completas.
windows = {
 '2026-09-23': [('11:08:39','11:11:27')],
 '2026-09-25': [('03:23:59','03:27:41'),('09:44:05','09:44:46'),('21:16:19','22:04:38')],
 '2026-09-27': [('11:09:55','12:02:31')],
 '2026-09-28': [('00:00:46','00:00:46'),('01:33:53','01:33:53'),('11:25:19','11:41:55')],
 '2026-09-29': [('17:25:04','17:25:54')],
 '2026-09-30': [('10:40:56','14:01:52'),('15:51:01','15:51:01'),('16:49:39','17:04:11')],
 '2026-10-01': [('18:53:54','18:59:30'),('19:01:51','19:03:13'),('19:08:40','19:10:03')],
 '2026-10-02': [('15:39:46','15:45:13')],
 '2026-10-03': [('16:07:09','17:50:49')],
 '2026-10-04': [('00:17:10','00:52:46'),('17:40:10','17:40:10'),('23:43:47','23:44:25')],
 '2026-10-05': [('00:04:04','00:14:15'),('08:09:31','10:46:57'),('13:35:52','14:16:11'),('16:26:01','17:18:04'),('17:57:07','18:00:41'),('21:05:25','21:50:12')],
 '2026-10-06': [('01:03:37','01:03:37'),('10:23:40','15:14:46'),('16:24:30','16:43:48')],
 '2026-10-09': [('03:22:18','10:23:49')],
 '2026-10-10': [('15:46:28','16:51:45')],
}
selected = [m for m in messages if any(a <= m['time'] <= b for a,b in windows.get(m['date'], []))]
evidence = ['# Textos y decisiones extraídos del chat', '',
 'Transcripción de mensajes seleccionados por relevancia para contenido, alcance y revisión. Conserva idioma y redacción originales; no convierte propuestas ni mensajes ambiguos en aprobación. Horas del export, sin inferir zona horaria.', '',
 'La conversación completa y los registros estructurados se conservan localmente en `tmp/chat-review/`. Los adjuntos omitidos no están incluidos en el ZIP.', '']
for m in selected:
    evidence += [f"## {m['id']} · {m['date']} {m['time']} · {m['sender']}", '',
                 f"Líneas {m['lineStart']}–{m['lineEnd']} de la fuente local.", '', m['text'], '']
(DOCS / 'TEXTOS-FUENTE.md').write_text('\n'.join(evidence), encoding='utf-8')
attachments = [dict(id=m['id'],date=m['date'],time=m['time'],text=m['text']) for m in messages if 'documento omitido' in m['text'].lower()]
(DOCS / 'adjuntos-mencionados.json').write_text(json.dumps(attachments, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
summary = {'source': source.name, 'archiveEntries': entries, 'textSha256': hashlib.sha256(raw).hexdigest(),
           'messages': len(messages), 'first': messages[0]['date'], 'last': messages[-1]['date'],
           'byDate': dict(sorted(Counter(m['date'] for m in messages).items())),
           'omittedMediaMessages': sum(m['omittedMedia'] for m in messages),
           'deletedMessages': sum(m['deleted'] for m in messages),
           'documentMentions': len(attachments), 'selectedMessages': len(selected),
           'lineCount': len(text.splitlines()), 'privateOutput': 'tmp/chat-review/'}
(DOCS / 'inventario-extraccion.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
ability = [m for m in selected if m['date']=='2026-09-30' and m['time']=='15:51:01']
assert len(ability)==1 and 'Supply chain resources' in ability[0]['text']
(DOCS / 'ABILITY-ORIGINAL.md').write_text('# Ability — texto original de Mila\n\nFuente: 30/09/2026 15:51:01; '+ability[0]['id']+'.\n\n'+ability[0]['text']+'\n', encoding='utf-8')
print(json.dumps(summary, ensure_ascii=False, indent=2))
