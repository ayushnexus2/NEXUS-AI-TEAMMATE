"""Switch integration boundary.

Switch supports agents through its room/agent protocol. The exact endpoint and
payload depend on the Switch server/protocol version and deployment. Do not
guess an endpoint: configure a small authenticated bridge for your deployment
and point SWITCH_BASE_URL at that bridge.

The bridge contract used by this starter is:
POST {SWITCH_BASE_URL}/tasks
JSON: {"room_id": "...", "agent": "...", "task_id": "...", "task": "..."}
Response JSON: {"status": "completed", "result": "..."} OR
               {"status": "accepted", "task_ref": "..."}.

For asynchronous setups, the bridge should POST completion to your callback
service (not implemented in this starter), or you can poll its task endpoint.
This adapter times out safely and reports the limitation to Discord.
"""
import os
import httpx

class SwitchNotConfigured(RuntimeError):
    pass

class SwitchAdapter:
    def __init__(self):
        self.base_url = os.getenv("SWITCH_BASE_URL", "").rstrip("/")
        self.room_id = os.getenv("SWITCH_ROOM_ID", "")
        self.agent = os.getenv("SWITCH_AGENT_NAME", "nexus-codex")
        self.secret = os.getenv("SWITCH_SHARED_SECRET", "")
        self.timeout = float(os.getenv("TASK_TIMEOUT_SECONDS", "900"))

    async def execute(self, task_id: str, task: str) -> str:
        if not self.base_url or not self.room_id:
            raise SwitchNotConfigured(
                "Switch bridge is not configured. Set SWITCH_BASE_URL and SWITCH_ROOM_ID "
                "after connecting your Codex agent to a Switch room."
            )
        headers = {"Content-Type": "application/json"}
        if self.secret:
            headers["Authorization"] = f"Bearer {self.secret}"
        payload = {
            "room_id": self.room_id,
            "agent": self.agent,
            "task_id": task_id,
            "task": task,
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(f"{self.base_url}/tasks", json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
        status = data.get("status")
        if status == "completed" and data.get("result"):
            return str(data["result"])[:1800]
        if status == "accepted":
            raise RuntimeError(
                "Switch accepted the task but this starter bridge returned an asynchronous "
                "task. Add polling or a completion callback to your bridge before claiming "
                "automatic result delivery."
            )
        raise RuntimeError(f"Unexpected Switch bridge response: {str(data)[:500]}")
