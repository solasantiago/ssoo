#!/usr/bin/env python3
"""Genera el PDF de la guía (guias/*.md) para imprimir: color, fórmulas en LaTeX (KaTeX), números
de página, cada capítulo y cada bloque en hoja nueva, y títulos que no quedan sueltos al pie.
Usa el Chrome de Windows en modo headless y deja el PDF en guias/pdf/.

  python3 guia-pdf.py          un PDF por cada capítulo con contenido (guias/pdf/<ABR>-capNN.pdf)
                               y el índice (guias/pdf/<ABR>-indice.pdf, desde guias/README.md);
                               <ABR> es la abreviatura de la materia en lumen.json
  python3 guia-pdf.py 3 5      solo los capítulos 3 y 5, cada uno en su PDF
"""
import json, re, shutil, subprocess, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
TMP_WIN = 'C:\\Users\\admin\\AppData\\Local\\Temp'
TMP = Path('/mnt/c/Users/admin/AppData/Local/Temp')
CHROME = '/mnt/c/Program Files/Google/Chrome/Application/chrome.exe'
ABR = json.loads((REPO / 'lumen.json').read_text()).get('abreviatura', 'guia')

CSS = r"""
:root { --azul:#1d4e89; --azul-claro:#e8f0fa; --ambar:#b7791f; --ambar-claro:#fff8e1;
        --rojo:#b3261e; --rojo-claro:#fdecea; --verde:#2e7d32; --verde-claro:#edf7ee; --gris:#666; }
@page { size: A4; margin: 14mm 14mm 16mm 14mm; }
/* número de página del lado de afuera: impares abajo a la derecha, pares abajo a la izquierda */
@page :right { @bottom-right { content: counter(page) " / " counter(pages); font-family: "Segoe UI", Arial, sans-serif;
                               font-size: 8.5pt; color: #666; } }
@page :left  { @bottom-left  { content: counter(page) " / " counter(pages); font-family: "Segoe UI", Arial, sans-serif;
                               font-size: 8.5pt; color: #666; } }
body { font-family: "Segoe UI", Calibri, Arial, sans-serif; font-size: 10.5pt; line-height: 1.4; color: #111; }
section.capitulo + section.capitulo, section.indice + section.capitulo { break-before: page; }
.indice h1 { font-size: 20pt; color: var(--azul); margin: 0 0 6pt; }
.indice h2 { font-size: 14pt; color: var(--azul); border-bottom: 1pt solid var(--azul); padding-bottom: 2pt;
             margin: 16pt 0 6pt; break-after: avoid; }
.capitulo h1 { font-size: 17pt; color: var(--azul); border-bottom: 2pt solid var(--azul); padding-bottom: 3pt;
               margin: 0 0 8pt; }
.capitulo h2 { font-size: 13.5pt; color: var(--azul); border-left: 5pt solid var(--azul); padding: 2pt 0 2pt 7pt;
               margin: 14pt 0 4pt; break-after: avoid; }
.capitulo h3 { font-size: 11pt; color: var(--azul); text-transform: uppercase; letter-spacing: .04em;
               margin: 14pt 0 4pt; break-after: avoid; }
.capitulo h4 { font-size: 10.5pt; margin: 12pt 0 4pt; break-after: avoid; }
.junto { break-inside: avoid; }
p, li { orphans: 3; widows: 3; }
.estrellas { color: var(--ambar); letter-spacing: .05em; white-space: nowrap; }
.cuenta { color: var(--gris); font-weight: normal; font-size: .8em; white-space: nowrap; }
p { margin: 5pt 0; }
p > strong:first-child, li > strong:first-child { color: var(--azul); }
.lumen { color: var(--gris); font-size: 8.5pt; }
.lumen code { background: none; }
.ojo { color: var(--rojo); font-weight: bold; }
pre { font-family: "Cascadia Mono", Consolas, "Courier New", monospace; font-size: 8.4pt; line-height: 1.25;
      background: #f4f6f8; border: .5pt solid #c9d1d9; border-radius: 3pt; padding: 5pt 7pt;
      white-space: pre-wrap; break-inside: avoid; margin: 5pt 0 8pt; }
.mate { margin: 6pt 0; break-inside: avoid; }
.katex-display { overflow: visible !important; margin: 4pt 0; }
/* en pantalla, el contenido mide lo mismo que en la hoja A4 (210 − 2 × 14 mm), para medir bien */
@media screen { #c { width: 182mm; } }
/* nada se sale del ancho del contenido (así Chrome no achica la página al imprimir) */
html, body, #c, section { overflow-x: clip; }
.katex svg { overflow: hidden; }
.katex { font-size: 1.08em; }
div.mate.formulas { background: var(--ambar-claro); border: 1pt solid var(--ambar); border-radius: 3pt; padding: 2pt 6pt; }
pre.formulas { background: var(--ambar-claro); border: 1pt solid var(--ambar); }
code { font-family: "Cascadia Mono", Consolas, monospace; font-size: 9pt; }
.ok { color: var(--verde); font-weight: bold; }
.mal { color: var(--rojo); font-weight: bold; }
.blanco { color: var(--azul); font-weight: bold; }
blockquote { margin: 6pt 0; padding: 5pt 9pt; border-left: 4pt solid var(--verde); background: var(--verde-claro);
             break-inside: avoid; }
blockquote p { margin: 2pt 0; }
ul.trampas { background: var(--rojo-claro); border-left: 4pt solid var(--rojo); padding: 5pt 9pt 5pt 22pt; }
ul.trampas li > strong:first-child { color: var(--rojo); }
.titulo-cierre { color: var(--ambar); }
table { border-collapse: collapse; margin: 6pt 0; font-size: 9.5pt; break-inside: avoid; }
th { background: var(--azul-claro); color: var(--azul); }
th, td { border: .5pt solid #9aa5b1; padding: 3pt 5pt; vertical-align: top; text-align: left; }
ul, ol { margin: 4pt 0; padding-left: 18pt; }
li { margin: 2pt 0; }
em { color: #333; }
"""

JS = r"""
const mates = [];
const guardar = (tex, bloque) => { mates.push({tex, bloque}); return `@@M${mates.length - 1}@@`; };
function render(md) {
let fuente = md.replace(/\$\$([\s\S]+?)\$\$/g, (m, tex) => '\n\n' + guardar(tex, true) + '\n\n')
               .replace(/\$([^$\n]+?)\$/g, (m, tex) => guardar(tex, false));
let html = marked.parse(fuente);
html = html.replace(/<p>@@M(\d+)@@<\/p>/g, (m, i) =>
  `<div class="mate">${katex.renderToString(mates[i].tex, {displayMode: true, throwOnError: false, strict: false, output: 'html'})}</div>`);
html = html.replace(/@@M(\d+)@@/g, (m, i) =>
  katex.renderToString(mates[i].tex, {displayMode: mates[i].bloque, throwOnError: false, strict: false, output: 'html'}));
return html;
}
const c = document.getElementById('c'); c.innerHTML = '';
for (const a of archivos) {
  const s = document.createElement('section'); s.className = a.tipo; s.innerHTML = render(a.md); c.appendChild(s);
}
document.querySelectorAll('details').forEach(d => d.open = true);
// estrellas y cuenta en los títulos
document.querySelectorAll('h2, h4, td').forEach(h => {
  h.innerHTML = h.innerHTML.replace(/([★☆]{5})(\s*\([^)]*\))?/g,
    (m, s, c) => `<span class="estrellas">${s}</span>` + (c ? `<span class="cuenta">${c}</span>` : ''));
});
// línea de temas en Lumen
document.querySelectorAll('p').forEach(p => {
  if (p.textContent.startsWith('Temas en Lumen')) p.classList.add('lumen');
  p.innerHTML = p.innerHTML.replace(/\bOjo:/g, '<span class="ojo">Ojo:</span>');
});
document.querySelectorAll('li').forEach(li => {
  li.innerHTML = li.innerHTML.replace(/\bOjo:/g, '<span class="ojo">Ojo:</span>');
});
// cierre: fórmulas y trampas
document.querySelectorAll('p > strong:first-child').forEach(s => {
  const p = s.parentElement, t = s.textContent.trim();
  if (p.textContent.trim().startsWith('Fórmulas')) {
    s.classList.add('titulo-cierre');
    let n = p.nextElementSibling;
    while (n && (n.tagName === 'PRE' || n.classList.contains('mate'))) { n.classList.add('formulas'); n = n.nextElementSibling; }
  }
  if (t === 'Trampas') {
    s.classList.add('titulo-cierre');
    let n = p.nextElementSibling; if (n && n.tagName === 'UL') n.classList.add('trampas');
  }
  if (t.startsWith('Autoevaluación')) s.classList.add('titulo-cierre');
});
// mantener con el siguiente: títulos, rótulos del cierre y frases que presentan algo
const esContenido = el => el && !/^H[1-6]$/.test(el.tagName) && !el.classList.contains('lumen') && !esRotulo(el);
function esRotulo(el) {
  if (!el || el.tagName !== 'P') return false;
  const s = el.firstElementChild, txt = el.textContent.trim();
  return (s && s.tagName === 'STRONG' && s.textContent.trim() === txt.replace(/\s*\(.*\)$/, '')) || false;
}
const presenta = el => el && el.tagName === 'P' && /[:.]$/.test(el.textContent.trim()) &&
  el.textContent.length < 400 && /^(PRE|BLOCKQUOTE|UL|OL|TABLE|DIV)$/.test((el.nextElementSibling || {}).tagName || '');
// las fórmulas seguidas (varios $$ uno debajo del otro) viajan juntas
function sumarMates(grupo) {
  let n = grupo[grupo.length - 1].nextElementSibling;
  while (grupo[grupo.length - 1].classList.contains('mate') && n && n.classList.contains('mate')) {
    grupo.push(n); n = n.nextElementSibling;
  }
}
function agrupar(inicio) {
  const grupo = [inicio];
  let n = inicio.nextElementSibling;
  while (n && !esContenido(n)) { grupo.push(n); n = n.nextElementSibling; }  // títulos, temas en Lumen, rótulos
  if (n) {
    grupo.push(n);                                                          // primer contenido
    if (presenta(n)) grupo.push(n.nextElementSibling);                      // y lo que presenta
    sumarMates(grupo);
  }
  const caja = document.createElement('div'); caja.className = 'junto';
  inicio.parentNode.insertBefore(caja, inicio);
  grupo.forEach(el => caja.appendChild(el));
}
for (const c0 of document.querySelectorAll('section')) {
  [...c0.querySelectorAll(':scope > h1, :scope > h2, :scope > h3, :scope > h4')].forEach(h => {
    if (h.parentNode === c0 && !(h.previousElementSibling && /^H[1-6]$/.test(h.previousElementSibling.tagName))) agrupar(h);
  });
  [...c0.querySelectorAll(':scope > p')].forEach(p => {
    if (p.parentNode !== c0) return;
    if (esRotulo(p) && !(p.previousElementSibling && esRotulo(p.previousElementSibling))) agrupar(p);
    else if (presenta(p)) {
      const caja = document.createElement('div'); caja.className = 'junto';
      const grupo = [p, p.nextElementSibling]; sumarMates(grupo);
      p.parentNode.insertBefore(caja, p); grupo.forEach(el => caja.appendChild(el));
    }
  });
}
// en los capítulos, cada bloque y las respuestas empiezan en hoja nueva (el primer bloque va con el título)
document.querySelectorAll('section.capitulo > .junto').forEach(j => {
  if (j.firstElementChild && j.firstElementChild.tagName === 'H2') j.style.breakBefore = 'page';
});
// una fórmula más ancha que la hoja se achica sola (si no, Chrome achica la página entera)
document.querySelectorAll('.katex-display').forEach(d => {
  const k = d.querySelector('.katex'); if (!k) return;
  const w = k.scrollWidth, W = d.clientWidth;
  if (w > W) k.style.fontSize = (0.97 * W / w).toFixed(3) + 'em';
});
// dentro del código: ✓, ✗ y espacios para completar
document.querySelectorAll('pre code').forEach(c => {
  c.innerHTML = c.innerHTML
    .replace(/✓/g, '<span class="ok">✓</span>')
    .replace(/✗/g, '<span class="mal">✗</span>')
    .replace(/→ (_{4,})/g, '<span class="blanco">→ $1</span>\n');
});
"""


def capitulo(n):
    return next((REPO / 'guias').glob(f'cap-{n:02d}-*.md'))


def tiene_contenido(p):
    return re.search(r'(?m)^## ', p.read_text()) is not None


def generar(archivos, nombre):
    html = f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><title>{nombre}</title>
<style>{CSS}</style>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/marked@12.0.2/marked.min.js"></script></head>
<body><div id="c">Cargando...</div>
<script>const archivos = {json.dumps(archivos).replace('</', '<\\/')};
{JS}

</script></body></html>"""
    (TMP / f'{nombre}.html').write_text(html)
    pdf = f'{TMP_WIN}\\{nombre}.pdf'
    r = subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-pdf-header-footer',
                        '--virtual-time-budget=15000', '--run-all-compositor-stages-before-draw',
                        f'--print-to-pdf={pdf}', f'file:///{TMP_WIN}\\{nombre}.html'.replace('\\', '/')],
                       capture_output=True, text=True, timeout=120, cwd=str(TMP))
    print((r.stdout + r.stderr).strip().splitlines()[-1:] or 'sin salida')
    destino = REPO / 'guias' / 'pdf' / f'{nombre}.pdf'
    destino.parent.mkdir(exist_ok=True)
    shutil.move(str(TMP / f'{nombre}.pdf'), destino)
    print(destino)


def main():
    capitulos = [int(a) for a in sys.argv[1:]]
    libro = not capitulos
    if libro:
        capitulos = [int(p.name[4:6]) for p in sorted((REPO / 'guias').glob('cap-*.md')) if tiene_contenido(p)]
    for n in capitulos:
        generar([{'tipo': 'capitulo', 'md': capitulo(n).read_text()}], f'{ABR}-cap{n:02d}')
    if libro:
        generar([{'tipo': 'indice', 'md': (REPO / 'guias' / 'README.md').read_text()}], f'{ABR}-indice')


if __name__ == '__main__':
    main()
