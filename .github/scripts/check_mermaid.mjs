// Los bloques ```mermaid del README los dibuja GitHub. Uno invalido no da error:
// se queda como un recuadro roto en la portada de un repo publico, que es la
// primera cosa que ve quien llega. Esto lo valida con el parser real de Mermaid,
// no con una heuristica.
import { JSDOM } from 'jsdom';
import fs from 'node:fs';
import path from 'node:path';

const RAIZ = path.resolve(import.meta.dirname, '..', '..');
const dom = new JSDOM('<!doctype html><body></body>', { pretendToBeVisual: true });
global.window = dom.window;
global.document = dom.window.document;
Object.defineProperty(globalThis, 'navigator', { value: dom.window.navigator, configurable: true });

const mermaid = (await import('mermaid')).default;
mermaid.initialize({ startOnLoad: false });

const ficheros = fs.readdirSync(RAIZ).filter((f) => f.endsWith('.md'));
let total = 0;
const fallos = [];

for (const fichero of ficheros) {
  const texto = fs.readFileSync(path.join(RAIZ, fichero), 'utf8');
  const bloques = [...texto.matchAll(/```mermaid\n([\s\S]*?)```/g)];
  for (const [i, m] of bloques.entries()) {
    total += 1;
    try {
      const r = await mermaid.parse(m[1]);
      console.log(`  ok  ${fichero} bloque ${i + 1}: ${r.diagramType}`);
    } catch (e) {
      fallos.push(`${fichero} bloque ${i + 1}: ${(e?.message ?? String(e)).slice(0, 400)}`);
    }
  }
}

// Caso de control: un validador que no distingue lo roto no vale de nada.
try {
  await mermaid.parse('flowchart TD\n  A[" --> B\n');
  fallos.push('control: el parser acepto un diagrama roto, asi que no valida nada');
} catch { /* esperado */ }

if (fallos.length) {
  console.error('Diagramas Mermaid invalidos:');
  for (const f of fallos) console.error(`  - ${f}`);
  process.exit(1);
}
console.log(`Mermaid correcto: ${total} bloque(s) valido(s).`);
