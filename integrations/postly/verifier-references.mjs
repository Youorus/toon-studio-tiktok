// Exécuter dans le conteneur frontend ; les identifiants restent en mémoire.
import { readFileSync, readdirSync } from "node:fs";
import { createHash } from "node:crypto";

const base = "https://studio.seyalabs.com";
const expected = { videos: 361, folders: 357 };
function assert(value, message) { if (!value) throw new Error(message); }
function secret(name) {
  return process.env[`${name}_FILE`] ? readFileSync(process.env[`${name}_FILE`], "utf8").trim() : process.env[name];
}
async function main() {
  const accountId = "4ba32772-1af6-585a-8bc3-62accfd1aee3";
  const endpoint = `/api/postly/accounts/${accountId}/references`;
  const unauth = await fetch(base + endpoint, { redirect: "manual" });
  assert(unauth.status === 401, "Le catalogue doit demander une session");
  const login = await fetch(`${base}/api/auth/login`, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ password: secret("POSTLY_DASHBOARD_PASSWORD") }), redirect: "manual",
  });
  assert(login.ok, "Connexion de vérification refusée");
  const cookie = login.headers.get("set-cookie")?.split(";")[0];
  assert(cookie, "Session absente");
  const session = (path) => fetch(base + path, { headers: { Cookie: cookie }, redirect: "manual" });
  const read = async (path) => {
    const response = await session(path);
    assert(response.ok, `Réponse ${response.status} pour ${path}`);
    return response.json();
  };
  const first = await read(endpoint + "?limit=100");
  assert(first.total === expected.videos && first.folders.length === expected.folders, "Corpus incomplet");
  const refs = [...first.references];
  for (let offset = 100; offset < first.total; offset += 100) {
    const next = await read(endpoint + `?limit=100&offset=${offset}`);
    refs.push(...next.references);
  }
  assert(new Set(refs.map((r) => r.id)).size === expected.videos, "Pagination incomplète");
  assert(!JSON.stringify(refs).includes("s3://"), "Référence de stockage interne exposée");
  const shared = await read(endpoint + "?folder=2025-10-14");
  assert(shared.matched === 2 && new Set(shared.references.map((r) => r.id)).size === 2, "Date partagée ambiguë");
  const unique = await read(endpoint + "?folder=2026-11-01");
  assert(unique.matched === 1, "Résolution d’une date unique incorrecte");
  const searched = await read(endpoint + `?q=${unique.references[0].source_video_id}`);
  assert(searched.matched === 1, "Recherche par identifiant incorrecte");
  const download = async (ref, asset, full = false) => {
    const response = await session(endpoint + `/${ref.id}/download?asset=${asset}&inline=true`);
    assert(response.status === 307, `Lien privé indisponible pour ${ref.id}`);
    const location = response.headers.get("location");
    assert(location?.startsWith("https://"), "Objet HTTPS signé attendu");
    const file = await fetch(location, { headers: full ? {} : { Range: "bytes=0-1023" } });
    assert(full ? file.status === 200 : [200, 206].includes(file.status), `Objet indisponible pour ${ref.id}`);
    if (full) {
      const hash = createHash("sha256"); let bytes = 0;
      for await (const chunk of file.body) { hash.update(chunk); bytes += chunk.length; }
      assert(hash.digest("hex") === (asset === "video" ? ref.sha256 : ref.thumbnail_sha256), "Fichier HTTP différent de l’original");
      if (asset === "video") assert(bytes === ref.size_bytes, "Taille HTTP différente de l’original");
    } else await file.arrayBuffer();
  };
  // Contrôler tous les liens vidéo, avec une concurrence bornée.
  let cursor = 0;
  await Promise.all(Array.from({ length: 6 }, async () => {
    while (cursor < refs.length) { const ref = refs[cursor++]; await download(ref, "video"); }
  }));
  const samples = [...shared.references, unique.references[0], refs.at(-1)];
  for (const ref of samples) {
    await download(ref, "video", true);
    await download(ref, "thumbnail", true);
  }
  const page = await session(`/references?account=${accountId}&date=2026-11-01`);
  assert(page.status === 200, "La page Références ne s’ouvre pas");
  const paths = [];
  function walk(path) { for (const item of readdirSync(path, { withFileTypes: true })) {
    const name = path + "/" + item.name;
    if (item.isDirectory()) walk(name); else if (name.endsWith(".js")) paths.push(name);
  }}
  walk("/app/.next/static/chunks");
  assert(paths.some((path) => {
    const code = readFileSync(path, "utf8");
    return code.includes("Copier la consigne") && code.includes("@lecorps.parle.fr");
  }), "La nouvelle bibliothèque n’est pas dans le bundle déployé");
  const inventory = refs.map((r) => [r.id, r.sha256]).sort((a, b) => a[0].localeCompare(b[0]));
  console.log(JSON.stringify({
    verified: true, checked_at: new Date().toISOString(), studio_url: base + `/references?account=${accountId}`,
    account_id: accountId, private_access: true, references: refs.length, folders: first.folders.length,
    video_links_checked: refs.length, original_downloads_sha256_checked: samples.length,
    thumbnail_downloads_sha256_checked: samples.length, shared_date_checked: "2025-10-14",
    catalogue_inventory_sha256: createHash("sha256").update(JSON.stringify(inventory)).digest("hex"),
    frontend_bundle_checked: true, publication_created: false,
  }));
}
main().catch((error) => { console.error(JSON.stringify({ verified: false, reason: error.message })); process.exitCode = 1; });
