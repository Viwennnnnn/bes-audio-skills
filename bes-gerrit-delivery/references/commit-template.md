# Gerrit commit message policy

The BES Gerrit hook requires each section to exist with non-empty content:

```text
<type>[#task-or-bug]component: concise subject

[Desc]
What changed and why.

[Solution]
How the change is implemented.

[Impact(None/Fast/Stable/Space/Function/Security/Privacy)]
Function

[Self-Test Result(Pass/Fail)]
Pass: exact build or test evidence.

[Test Suggestions]
Concrete board/runtime checks for reviewers.

Change-Id: I...
```

Use real evidence and a valid impact value. Wrap ordinary lines near 72 characters. Do not encode line breaks as literal `\n` inside a shell `-m` argument; use separate paragraphs, a message file, or a safe editor mechanism.

Known successful G28 KWS review upload:

- repository: `bes/metabounds/configs`
- branch: `main`
- change: `46700`
- URL: `http://192.168.1.15:8001/c/bes/metabounds/configs/+/46700`

This example is historical context; always use the new push response as the source of truth.
