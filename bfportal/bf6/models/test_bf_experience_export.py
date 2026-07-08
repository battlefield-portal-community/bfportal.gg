# flake8: noqa: D101
from __future__ import annotations

import base64

from bf6.models.bf_experience_export import (
    Attachment,
    AttachmentData,
    ExperienceExport,
    MapRotationEntry,
    Workspace,
    WorkspaceBlock,
    WorkspaceBlocks,
    WorkspaceMod,
)
from django.test import SimpleTestCase
from pydantic import ValidationError


def _b64(text: str) -> str:
    """Encode ``text`` as a base64 string."""
    return base64.b64encode(text.encode("utf-8")).decode("ascii")


def _attachment_data(**overrides) -> dict:
    """A minimal valid ``AttachmentData`` payload."""
    return {"original": _b64("original"), **overrides}


def _attachment(**overrides) -> dict:
    """A minimal valid ``Attachment`` payload."""
    data = {
        "id": "att-1",
        "version": "1",
        "filename": "Script.ts",
        "isProcessable": True,
        "processingStatus": 0,
        "attachmentData": _attachment_data(),
        "attachmentType": 0,
    }
    data.update(overrides)
    return data


class AttachmentDataTests(SimpleTestCase):
    def test_valid_base64_passes(self):
        payload = _b64("hello world")
        data = AttachmentData(original=payload, compiled=payload)
        self.assertEqual(data.original, payload)
        self.assertEqual(data.compiled, payload)

    def test_compiled_defaults_to_empty_string(self):
        data = AttachmentData(original=_b64("x"))
        self.assertEqual(data.compiled, "")

    def test_empty_string_is_allowed(self):
        # Empty payloads short-circuit validation and are returned as-is.
        data = AttachmentData(original="", compiled="")
        self.assertEqual(data.original, "")
        self.assertEqual(data.compiled, "")

    def test_invalid_base64_original_raises(self):
        with self.assertRaises(ValidationError) as ctx:
            AttachmentData(original="not!valid!base64!")
        self.assertIn("is not valid base64", str(ctx.exception))

    def test_invalid_base64_compiled_raises(self):
        with self.assertRaises(ValidationError):
            AttachmentData(original=_b64("ok"), compiled="@@@notbase64@@@")

    def test_non_multiple_of_four_length_raises(self):
        # "abc" is not valid strict base64 (length not a multiple of 4).
        with self.assertRaises(ValidationError):
            AttachmentData(original="abc")


class AttachmentTests(SimpleTestCase):
    def test_defaults(self):
        attachment = Attachment(**_attachment())
        self.assertEqual(attachment.errors, [])
        self.assertIsNone(attachment.metadata)

    def test_missing_required_field_raises(self):
        payload = _attachment()
        del payload["filename"]
        with self.assertRaises(ValidationError):
            Attachment(**payload)

    def test_nested_attachment_data_is_parsed(self):
        attachment = Attachment(**_attachment())
        self.assertIsInstance(attachment.attachmentData, AttachmentData)


class MapRotationEntryTests(SimpleTestCase):
    def test_parses_nested_spatial_attachment(self):
        entry = MapRotationEntry(
            id="map-1",
            spatialAttachment=_attachment(filename="Spatial.bin"),
        )
        self.assertEqual(entry.id, "map-1")
        self.assertIsInstance(entry.spatialAttachment, Attachment)
        self.assertEqual(entry.spatialAttachment.filename, "Spatial.bin")


class WorkspaceBlockTests(SimpleTestCase):
    def test_deletable_defaults_true(self):
        block = WorkspaceBlock(type="rule", id="b1", x=1, y=2)
        self.assertTrue(block.deletable)

    def test_deletable_can_be_overridden(self):
        block = WorkspaceBlock(type="rule", id="b1", x=1, y=2, deletable=False)
        self.assertFalse(block.deletable)


class WorkspaceBlocksTests(SimpleTestCase):
    def test_blocks_defaults_empty(self):
        blocks = WorkspaceBlocks(languageVersion=1)
        self.assertEqual(blocks.blocks, [])

    def test_blocks_are_parsed(self):
        blocks = WorkspaceBlocks(
            languageVersion=1,
            blocks=[{"type": "rule", "id": "b1", "x": 0, "y": 0}],
        )
        self.assertEqual(len(blocks.blocks), 1)
        self.assertIsInstance(blocks.blocks[0], WorkspaceBlock)


class WorkspaceTests(SimpleTestCase):
    def test_mod_defaults_to_empty_workspace_mod(self):
        workspace = Workspace()
        self.assertIsInstance(workspace.mod, WorkspaceMod)
        self.assertIsInstance(workspace.mod.blocks, WorkspaceBlocks)
        self.assertEqual(workspace.mod.blocks.languageVersion, 0)
        self.assertEqual(workspace.mod.blocks.blocks, [])

    def test_mod_blocks_are_parsed(self):
        workspace = Workspace(
            mod={
                "blocks": {
                    "languageVersion": 2,
                    "blocks": [{"type": "modBlock", "id": "b1", "x": 10, "y": 10}],
                }
            }
        )
        self.assertEqual(workspace.mod.blocks.languageVersion, 2)
        self.assertEqual(len(workspace.mod.blocks.blocks), 1)
        self.assertIsInstance(workspace.mod.blocks.blocks[0], WorkspaceBlock)


class ExperienceExportTests(SimpleTestCase):
    def _minimal(self, **overrides) -> dict:
        data = {
            "name": "My Experience",
            "description": "A cool mode",
            "gameMode": "Conquest",
        }
        data.update(overrides)
        return data

    def test_minimal_required_fields(self):
        export = ExperienceExport(**self._minimal())
        self.assertEqual(export.name, "My Experience")
        self.assertEqual(export.description, "A cool mode")
        self.assertEqual(export.gameMode, "Conquest")

    def test_collection_and_object_defaults(self):
        export = ExperienceExport(**self._minimal())
        self.assertEqual(export.mutators, {})
        self.assertEqual(export.assetRestrictions, {})
        self.assertEqual(export.mapRotation, [])
        self.assertEqual(export.teamComposition, [])
        self.assertEqual(export.attachments, [])
        self.assertIsInstance(export.workspace, Workspace)
        self.assertIsInstance(export.workspace.mod, WorkspaceMod)
        self.assertEqual(export.workspace.mod.blocks.blocks, [])

    def test_missing_required_field_raises(self):
        payload = self._minimal()
        del payload["gameMode"]
        with self.assertRaises(ValidationError):
            ExperienceExport(**payload)

    def test_nested_structures_are_parsed(self):
        export = ExperienceExport(
            **self._minimal(
                mapRotation=[
                    {"id": "map-1", "spatialAttachment": _attachment()},
                ],
                attachments=[_attachment()],
            )
        )
        self.assertIsInstance(export.mapRotation[0], MapRotationEntry)
        self.assertIsInstance(export.attachments[0], Attachment)

    def test_ts_code_decodes_script_attachment(self):
        source = "const x: number = 1;\nconsole.log(x);"
        export = ExperienceExport(
            **self._minimal(
                attachments=[
                    _attachment(
                        filename="Script.ts",
                        attachmentData=_attachment_data(original=_b64(source)),
                    ),
                ]
            )
        )
        self.assertEqual(export.ts_code, source)

    def test_ts_code_returns_none_when_no_script(self):
        export = ExperienceExport(
            **self._minimal(
                attachments=[_attachment(filename="Strings.csv")],
            )
        )
        self.assertIsNone(export.ts_code)

    def test_ts_code_returns_none_with_no_attachments(self):
        export = ExperienceExport(**self._minimal())
        self.assertIsNone(export.ts_code)

    def test_ts_code_picks_first_matching_attachment(self):
        first = "first script"
        export = ExperienceExport(
            **self._minimal(
                attachments=[
                    _attachment(
                        filename="Script.ts",
                        attachmentData=_attachment_data(original=_b64(first)),
                    ),
                    _attachment(
                        filename="Script.ts",
                        attachmentData=_attachment_data(original=_b64("second")),
                    ),
                ]
            )
        )
        self.assertEqual(export.ts_code, first)

    def test_ts_code_is_cached(self):
        export = ExperienceExport(
            **self._minimal(
                attachments=[
                    _attachment(
                        filename="Script.ts",
                        attachmentData=_attachment_data(original=_b64("cached")),
                    ),
                ]
            )
        )
        # cached_property stores the result on the instance after first access.
        self.assertNotIn("ts_code", export.__dict__)
        first_access = export.ts_code
        self.assertIn("ts_code", export.__dict__)
        self.assertIs(export.ts_code, first_access)
