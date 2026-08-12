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
        "Refus de déployer EURES : le dossier Git contient des changements non commités.",
        "Commite ou annule les changements avant de déployer.",
        status,
      ].join("\n"),
    );
  }
}

function assertRemote() {
  const url = remoteUrl("scalingo-eures");
  if (!url.includes("eures-beta.git")) {
    throw new Error(`Refus de déployer EURES : le remote scalingo-eures ne pointe pas vers eures-beta.git (${url}).`);
  }
}

function assertBranchContainsEures() {
  run("node", ["tools/check-eures-regressions.mjs"]);
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
  assertBranchContainsEures();
  assertServerCompiles();

  if (!shouldPush) {
    console.log("Contrôles EURES OK. Ajoute --push pour déployer vers Scalingo EURES.");
    return;
  }

  run("git", ["push", "origin", "main"]);
  run("git", ["push", "scalingo-eures", "main"]);
}

try {
  main();
} catch (error) {
  console.error(error.message || error);
  process.exit(1);
}
