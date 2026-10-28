# sweep.json schema

Every field is plain text. Timestamps are ISO 8601 with a UTC offset (`2026-10-28T08:56:00-07:00` or `...Z`).
Each linkable item needs **exactly one** of `thread_id` (Gmail thread id, hex) or `search` (Gmail search query).

```jsonc
{
  "account": "you@example.com",      // required; used for Gmail links
  "generated_at": "2026-10-28T08:56:00-07:00", // required; run time, local offset
  "timezone_label": "PT",                      // optional, default "PT"
  "scanned": 183,                              // required; inbox threads read
  "errors": 0,                                 // optional; > 0 shows red in footer
  "subject_prefix": "[Test]",                  // optional; prepended to subject
  "preheader": "…",                            // optional; inbox preview text (auto if absent)

  "todo": [                                    // required, may be []; ranked, rendered numbered
    {
      "title": "Schedule Redis maintenance: 6 prod add-ons",  // action phrasing
      "source": "Heroku",                                     // short sender/system name
      "received_at": "2026-10-22T09:00:00Z",                  // or a list → "6–17d" range
      "detail": "api-prod · api-eu-prod",             // optional one line
      "thread_id": "18f0000000000002",                        // or "search": "…"
      "link": {"label": "view", "search": "TKT-1042"}          // optional extra link
    }
  ],
  "handled": [                                 // required, may be []; omitted when empty
    {"title": "Remote-support license renewal (11/2)", "reason": "Morgan: cancel all licenses; Casey owns it", "thread_id": "…"}
  ],
  "fyi": [                                     // required, may be []; omitted when empty
    {"title": "Mailchimp order", "thread_id": "…"}
  ],
  "swept": {                                   // required
    "by_source": [{"name": "Asana", "count": 18}],          // required; total = sum
    "possible_misses": [{"title": "Jamie: “Thanks…”", "thread_id": "…"}],  // optional
    "unsure": [{"title": "…", "thread_id": "…"}]                              // optional
  }
}
```

Validation errors are all reported at once, one per line, with the JSON path (e.g. `todo[2].received_at: needs a UTC offset`).
