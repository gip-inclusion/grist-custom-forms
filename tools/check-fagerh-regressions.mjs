import { existsSync, readFileSync } from "node:fs";

const requiredFiles = [
  "fagerh_analytics/__init__.py",
  "fagerh_analytics/flask_adapter.py",
  "fagerh_analytics/repositories/grist.py",
  "forms/fagerh/admin.html",
  "forms/fagerh/analytics.html",
  "forms/fagerh/analytics.css",
  "forms/fagerh/analytics.js",
  "forms/fagerh/observatoire.html",
  "forms/fagerh/observatoire.css",
  "forms/fagerh/observatoire.js",
  "forms/fagerh/livret.html",
  "forms/fagerh/livret.css",
  "forms/fagerh/livret.js",
  "forms/fagerh/aura-establishments-map.svg",
  "forms/fagerh/cover-photo.jpg",
  "forms/fagerh/model-cover.jpg",
];

const failures = [];
for (const file of requiredFiles) {
  if (!existsSync(file)) {
    failures.push(`missing required file: ${file}`);
  }
}

const files = {
  appPy: readFileSync("app.py", "utf8"),
  admin: readFileSync("forms/fagerh/admin.html", "utf8"),
};

const checks = [
  ["analytics admin link", files.admin, "/admin/fagerh/analytics/"],
  ["observatoire admin link", files.admin, "/admin/fagerh/observatoire/"],
  ["livret admin link", files.admin, "/admin/fagerh/livret/"],
  ["analytics route", files.appPy, "@app.route('/admin/<form_id>/analytics/')"],
  ["observatoire route", files.appPy, "@app.route('/admin/<form_id>/observatoire/')"],
  ["livret route", files.appPy, "@app.route('/admin/<form_id>/livret/')"],
  ["analytics blueprint", files.appPy, "create_fagerh_analytics_blueprint"],
  ["analytics session mark", files.appPy, "mark_fagerh_analytics_session_authenticated"],
  ["grist repository", files.appPy, "GristQuestionnaireRepository"],
];

for (const [label, content, marker] of checks) {
  if (!content.includes(marker)) {
    failures.push(`${label}: missing marker ${JSON.stringify(marker)}`);
  }
}

if (failures.length) {
  console.error("FAGERH regression checks failed:");
  for (const failure of failures) {
    console.error(`- ${failure}`);
  }
  process.exit(1);
}

console.log(`FAGERH regression checks passed (${requiredFiles.length} files + ${checks.length} markers).`);
