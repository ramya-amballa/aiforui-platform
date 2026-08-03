# Citation Model

Every canonical object has a `citations` array (`/schemas/common/citation.schema.json`), each entry pointing to one external source backing something the object claims. This is how "every fact must be traceable" is enforced structurally rather than left as a norm.

## Citation fields

| Field | Required | Purpose |
|---|---|---|
| `id` | yes | Local identifier (`cite-...`), unique within the object, so a `relationship.citation_ids` entry (see below) can point at a specific citation. |
| `source_type` | yes | One of the seven categories below. |
| `title` | yes | Title of the cited work. |
| `publisher` | yes | The organisation/body responsible for the source. |
| `accessed_date` | yes | When the contributor retrieved/verified the source — lets stale or link-rotted citations be identified later. |
| `url` | no | Direct link, when the source exists online. |
| `publication_date` | no | When the source was originally published, if known. |
| `locator` | no | A precise pointer within the source (e.g. `'Article 6(2)'`, `'p. 12'`, `'MEASURE function, category 2.11'`) that anchors the specific claim, not just the document as a whole. |
| `excerpt` | no | A short, direct quotation supporting the claim it's attached to. |

`url` is optional rather than required because not every legitimate source type has a stable public URL (a court judgment might only exist in a paywalled reporter service; a company statement might have been made verbally and reported secondhand). `title` + `publisher` + `accessed_date` are the minimum needed for a human to go find the source again.

## Source types

`regulator`, `legislation`, `court_judgment`, `company_statement`, `academic_paper`, `standards_body`, `news_publication`, `other`. These cover the kinds of primary and secondary sources AI governance claims actually come from — a regulator's guidance, the text of a law, a tribunal or court ruling, a company's own public statement, peer-reviewed research, a standards body's publication (NIST, ISO, IEEE, etc.), and press reporting. `other` is the deliberate escape hatch for anything that doesn't fit, so contributors aren't forced to mis-categorise a source just to satisfy the enum.

## Linking a citation to a specific relationship

A `relationship` (`/schemas/common/relationship.schema.json`) can optionally carry `citation_ids`, referencing `id`s declared in the *same object's* `citations` array. This lets a contributor say not just "this decision has these three citations" but "specifically, this decision's claim that it satisfies this control is backed by citation X" — useful once an object accumulates several citations supporting different parts of it. The validator rejects a `citation_ids` entry that doesn't resolve to a real citation on the same object (`dangling_citation_reference`).

## When citations are mandatory

The validator's `missing_citation` rule requires `citations` to be non-empty when either of these is true:

1. **The object's `confidence` is `Verified` or `Reviewed`.** A record claiming that level of trust must show its work.
2. **The object is an `Incident` or a `Decision`, regardless of confidence.** These two entity types make factual/prescriptive claims about the world ("this happened," "this is what to do") that shouldn't be published even provisionally without at least one source — as opposed to, say, a `Draft` `Pattern`, which is closer to a design idea a contributor is still fleshing out and can legitimately start uncited.

`Pattern`, `Control`, `Evidence`, and `Board Question` objects at `Draft` or `Community` confidence are permitted zero citations, but should generally still have at least a rationale in `description` even before a formal citation is added — the schema doesn't enforce that, since it's genuinely a judgement call for maintainers reviewing the pull request.

## What counts as AI-generated content review

Per the project's core principle — "no AI-generated content enters the canonical dataset without human review" — this is enforced at the ingestion boundary rather than in the citation schema itself: see `/docs/ingestion-pipeline.md`. An AI-assisted draft's citations are exactly as scrutinisable as a human-authored one's; the difference is that the draft cannot become canonical without a named human reviewer's approval.
