# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Keep language navigation on the current page and label unapproved previews."""


def on_page_context(context, *, page, config, nav):
    """Use MkDocs' upstream hook to preserve the page path across languages."""

    root = config.extra["localeRoot"]
    config.extra["alternate"] = [
        {"name": name, "lang": locale, "link": f"{root}/{locale}/{page.url}"}
        for locale, name in (("en", "English"), ("ru", "Русский"), ("zh-CN", "简体中文"))
    ]
    return context


def on_page_markdown(markdown, *, page, config, files):
    """Clearly distinguish human-review previews from publishable translations."""

    banner = config.extra.get("localePreviewBanner", "")

    if banner:
        title = config.extra.get("localePreviewTitle", "Review preview")
        return f'!!! warning "{title}"\n\n    {banner}\n\n{markdown}'

    return markdown
