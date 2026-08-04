#!/usr/bin/env node
// Apply Anthropic Sandbox Runtime's filesystem boundary without a network
// allowlist. OpenCode must reach arbitrary research, package, and data hosts.
import { readFile } from "node:fs/promises";
import { spawn } from "node:child_process";
import { pathToFileURL } from "node:url";
import { join } from "node:path";

function fail(message) {
  console.error(`ERROR: ${message}`);
  process.exit(1);
}

if (process.argv.length < 5) {
  fail("OpenCode sandbox adapter needs a policy, SRT package, and command");
}

const [, , policyPath, packagePath, ...commandArgs] = process.argv;
let policy;
try {
  policy = JSON.parse(await readFile(policyPath, "utf8"));
} catch (error) {
  fail(`cannot read OpenCode sandbox policy ${policyPath}: ${error.message}`);
}

const unexpected = (object, allowed) =>
  object && typeof object === "object"
    ? Object.keys(object).filter((key) => !allowed.includes(key))
    : [];
const policyExtras = unexpected(policy, ["network", "filesystem"]);
const networkExtras = unexpected(policy?.network, ["mode"]);
const filesystemExtras = unexpected(policy?.filesystem, [
  "allowWrite",
  "denyWrite",
  "denyRead",
  "allowRead",
  "allowGitConfig",
]);
if (policyExtras.length || networkExtras.length || filesystemExtras.length) {
  fail(`OpenCode sandbox policy has unknown fields: ${[
    ...policyExtras,
    ...networkExtras.map((key) => `network.${key}`),
    ...filesystemExtras.map((key) => `filesystem.${key}`),
  ].join(", ")}`);
}
if (policy?.network?.mode !== "unrestricted") {
  fail('OpenCode sandbox policy must explicitly set network.mode to "unrestricted"');
}
const filesystem = policy?.filesystem;
for (const key of ["allowWrite", "denyWrite", "denyRead"]) {
  if (!Array.isArray(filesystem?.[key]) || filesystem[key].some((item) => typeof item !== "string" || !item)) {
    fail(`OpenCode sandbox policy filesystem.${key} must be an array of paths`);
  }
}
if (
  filesystem.allowRead !== undefined &&
  (!Array.isArray(filesystem.allowRead) || filesystem.allowRead.some((item) => typeof item !== "string" || !item))
) {
  fail("OpenCode sandbox policy filesystem.allowRead must be an array of paths");
}
if (filesystem.allowGitConfig !== undefined && typeof filesystem.allowGitConfig !== "boolean") {
  fail("OpenCode sandbox policy filesystem.allowGitConfig must be boolean");
}
if (commandArgs.some((arg) => arg.includes("\0"))) {
  fail("OpenCode sandbox command contains a NUL byte");
}

let SandboxManager;
try {
  const packageMetadata = JSON.parse(await readFile(join(packagePath, "package.json"), "utf8"));
  if (packageMetadata.name !== "@anthropic-ai/sandbox-runtime") {
    throw new Error(`unexpected package ${packageMetadata.name ?? "(unnamed)"}`);
  }
  ({ SandboxManager } = await import(pathToFileURL(join(packagePath, "dist", "index.js"))));
  if (typeof SandboxManager?.initialize !== "function" || typeof SandboxManager?.wrapWithSandboxArgv !== "function") {
    throw new Error("required SandboxManager API is unavailable");
  }
} catch (error) {
  fail(`cannot load Anthropic Sandbox Runtime library: ${error.message}`);
}

const runtimeConfig = {
  // allowedDomains is deliberately absent. SRT then leaves the host network
  // namespace/profile unchanged while still emitting its filesystem policy.
  network: { deniedDomains: [], allowLocalBinding: true },
  filesystem,
};

const quote = (arg) => `'${arg.replaceAll("'", "'\\''")}'`;
let wrapped;
try {
  await SandboxManager.initialize(runtimeConfig);
  if (!SandboxManager.isSandboxingEnabled()) {
    throw new Error("Sandbox Runtime did not enable confinement");
  }
  wrapped = await SandboxManager.wrapWithSandboxArgv(commandArgs.map(quote).join(" "));
} catch (error) {
  await SandboxManager?.reset?.().catch(() => {});
  fail(`cannot initialize OpenCode sandbox: ${error.message}`);
}

const childEnv = {
  ...wrapped.env,
  SANDBOX_RUNTIME: "1",
  PATH: process.env.ZEROPAPER_OPENCODE_CHILD_PATH || wrapped.env.PATH,
  XDG_DATA_HOME: join(process.cwd(), "process_log", ".opencode-runtime", "data"),
  XDG_STATE_HOME: join(process.cwd(), "process_log", ".opencode-runtime", "state"),
};
if (process.env.ZEROPAPER_OPENCODE_CHILD_VIRTUAL_ENV) {
  childEnv.VIRTUAL_ENV = process.env.ZEROPAPER_OPENCODE_CHILD_VIRTUAL_ENV;
} else {
  delete childEnv.VIRTUAL_ENV;
}
delete childEnv.ZEROPAPER_OPENCODE_CHILD_PATH;
delete childEnv.ZEROPAPER_OPENCODE_CHILD_VIRTUAL_ENV;

const child = spawn(wrapped.argv[0], wrapped.argv.slice(1), {
  cwd: process.cwd(),
  env: childEnv,
  shell: false,
  stdio: "inherit",
});
const signalHandlers = new Map();
for (const signal of ["SIGINT", "SIGTERM", "SIGHUP"]) {
  const handler = () => child.kill(signal);
  signalHandlers.set(signal, handler);
  process.on(signal, handler);
}

const result = await new Promise((resolve) => {
  child.once("error", (error) => resolve({ error }));
  child.once("exit", (code, signal) => resolve({ code, signal }));
});
SandboxManager.cleanupAfterCommand();
await SandboxManager.reset().catch(() => {});

if (result.error) fail(`cannot execute sandboxed OpenCode command: ${result.error.message}`);
if (result.signal) {
  for (const [signal, handler] of signalHandlers) process.removeListener(signal, handler);
  process.kill(process.pid, result.signal);
}
process.exit(result.code ?? 1);
