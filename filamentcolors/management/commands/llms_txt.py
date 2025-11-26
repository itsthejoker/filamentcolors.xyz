from __future__ import annotations

import os
from datetime import datetime, timezone

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Count, Q
from django.urls import reverse

from filamentcolors.models import Manufacturer, Swatch


class Command(BaseCommand):
    help = "Generate an llms.txt file with a concise project overview and key links."

    def handle(self, *args, **options):
        # Resolve output path (project static directory)
        static_root = getattr(settings, "STATIC_ROOT", os.path.join(settings.BASE_DIR, "static"))
        os.makedirs(static_root, exist_ok=True)
        out_path = os.path.join(static_root, "llms.txt")

        # Title (H1)
        title = "filamentcolors.xyz"

        # Summary (blockquote) — keep concise and informative
        summary = (
            "A public library of 3D‑printing filament colors. Browse swatches, compare hues, "
            "and explore manufacturer catalogs."
        )

        # Details paragraph(s) — avoid headings per spec
        details = (
            "Core concepts: a Swatch represents a single filament color entry; Manufacturers group "
            "related swatches. Library pages provide filters and sorts by manufacturer, type, and color family. "
            "Links below are relative to the site root."
        )

        # Build core/static route links via URL names where possible
        def link(name: str, url: str, notes: str | None = None) -> str:
            base = f"- [{name}]({url})"
            return base if not notes else f"{base}: {notes}"

        core_links: list[str] = [
            link("Home", reverse("homepage"), "Start here"),
            link("Library", reverse("library"), "All published colors"),
            link("Manufacturers", reverse("mfr_list"), "Browse by brand"),
            link("Inventory", reverse("inventory"), "Colors on‑hand for measurement"),
            link("Color Match", reverse("colormatch"), "Find nearest colors by input"),
            link("About", reverse("about"), "What this site is and FAQ"),
            link("The Librarians", reverse("about_us"), "Who maintains the library"),
            link("Donations", reverse("donations"), "How to donate filament for the library"),
            link("Monetary Donations", reverse("monetary_donations"), "How to support hosting costs"),
            link("API root", "/api/", "Public JSON endpoints"),
            link("Sitemap", reverse("django.contrib.sitemaps.views.sitemap"))
        ]

    # Dynamic Manufacturers section — only those with published swatches
        manufacturers_section: list[str] = []
        try:
            mfr_counts = (
                Manufacturer.objects
                .filter(swatch__published=True)
                .annotate(published_count=Count("swatch", filter=Q(swatch__published=True)))
                .order_by("name")
            )
            for m in mfr_counts:
                # Use manufacturer page URL
                try:
                    m_url = reverse("manufacturersort", args=(m.slug,))
                except Exception:
                    # Fallback to id if slug is missing (rare)
                    m_url = reverse("manufacturersort", args=(str(m.id),))
                p_count = getattr(m, 'published_count', 0)
                notes = f"{p_count} swatch{'es' if p_count > 1 else ''}"
                manufacturers_section.append(link(m.get_display_name(), m_url, notes))
        except Exception:
            # If DB unavailable (e.g., during collectstatic without DB), skip gracefully
            manufacturers_section.append("- No manufacturer data available.")

        # Dynamic Swatches section — sample of recently published swatches
        swatches_section: list[str] = []
        try:
            sample = (
                Swatch.objects.filter(published=True)
                .exclude(slug__isnull=True)
                .order_by("-date_published", "-date_added")[:25]
            )
            for s in sample:
                try:
                    url = s.get_absolute_url()
                except Exception:
                    # Fallback: use slug if available
                    url = f"/swatch/{s.slug or s.id}/"
                label_parts = [
                    (s.manufacturer.name if s.manufacturer_id else None),
                    s.color_name,
                    (s.filament_type.name if s.filament_type_id else None),
                ]
                label = " ".join([p for p in label_parts if p])
                swatches_section.append(link(label, url))
        except Exception:
            swatches_section.append("- No swatch data available.")

        # Optional section — useful but not essential
        optional_links: list[str] = []

        # Compose markdown in the requested order
        lines: list[str] = []
        lines.append(f"# {title}")
        lines.append("")
        lines.append(f"> {summary}")
        lines.append("")
        lines.append(details)
        lines.append("")

        if core_links:
            lines.append("## Core routes")
            lines.extend(core_links)
            lines.append("")

        if manufacturers_section:
            lines.append("## Manufacturers")
            lines.extend(manufacturers_section)
            lines.append("")

        if swatches_section:
            lines.append("## Sample swatches")
            lines.extend(swatches_section)
            lines.append("")

        if optional_links:
            lines.append("## Optional")
            lines.extend(optional_links)
            lines.append("")

        # Include a tiny footer timestamp to help cache invalidation (not a heading)
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
        lines.append(f"Generated: {now}")
        lines.append("")

        content = "\n".join(lines)

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)

        self.stdout.write(self.style.SUCCESS(f"llms.txt written to {out_path}"))
