import sys
import json
import yaml
from pathlib import Path
from typing import Any, Dict, List, Tuple

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.timezone import now

from student_registration.backends.models import Metric


REQUIRED_FIELDS = {
    "key": str,
    "label": str,
    "description": str,
    "sql_view": str,
    "value_column": str,
    "allowed_breakdowns": list,
    "allowed_filters": list,
    "default_time_column": str,
    "unit": str,
}

OPTIONAL_FIELDS_WITH_DEFAULTS = {
    "decimals": 0,
    "min_sample_size": 15,
    "rounding": 5,
    "owner_team": "T4D/Unknown",
    "tags": [],
    "freshness_sla_minutes": 60,
    "meta": {},
}

def load_catalog_file(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        raise CommandError(f"File not found: {path}")
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in (".yml", ".yaml"):
        data = yaml.safe_load(text)
    elif path.suffix.lower() == ".json":
        data = json.loads(text)
    else:
        raise CommandError("Unsupported file type. Use .yaml/.yml or .json")
    if not isinstance(data, list):
        raise CommandError("Catalog root must be a list of metric objects")
    return data

def validate_item(i: Dict[str, Any]) -> Tuple[bool, str]:
    # Required fields & types
    for f, typ in REQUIRED_FIELDS.items():
        if f not in i:
            return False, f"Missing required field: {f}"
        if not isinstance(i[f], typ):
            return False, f"Field `{f}` must be {typ.__name__}"

    # Types for simple lists
    if not all(isinstance(x, str) for x in i["allowed_breakdowns"]):
        return False, "allowed_breakdowns must be a list[str]"
    if not all(isinstance(x, str) for x in i["allowed_filters"]):
        return False, "allowed_filters must be a list[str]"

    # Optional defaults
    for f, default in OPTIONAL_FIELDS_WITH_DEFAULTS.items():
        i.setdefault(f, default)

    # Normalize tags to unique, sorted strings
    i["tags"] = sorted({str(t).strip() for t in i.get("tags", []) if str(t).strip()})

    # meta must be a dict
    if not isinstance(i["meta"], dict):
        return False, "meta must be an object/dict"

    # Guardrails
    if i["decimals"] < 0 or i["decimals"] > 6:
        return False, "decimals must be between 0 and 6"
    if i["min_sample_size"] < 0:
        return False, "min_sample_size must be >= 0"
    if i["rounding"] not in (1, 2, 5, 10, 20, 50, 100):
        return False, "rounding should be one of 1,2,5,10,20,50,100"
    if i["freshness_sla_minutes"] < 0:
        return False, "freshness_sla_minutes must be >= 0"

    return True, ""

class Command(BaseCommand):
    help = "Load/update the metrics catalog from a YAML/JSON file into the Metric table."

    def add_arguments(self, parser):
        parser.add_argument("--file", required=True, help="Path to catalog file (.yaml/.yml/.json)")
        parser.add_argument("--dry-run", action="store_true", help="Validate and show changes without writing")
        parser.add_argument("--only-keys", nargs="*", default=[], help="Optional subset of metric keys to apply")
        parser.add_argument("--delete-missing", action="store_true",
                            help="Delete Metric rows not present in the catalog (CAUTION)")

    def handle(self, *args, **opts):
        path = Path(opts["file"])
        dry = opts["dry_run"]
        only_keys = set(opts["only_keys"] or [])
        delete_missing = opts["delete_missing"]

        items = load_catalog_file(path)

        # Detect duplicate keys in input
        seen = set()
        dup = [i["key"] for i in items if "key" in i and (i["key"] in seen or seen.add(i["key"]))]
        if dup:
            raise CommandError(f"Duplicate keys found in the catalog: {dup}")

        # Validate & normalize
        valid_items = []
        for i in items:
            ok, msg = validate_item(i)
            if not ok:
                raise CommandError(f"Invalid metric `{i.get('key','<no-key>')}`: {msg}")
            valid_items.append(i)

        if only_keys:
            valid_items = [i for i in valid_items if i["key"] in only_keys]
            if not valid_items:
                self.stdout.write(self.style.WARNING("No items match --only-keys. Nothing to do."))
                return

        # Compute diffs
        db_by_key: Dict[str, Metric] = {m.key: m for m in Metric.objects.all()}
        input_keys = {i["key"] for i in valid_items}
        to_create, to_update = [], []
        for i in valid_items:
            existing = db_by_key.get(i["key"])
            if not existing:
                to_create.append(i)
            else:
                # Determine if anything changed (simple dict compare on serialized shape)
                changed = (
                    existing.label != i["label"] or
                    existing.description != i["description"] or
                    existing.sql_view != i["sql_view"] or
                    existing.value_column != i["value_column"] or
                    list(existing.allowed_breakdowns) != list(i["allowed_breakdowns"]) or
                    list(existing.allowed_filters) != list(i["allowed_filters"]) or
                    existing.default_time_column != i["default_time_column"] or
                    existing.unit != i["unit"] or
                    existing.decimals != i["decimals"] or
                    existing.min_sample_size != i["min_sample_size"] or
                    existing.rounding != i["rounding"] or
                    existing.owner_team != i["owner_team"] or
                    list(existing.tags) != list(i["tags"]) or
                    existing.freshness_sla_minutes != i["freshness_sla_minutes"] or
                    dict(existing.meta or {}) != dict(i["meta"] or {})
                )
                if changed:
                    to_update.append(i)

        to_delete = []
        if delete_missing:
            to_delete = [k for k in db_by_key.keys() if k not in input_keys]

        # Report
        self.stdout.write(self.style.MIGRATE_HEADING(f"Catalog: {path}"))
        self.stdout.write(f"  Dry run: {dry}")
        self.stdout.write(f"  Items in file: {len(valid_items)}")
        self.stdout.write(f"  Create: {len(to_create)}  Update: {len(to_update)}  Delete: {len(to_delete)}")

        if dry:
            # Print keys for visibility
            if to_create:
                self.stdout.write(self.style.SUCCESS("  + To create: " + ", ".join(i['key'] for i in to_create)))
            if to_update:
                self.stdout.write(self.style.WARNING("  ~ To update: " + ", ".join(i['key'] for i in to_update)))
            if to_delete:
                self.stdout.write(self.style.ERROR("  - To delete: " + ", ".join(to_delete)))
            return

        # Apply changes transactionally
        with transaction.atomic():
            for i in to_create:
                Metric.objects.create(**i)
            for i in to_update:
                Metric.objects.filter(key=i["key"]).update(**i)
            if to_delete:
                Metric.objects.filter(key__in=to_delete).delete()

        self.stdout.write(self.style.SUCCESS(
            f"Done at {now().isoformat(timespec='seconds')}. "
            f"Created={len(to_create)} Updated={len(to_update)} Deleted={len(to_delete)}"
        ))
