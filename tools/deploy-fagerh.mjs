import { existsSync } from "node:fs";
import { spawnSync } from "node:child_process";

function run(command, args, options = {}) {
  const result = spawnSync(command, args, {
    encoding: "utf8",
    env: options.env ? { ...process.env, ...options.env } : process.env,
    stdio: options.capture ? "pipe" : "inherit",
  });
  if (result.status !== 0) {
    const output = [result.stdout, result.stderr].filter(Boolean).join("\n").trim();
    throw new Error(output || `${command} ${args.join(" ")} failed`);
  }
  return (result.stdout || "").trim();
}

function remoteUrl(name) {
  return run("git", ["remote", "get-url", name], { capture: true });
}

function assertCleanWorktree() {
  const status = run("git", ["status", "--short"], { capture: true });
  if (status) {
    throw new Error(
      [
        "Refus de déployer FAGERH : le dossier Git contient des changements non commités.",
        "Commite ou annule les changements avant de déployer.",
        status,
      ].join("\n"),
    );
  }
}

function assertRemote() {
  const url = remoteUrl("scalingo");
  if (!url.includes("fagerh.git")) {
    throw new Error(`Refus de déployer FAGERH : le remote scalingo ne pointe pas vers fagerh.git (${url}).`);
  }
}

function assertNoEuresPayload() {
  const forbidden = [
    "forms/eures-beta/app.js",
    "forms/eures-beta/admin.html",
    "forms/eures-beta/site.css",
    "forms/eures-beta/candidate.html",
    "forms/eures-beta/employer.html",
  ];
  const present = forbidden.filter((file) => existsSync(file));
  if (present.length) {
    throw new Error(
      [
        "Refus de déployer FAGERH : cette branche contient encore des fichiers EURES.",
        "Cela indique que tu n’es pas sur une branche FAGERH isolée.",
        ...present.map((file) => `- ${file}`),
      ].join("\n"),
    );
  }
}

function assertBranchContainsFagerh() {
  run("node", ["tools/check-fagerh-regressions.mjs"]);
}

function assertServerCompiles() {
  run("python3", ["-m", "py_compile", "app.py"], {
    env: { PYTHONPYCACHEPREFIX: "/tmp/grist-custom-forms-pycache" },
  });
}

function main() {
  const shouldPush = process.argv.includes("--push");
  assertCleanWorktree();
  assertRemote();
  assertNoEuresPayload();
  assertBranchContainsFagerh();
  assertServerCompiles();

  if (!shouldPush) {
    console.log("Contrôles FAGERH OK. Ajoute --push pour déployer vers Scalingo FAGERH.");
    return;
  }

  run("git", ["push", "scalingo", "HEAD:main"]);
}

try {
  main();
} catch (error) {
  console.error(error.message || error);
  process.exit(1);
}
