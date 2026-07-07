from __future__ import annotations

import base64
import binascii
from dataclasses import dataclass, field
from functools import cached_property
from typing import Any


@dataclass
class AttachmentData:
    """Base64 payloads carried by an attachment."""

    original: str
    compiled: str = ""

    def __post_init__(self) -> None:
        """Validate that the payloads are decodable base64."""
        for name in ("original", "compiled"):
            value = getattr(self, name)
            if not value:
                continue
            try:
                base64.b64decode(value, validate=True)
            except (binascii.Error, ValueError) as exc:
                raise ValueError(
                    f"AttachmentData.{name} is not valid base64: {exc}"
                ) from exc


@dataclass
class Attachment:
    """A file attached to an experience (script, map, strings, ...)."""

    id: str
    version: str
    filename: str
    isProcessable: bool
    processingStatus: int
    attachmentData: AttachmentData
    attachmentType: int
    errors: list[Any] = field(default_factory=list)
    metadata: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Attachment:
        """Build an ``Attachment`` (and its nested data) from a JSON dict."""
        return cls(
            id=data["id"],
            version=data["version"],
            filename=data["filename"],
            isProcessable=data["isProcessable"],
            processingStatus=data["processingStatus"],
            attachmentData=AttachmentData(**data["attachmentData"]),
            attachmentType=data["attachmentType"],
            errors=data.get("errors", []),
            metadata=data.get("metadata"),
        )


@dataclass
class MapRotationEntry:
    """A single map in the rotation with its spatial attachment."""

    id: str
    spatialAttachment: Attachment


@dataclass
class WorkspaceBlock:
    """A block placed on the visual scripting workspace."""

    type: str
    id: str
    x: int
    y: int
    deletable: bool = True


@dataclass
class WorkspaceBlocks:
    """The set of blocks in the workspace along with their language version."""

    languageVersion: int
    blocks: list[WorkspaceBlock] = field(default_factory=list)


@dataclass
class Workspace:
    """The visual scripting workspace (`mod`) of an experience."""

    mod: dict[str, Any] = field(default_factory=dict)


@dataclass
class Experience:
    """A Battlefield Portal experience as exported to JSON."""

    name: str
    description: str
    gameMode: str
    mutators: dict[str, Any] = field(default_factory=dict)
    assetRestrictions: dict[str, Any] = field(default_factory=dict)
    mapRotation: list[MapRotationEntry] = field(default_factory=list)
    workspace: Workspace = field(default_factory=Workspace)
    teamComposition: list[Any] = field(default_factory=list)
    attachments: list[Attachment] = field(default_factory=list)

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

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Experience:
        """Build an ``Experience`` from a decoded JSON dict."""
        return cls(
            name=data["name"],
            description=data["description"],
            gameMode=data["gameMode"],
            mutators=data.get("mutators", {}),
            assetRestrictions=data.get("assetRestrictions", {}),
            mapRotation=[
                MapRotationEntry(
                    id=entry["id"],
                    spatialAttachment=Attachment.from_dict(entry["spatialAttachment"]),
                )
                for entry in data.get("mapRotation", [])
            ],
            workspace=Workspace(mod=data.get("workspace", {}).get("mod", {})),
            teamComposition=data.get("teamComposition", []),
            attachments=[
                Attachment.from_dict(att) for att in data.get("attachments", [])
            ],
        )
