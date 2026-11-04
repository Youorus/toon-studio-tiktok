// Exécuter dans le conteneur frontend : les identifiants restent dans ce processus.
import { readFileSync, readdirSync } from "node:fs";
import { createHash } from "node:crypto";

const base = "https://studio.seyalabs.com";
function secret(name) {
  return process.env[`${name}_FILE`] ? readFileSync(process.env[`${name}_FILE`], "utf8").trim() : process.env[name];
}
function assert(value, message) { if (!value) throw new Error(message); }
async function main() {
  const unauth = await fetch(`${base}/api/postly/accounts`, { redirect: "manual" });
  assert(unauth.status === 401, "Le proxy doit demander une session");
  const login = await fetch(`${base}/api/auth/login`, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ password: secret("POSTLY_DASHBOARD_PASSWORD") }), redirect: "manual",
  });
  assert(login.ok, "Connexion de vérification refusée");
  const cookie = login.headers.get("set-cookie")?.split(";")[0];
  assert(cookie, "Session de vérification absente");
  const session = (path) => fetch(base+path, { headers: { Cookie: cookie }, redirect: "manual" });
  const read = async (path) => {
    const response = await session(path);
    assert(response.ok, `Réponse ${response.status} pour ${path}`);
    return response.json();
  };
  const accounts = await read("/api/postly/accounts");
  const account = accounts.find((a) => a.slug === "le-corps-parle-fr");
  assert(account, "Compte Le Corps Parle.fr absent");
  assert(!account.autopilot_enabled && !account.auto_schedule_enabled, "Ce compte doit rester en publication manuelle");
  const videos = await read(`/api/postly/videos?account_id=${account.id}&limit=200`);
  assert(videos.length >= 4, "Les quatre livraisons ne sont pas toutes présentes");
  const page = await session(`/videos?account=${account.id}`);
  assert(page.status === 200, "La bibliothèque du compte ne s’ouvre pas");
  const download = async (path, expected, full=false) => {
    const redirect = await session(path);
    assert(redirect.status === 307, `Téléchargement ${redirect.status} pour ${path}`);
    const location = redirect.headers.get("location");
    assert(location?.startsWith("https://"), "Téléchargement HTTPS signé attendu");
    // La requête objet n'emporte ni cookie du studio ni clé API.
    const response = await fetch(location, { headers: full ? {} : { Range: "bytes=0-1023" } });
    assert(full ? response.status===200 : [200,206].includes(response.status), "L’objet signé ne répond pas");
    if (full) {
      const hash=createHash("sha256"); let count=0;
      for await (const chunk of response.body) { hash.update(chunk); count+=chunk.length; }
      assert(hash.digest("hex")===expected.sha256, "Le fichier HTTP diffère du master local");
      if (expected.size_bytes) assert(count===expected.size_bytes, "Taille HTTP différente");
    } else {
      await response.arrayBuffer();
      const range=response.headers.get("content-range");
      if (range && expected.size_bytes) assert(range.endsWith(`/${expected.size_bytes}`), "Taille distante différente de l’inventaire");
    }
  };
  const report={studio_url:base,account_id:account.id,authenticated:true,private_access:true,episodes:[],files_checked:0};
  const selected = process.env.POSTLY_VERIFY_VIDEO_ID ? videos.filter((v) => v.id === process.env.POSTLY_VERIFY_VIDEO_ID) : videos;
  assert(selected.length > 0, "Aucune livraison à vérifier");
  for (const summary of selected) {
    const v=await read(`/api/postly/videos/${summary.id}`);
    assert(v.production_origin==="local_studio" && v.media_retained && v.archive_available, "Livraison non conservée ou incomplète");
    const s=v.segments[0];
    assert(s.status==="ready" && s.hashtags.includes("#Santé"), "Publication ou hashtags incomplets");
    assert(s.available_artifacts.includes("final") && s.available_artifacts.includes("srt") && s.available_artifacts.includes("caption"), "Livrables habituels absents");
    await download(`/api/postly/segments/${s.id}/download?artifact=final`,s.media_profile,true);
    await download(`/api/postly/segments/${s.id}/download?artifact=srt`,{});
    await download(`/api/postly/segments/${s.id}/download?artifact=caption`,{});
    await download(`/api/postly/videos/${v.id}/archive`,{});
    for (const file of v.production_files) {
      assert(!("reference" in file), "Une référence de stockage interne a été exposée");
      await download(`/api/postly/videos/${v.id}/production-files/${file.id}`,file,file.kind==="proof" || file.kind==="appeal");
      report.files_checked++;
    }
    const detail=await session(`/videos/${v.id}`);
    assert(detail.status===200,"La fiche de l’épisode ne s’ouvre pas");
    report.episodes.push({id:v.id,title:v.title,files:v.production_files.length,master_sha256:s.media_profile.sha256,ready:true,retained:true,url:base+`/videos/${v.id}`});
  }
  // Vérifier que les nouveaux contrôles sont bien présents dans le bundle déployé.
  const paths=[];
  function walk(path) { for(const item of readdirSync(path,{withFileTypes:true})) {
    const name=path+"/"+item.name;
    if(item.isDirectory()) walk(name); else if(name.endsWith(".js")) paths.push(name);
  }}
  walk("/app/.next/static/chunks");
  assert(paths.some((path)=>readFileSync(path,"utf8").includes("/production-files/")),"Le panneau des preuves n’est pas dans le bundle déployé");
  report.frontend_bundle_checked=true;
  console.log(JSON.stringify(report));
}
main().catch((error)=>{ console.error(JSON.stringify({verified:false,reason:error.message})); process.exitCode=1; });
