from __future__ import annotations

import base64
import binascii
from functools import cached_property
from typing import Any

from pydantic import BaseModel, Field, field_validator


class AttachmentData(BaseModel):
    """Base64 payloads carried by an attachment."""

    original: str
    compiled: str = ""

    @field_validator("original", "compiled")
    @classmethod
    def _validate_base64(cls, value: str) -> str:
        """Validate that the payload is decodable base64."""
        if not value:
            return value
        try:
            base64.b64decode(value, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise ValueError(f"is not valid base64: {exc}") from exc
        return value


class Attachment(BaseModel):
    """A file attached to an experience (script, map, strings, ...)."""

    id: str
    version: str
    filename: str
    isProcessable: bool
    processingStatus: int
    attachmentData: AttachmentData
    attachmentType: int
    errors: list[Any] = []
    metadata: str | None = None


class MapRotationEntry(BaseModel):
    """A single map in the rotation with its spatial attachment."""

    id: str
    spatialAttachment: Attachment


class WorkspaceBlock(BaseModel):
    """A block placed on the visual scripting workspace."""

    type: str
    id: str
    x: int
    y: int
    deletable: bool = True


class WorkspaceBlocks(BaseModel):
    """The set of blocks in the workspace along with their language version."""

    languageVersion: int
    blocks: list[WorkspaceBlock] = []


class Workspace(BaseModel):
    """The visual scripting workspace (`mod`) of an experience."""

    mod: dict[str, Any] = {}


class ExperienceExport(BaseModel):
    """A Battlefield Portal experience as exported to JSON."""

    name: str
    description: str
    gameMode: str
    mutators: dict[str, Any] = {}
    assetRestrictions: dict[str, Any] = {}
    mapRotation: list[MapRotationEntry] = []
    workspace: Workspace = Field(default_factory=Workspace)
    teamComposition: list[Any] = []
    attachments: list[Attachment] = []

    @cached_property
    def ts_code(self) -> str | None:
        """The decoded TypeScript source of the ``Script.ts`` attachment.

        Computed once and cached. Returns ``None`` if there is no
        ``Script.ts`` attachment.
        """
        for attachment in self.attachments:
            if attachment.filename == "Script.ts":
                return base64.b64decode(
                    attachment.attachmentData.original, validate=True
                ).decode("utf-8")
        return None
