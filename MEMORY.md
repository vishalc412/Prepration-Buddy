# Project conventions

- App name: Prepration Buddy (OFFline and AI), as requested on 7 October 2026.
- Preserve `principal-ai-studio-v1` localStorage identity and version-1 backup compatibility across branding changes.
- Home must visibly explain selected preparation mode. Challenge start opens Recall; answers require an attempt in that question. Prior attempts are preserved and remain eligible for reference review.
- Library and topic search are explicit review tools. No AI model is required for bundled teaching; the app does not grade free-text or execute Python/Java.

- Curriculum edition `offline-teacher-30d-4h` migrates legacy six-hour schedules to four hours once, while preserving original draft IDs and storage identity. Extend DAYS before normalizing backups so day 15–30 selections and scores survive imports.
- Revised JD drills map to existing design/defend time; do not silently add extra daily hours. Explicitly acknowledge JS/TS requirement while respecting the user’s Python/Java coding scope.

- JD coverage statuses must distinguish executed local prototypes, design exercises, optional external integrations, credentials/experience and language scope. A topic link is not production execution evidence.
- Case-study ZIP archives are assembled locally from embedded authored files. Challenge unlocks reference code only after an implementation draft; downloading or viewing author receipts never certifies the learner’s code.

Practical-case close-out: four reference fixtures executed independently from embedded JSON source in fresh workspaces; output/practical-validation.json records receipts and exact HTML hash. Actual browser-downloaded ZIP bytes/CRC match all 22 source/config files. New case draft/defense/follow-up/evidence maps survive reload and progress export/import. Source parity is checked by validate_practical_cases.py --html; --execute needs a prepared enterprise Python/JDK/offline-Maven toolchain. Source review and fixture execution do not certify learner code, cloud operation, current MCP SDK compatibility or real model quality.

- Tutorial companions come from the authored `video-catalog.json`, merged by exact YouTube ID from two research shards. Extend mappings and retain first-party evidence, watch/build prompts and version cautions; do not restore generic YouTube search destinations or automatic remote media loads.
- Video saved/reviewed/takeaway entries use the existing `state.notes` map and backup format. Reviewed is a learner declaration, separate from quiz mastery and Challenge attempt gates. Evidence: `output/video-browser-validation.json` verifies backup/reload and zero offline remote requests; `output/video-gate-validation.json` verifies that video review cannot unlock a blank client answer or case reference.
- Keep full tutorial guidance in the main lesson and only one compact `teacherTutorialLinks` companion in the sidebar. Browser validation covers all 155 lesson mappings, 30 days, eight scenario tracks, 50 client questions, eight JD drills and four cases.
