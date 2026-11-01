// Used by pipeline.py: speaks one text file with Puter.js and writes the raw audio file.
// Usage: node puter_tts.mjs <text file> <output file>.  Needs PUTER_AUTH_TOKEN (and optional PUTER_VOICE, PUTER_PROVIDER).
import { init } from "@heyputer/puter.js/src/init.cjs";
import fs from "node:fs";

try {
  const [textFile, outFile] = process.argv.slice(2);
  const text = fs.readFileSync(textFile, "utf8");
  const puter = init(process.env.PUTER_AUTH_TOKEN);
  const r = await puter.ai.txt2speech(text, {
    provider: process.env.PUTER_PROVIDER || "gemini",
    voice: process.env.PUTER_VOICE || "Charon",
    language: "ta-IN",
  });
  let buf;
  if (Buffer.isBuffer(r)) buf = r;
  else if (r instanceof ArrayBuffer) buf = Buffer.from(r);
  else if (r && typeof r.arrayBuffer === "function") buf = Buffer.from(await r.arrayBuffer());
  else {
    const src = r && (r.src || r.url || r.currentSrc);
    if (typeof src !== "string") throw new Error("unknown audio result shape");
    if (src.startsWith("data:")) buf = Buffer.from(src.split(",")[1], "base64");
    else {
      const resp = await fetch(src);
      if (!resp.ok) throw new Error("download failed " + resp.status);
      buf = Buffer.from(await resp.arrayBuffer());
    }
  }
  fs.writeFileSync(outFile, buf);
  process.exit(0);   // Puter keeps a connection open, so exit explicitly
} catch (e) {
  console.error(e && (e.message || JSON.stringify(e)));
  process.exit(1);
}
