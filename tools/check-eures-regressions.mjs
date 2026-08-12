import { readFileSync } from "node:fs";
import { spawnSync } from "node:child_process";

const files = {
  app: readFileSync("forms/eures-beta/app.js", "utf8"),
  admin: readFileSync("forms/eures-beta/admin.html", "utf8"),
  appPy: readFileSync("app.py", "utf8"),
  projectPage: readFileSync("forms/eures-beta/le-projet.html", "utf8"),
  journalPage: readFileSync("forms/eures-beta/journal.html", "utf8"),
  css: readFileSync("forms/eures-beta/site.css", "utf8"),
};

const checks = [
  // Public pages restored after the regression.
  ["project page shell", files.projectPage, 'data-page="project"'],
  ["journal page shell", files.journalPage, 'data-page="journal"'],
  ["project template", files.app, "function projectTemplate"],
  ["journal template", files.app, "function journalTemplate"],
  ["project summary", files.app, "summary-panel"],
  ["journal entries", files.app, "journalEntriesFR"],
  ["editorial css", files.css, ".editorial-grid"],
  ["journal css", files.css, ".journal-entry"],

  // Candidate WhatsApp consent must not disappear again.
  ["candidate whatsapp title", files.app, 'whatsappTitle: "Contact WhatsApp"'],
  ["candidate whatsapp accept", files.app, "J’accepte que Match Europe utilise mon numéro"],
  ["candidate whatsapp refuse", files.app, "Je refuse l’utilisation de WhatsApp"],
  ["candidate whatsapp input", files.app, 'radioPills("whatsapp_consent"'],
  ["candidate whatsapp raw json", files.app, "whatsapp: {"],
  ["candidate whatsapp consent field", files.app, "whatsapp_consent: normalized.whatsapp_consent"],
  ["candidate whatsapp phone field", files.app, "whatsapp_phone: normalized.tally_q34"],
  ["candidate form version", files.app, "2026-08-tally-candidate-salary-v4"],

  // Employer WhatsApp confirmation flow.
  ["employer email whatsapp option", files.appPy, "contact_whatsapp"],
  ["employer email no whatsapp option", files.appPy, "contact_no_whatsapp"],
  ["employer whatsapp consent field", files.appPy, "employer_whatsapp_consent"],
  ["employer whatsapp phone field", files.appPy, "employer_whatsapp_phone"],
  ["employer whatsapp confirmation page", files.appPy, "Confirmer la mise en relation WhatsApp"],

  // Admin matching flow safeguards.
  ["manual matching create button", files.admin, "manual-match-create-btn"],
  ["validate and send emails action", files.admin, 'data-send-emails="true"'],
  ["validate without emails action", files.admin, 'data-send-emails="false"'],
  ["matching compact details", files.admin, "Détail"],
  ["admin employer whatsapp display", files.admin, "Accord WhatsApp employeur"],
];

const failures = [];
for (const [label, content, marker] of checks) {
  if (!content.includes(marker)) {
    failures.push(`${label}: missing marker ${JSON.stringify(marker)}`);
  }
}

const syntax = spawnSync(process.execPath, ["--check", "forms/eures-beta/app.js"], {
  encoding: "utf8",
});
if (syntax.status !== 0) {
  failures.push(`app.js syntax check failed:\n${syntax.stderr || syntax.stdout}`);
}

if (failures.length) {
  console.error("EURES regression checks failed:");
  for (const failure of failures) {
    console.error(`- ${failure}`);
  }
  process.exit(1);
}

console.log(`EURES regression checks passed (${checks.length} markers + JS syntax).`);
