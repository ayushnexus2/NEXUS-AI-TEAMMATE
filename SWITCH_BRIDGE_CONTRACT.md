# Switch bridge contract for this starter

The starter calls `POST /tasks` on a bridge URL you control. This is an application-level contract for NEXUS, **not a claim that Switch itself exposes this route**.

Request:
```json
{
  "room_id": "your-switch-room",
  "agent": "nexus-codex",
  "task_id": "a1b2c3d4",
  "task": "Inspect the repo and add a unit test."
}
```

Synchronous response:
```json
{"status":"completed","result":"Implemented the test. pytest: 4 passed."}
```

The bridge must:
- authenticate NEXUS (for example, bearer token);
- validate room and agent identifiers;
- post the task into the configured Switch room using the current Switch agent/room protocol;
- wait for a correlated Codex result;
- return only that task's result;
- enforce a timeout and preserve task IDs.

If your Switch setup is asynchronous, extend this adapter with polling or a signed callback. Never expose a public unauthenticated task endpoint.
