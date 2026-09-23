// Install with npm ci from the repository root.
// Validate embedded diagram syntax and icon names; not visual layout.
import { JSDOM } from 'jsdom';
import { icons } from '@iconify-json/logos';
import { readFile, readdir } from 'node:fs/promises';
const dom = new JSDOM('<!doctype html><html><body></body></html>');
globalThis.window = dom.window;
globalThis.document = dom.window.document;
const { default: mermaid } = await import('mermaid');
mermaid.initialize({ startOnLoad: false, securityLevel: 'strict' });
mermaid.registerIconPacks([{ name: 'logos', icons }]);
async function* markdownFiles(directory) {
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const url = new URL(entry.name + (entry.isDirectory() ? '/' : ''), directory);
    if (entry.isDirectory()) yield* markdownFiles(url);
    else if (entry.name.endsWith('.md')) yield url;
  }
}
let count = 0;
for await (const file of markdownFiles(new URL('../bundles/', import.meta.url))) {
  const markdown = await readFile(file, 'utf8');
  for (const [, source] of markdown.matchAll(/```mermaid\r?\n([\s\S]*?)\r?\n```/g)) {
    for (const [, pack, icon] of source.matchAll(/\(([a-z0-9-]+):([a-z0-9-]+)\)/g)) {
      if (pack !== 'logos') throw new Error(`Unregistered icon pack: ${pack}`);
      if (!icons.icons[icon] && !icons.aliases?.[icon]) throw new Error(`Unknown icon: logos:${icon}`);
    }
    await mermaid.parse(source);
    count++;
    console.log(`PASS ${file.pathname.split('/bundles/')[1]}: ${source.split(/\r?\n/)[0]}`);
  }
}
if (count === 0) throw new Error('No embedded Mermaid diagrams found');
