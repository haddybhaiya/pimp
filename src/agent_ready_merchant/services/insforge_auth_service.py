"""Server-side verification of InsForge browser access tokens."""

import uuid
from dataclasses import dataclass

import httpx

from agent_ready_merchant.config import Settings


@dataclass(frozen=True)
class InsforgeIdentity:
    """Authenticated identity returned by InsForge."""

    user_id: uuid.UUID
    email: str


class InsforgeAuthService:
    """Verifies a bearer token by querying InsForge's current-session endpoint."""

    @classmethod
    async def verify_access_token(cls, token: str, settings: Settings) -> InsforgeIdentity:
        base_url = settings.INSFORGE_AUTH_BASE_URL
        if not base_url:
            raise ValueError("InsForge authentication is not configured.")

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{base_url.rstrip('/')}/api/auth/sessions/current",
                    headers={"Authorization": f"Bearer {token}"},
                )
        except httpx.HTTPError as exc:
            raise ValueError("Unable to verify the InsForge session.") from exc

        if response.status_code != 200:
            raise ValueError("Invalid or expired InsForge session.")

        body = response.json()
        user = body.get("user") if isinstance(body, dict) else None
        if not isinstance(user, dict) or not isinstance(user.get("id"), str):
            raise ValueError("InsForge returned an invalid session identity.")
        email = user.get("email")
        if not isinstance(email, str) or not email:
            raise ValueError("InsForge session has no verified email address.")
        try:
            return InsforgeIdentity(user_id=uuid.UUID(user["id"]), email=email.lower())
        except ValueError as exc:
            raise ValueError("InsForge returned an invalid user identifier.") from exc
