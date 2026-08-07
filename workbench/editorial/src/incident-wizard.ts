import { existsSync, writeFileSync } from "node:fs";
import path from "node:path";
import { createInterface } from "node:readline";
import { buildIngestionAjv, DRAFTS_DIR } from "../../ingestion/src/schema.js";

/**
 * Incident Authoring Wizard. Guides a maintainer through building a
 * schema-valid draft incident interactively, so the common failure modes of
 * hand-writing JSON (wrong date format, invalid enum value, forgotten
 * required field) are caught at entry time rather than at `npm run
 * ingest:validate-draft`. It only ever produces a draft with
 * human_review.status = "pending" — it never approves or promotes anything
 * itself, per the project principle that these tools improve consistency
 * without automating editorial judgment.
 */

const SOURCE_TYPES = ["regulator", "legislation", "court_judgment", "company_statement", "academic_paper", "standards_body", "news_publication", "other"];
const HARM_TYPES = ["discrimination", "privacy_violation", "safety", "financial", "reputational", "misinformation", "security", "other"];
const SEVERITIES = ["low", "medium", "high", "critical"];
const EXTRACTION_METHODS = ["human", "ai_assisted"];

const DATE_RE = /^\d{4}-\d{2}-\d{2}$/;
const SLUG_RE = /^[a-z0-9]+(-[a-z0-9]+)*$/;

// Node's readline/promises `question()` can drop lines that arrive before
// the next question() call re-arms it (a real risk here, not just a piped-
// input test artifact — e.g. a maintainer pasting a multi-line excerpt
// faster than prompts render). Queue every 'line' event instead, so no
// input is ever lost regardless of arrival timing.
const rl = createInterface({ input: process.stdin, output: process.stdout, terminal: process.stdin.isTTY === true });
const lineQueue: string[] = [];
const waiters: ((line: string) => void)[] = [];
rl.on("line", (line) => {
  const waiter = waiters.shift();
  if (waiter) waiter(line);
  else lineQueue.push(line);
});

function nextLine(): Promise<string> {
  const queued = lineQueue.shift();
  if (queued !== undefined) return Promise.resolve(queued);
  return new Promise((resolve) => waiters.push(resolve));
}

async function ask(question: string, opts: { default?: string; validate?: (v: string) => string | null } = {}): Promise<string> {
  const suffix = opts.default ? ` [${opts.default}]` : "";
  for (;;) {
    process.stdout.write(`${question}${suffix}: `);
    const raw = (await nextLine()).trim();
    const value = raw || opts.default || "";
    if (opts.validate) {
      const error = opts.validate(value);
      if (error) {
        console.log(`  ! ${error}`);
        continue;
      }
    }
    return value;
  }
}

async function askMenu(question: string, options: string[], opts: { default?: string; allowEmpty?: boolean } = {}): Promise<string> {
  console.log(question);
  options.forEach((o, i) => console.log(`  ${i + 1}. ${o}`));
  const answer = await ask("Choice (number)", { default: opts.default });
  if (opts.allowEmpty && answer === "") return "";
  const index = Number(answer) - 1;
  if (Number.isInteger(index) && index >= 0 && index < options.length) return options[index];
  const byName = options.find((o) => o === answer);
  if (byName) return byName;
  console.log(`  ! Not a valid choice, defaulting to '${options[0]}'.`);
  return options[0];
}

async function askMulti(question: string, options: string[]): Promise<string[]> {
  console.log(question);
  options.forEach((o, i) => console.log(`  ${i + 1}. ${o}`));
  const answer = await ask("Choices (comma-separated numbers, or blank for none)", {});
  if (!answer) return [];
  return answer
    .split(",")
    .map((s) => Number(s.trim()) - 1)
    .filter((i) => Number.isInteger(i) && i >= 0 && i < options.length)
    .map((i) => options[i]);
}

function csv(value: string): string[] {
  return value
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
}

async function main(): Promise<void> {
  console.log("=== AI Governance Workbench — Incident Authoring Wizard ===");
  console.log("Builds a schema-valid draft incident in /ingestion/drafts. It does NOT approve or promote anything.\n");

  const today = new Date().toISOString().slice(0, 10);

  console.log("-- Source --");
  const slug = await ask("Short slug for this draft (e.g. 'my-incident-2024')", {
    validate: (v) => (SLUG_RE.test(v) ? null : "Must be lowercase kebab-case, e.g. 'my-incident-2024'."),
  });
  const draftId = `draft-incident-${slug}`;
  const draftPath = path.join(DRAFTS_DIR, `${draftId}.json`);
  if (existsSync(draftPath)) {
    console.log(`! ${draftPath} already exists. Aborting — pick a different slug.`);
    rl.close();
    process.exit(1);
  }

  const sourceType = await askMenu("Source type:", SOURCE_TYPES);
  const sourceTitle = await ask("Source title", { validate: (v) => (v ? null : "Required.") });
  const sourcePublisher = await ask("Source publisher", { validate: (v) => (v ? null : "Required.") });
  const sourceUrl = await ask("Source URL (optional)");
  const sourcePublishedDate = await ask("Source published date YYYY-MM-DD (optional)", {
    validate: (v) => (!v || DATE_RE.test(v) ? null : "Format must be YYYY-MM-DD."),
  });
  const sourceRetrievedDate = await ask("Date you retrieved this source (YYYY-MM-DD)", {
    default: today,
    validate: (v) => (DATE_RE.test(v) ? null : "Format must be YYYY-MM-DD."),
  });
  const rawExcerpt = await ask("Verbatim excerpt from the source", { validate: (v) => (v ? null : "Required.") });
  const extractionMethod = await askMenu("Extraction method:", EXTRACTION_METHODS, { default: "1" });
  const capturedBy = await ask("Your name/handle (captured_by, optional)");

  console.log("\n-- Candidate incident content --");
  const title = await ask("Incident title", { validate: (v) => (v ? null : "Required.") });
  const description = await ask("Incident description (self-contained, 2-4 sentences)", { validate: (v) => (v ? null : "Required.") });
  const occurredDate = await ask("Occurred date YYYY-MM-DD", { validate: (v) => (DATE_RE.test(v) ? null : "Format must be YYYY-MM-DD.") });
  const organizationsInvolved = csv(await ask("Organizations involved (comma-separated, optional)"));
  const harmTypes = await askMulti("Harm types:", HARM_TYPES);
  const aiSystemCategory = await ask("AI system category (short snake_case slug, optional)");
  const jurisdiction = csv(await ask("Jurisdiction (comma-separated codes, optional)"));
  const severity = await askMenu("Severity:", SEVERITIES, { default: "2" });
  const rootCause = await ask("Root cause (optional)");
  const tags = csv(await ask("Tags (comma-separated, optional)"));

  rl.close();

  const draft: Record<string, unknown> = {
    id: draftId,
    created_date: today,
    source: {
      source_type: sourceType,
      title: sourceTitle,
      publisher: sourcePublisher,
      ...(sourceUrl ? { url: sourceUrl } : {}),
      ...(sourcePublishedDate ? { published_date: sourcePublishedDate } : {}),
      retrieved_date: sourceRetrievedDate,
    },
    raw_excerpt: rawExcerpt,
    extraction_method: extractionMethod,
    ...(capturedBy ? { captured_by: capturedBy } : {}),
    suggested_incident: {
      title,
      description,
      occurred_date: occurredDate,
      ...(organizationsInvolved.length ? { organizations_involved: organizationsInvolved } : {}),
      ...(harmTypes.length ? { harm_types: harmTypes } : {}),
      ...(aiSystemCategory ? { ai_system_category: aiSystemCategory } : {}),
      ...(jurisdiction.length ? { jurisdiction } : {}),
      ...(severity ? { severity } : {}),
      ...(rootCause ? { root_cause: rootCause } : {}),
      ...(tags.length ? { tags } : {}),
    },
    human_review: { status: "pending" },
  };

  const { draftValidator } = buildIngestionAjv();
  if (!draftValidator(draft)) {
    console.log("\n✘ The draft failed schema validation — not written:");
    for (const err of draftValidator.errors ?? []) {
      console.log(`  ${err.instancePath || "(root)"} ${err.message ?? "is invalid"}`);
    }
    process.exit(1);
  }

  writeFileSync(draftPath, JSON.stringify(draft, null, 2) + "\n", "utf-8");
  console.log(`\n✔ Draft written to ${draftPath}`);
  console.log("Next: get it reviewed, set human_review.status to 'approved' with a reviewer and confidence_assigned,");
  console.log(`then run: npm run ingest:promote -- ${path.relative(process.cwd(), draftPath)}`);
}

main();
