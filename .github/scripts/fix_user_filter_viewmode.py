from __future__ import annotations

import re
from pathlib import Path

SCHEMA_PATH = Path(
    "src/АнализЗамеровПроизводительности/Templates/"
    "ОсновнаяСхемаКомпоновкиДанных/Ext/Template.xml"
)


def add_view_mode_to_user_filters(text: str) -> tuple[str, int]:
    pattern = re.compile(
        r"(<dcsset:item xsi:type=\"dcsset:FilterItemComparison\">"
        r"(?:(?!</dcsset:item>).)*?"
        r"<dcsset:left xsi:type=\"dcscor:Field\">Пользователь</dcsset:left>"
        r"(?:(?!</dcsset:item>).)*?"
        r"<dcsset:comparisonType>InList</dcsset:comparisonType>"
        r"(?:(?!</dcsset:item>).)*?)"
        r"(?P<indent>\s*)<dcsset:userSettingID>",
        re.DOTALL,
    )

    def replace(match: re.Match[str]) -> str:
        block = match.group(1)
        if "<dcsset:viewMode>" in block:
            return match.group(0)
        indent = match.group("indent")
        return (
            block
            + indent
            + "<dcsset:viewMode>QuickAccess</dcsset:viewMode>"
            + indent
            + "<dcsset:userSettingID>"
        )

    return pattern.subn(replace, text)


def add_view_mode_to_parameter(text: str, parameter: str) -> tuple[str, int]:
    pattern = re.compile(
        r"(<dcscor:item xsi:type=\"dcsset:SettingsParameterValue\">"
        r"(?:(?!</dcscor:item>).)*?"
        rf"<dcscor:parameter>{re.escape(parameter)}</dcscor:parameter>"
        r"(?:(?!</dcscor:item>).)*?)"
        r"(?P<indent>\s*)<dcsset:userSettingID>",
        re.DOTALL,
    )

    def replace(match: re.Match[str]) -> str:
        block = match.group(1)
        if "<dcsset:viewMode>" in block:
            return match.group(0)
        indent = match.group("indent")
        return (
            block
            + indent
            + "<dcsset:viewMode>Normal</dcsset:viewMode>"
            + indent
            + "<dcsset:userSettingID>"
        )

    return pattern.subn(replace, text)


def main() -> None:
    text = SCHEMA_PATH.read_text(encoding="utf-8-sig")

    text, user_filter_count = add_view_mode_to_user_filters(text)
    text, only_measured_count = add_view_mode_to_parameter(
        text, "ТолькоПользователиСЗамерами"
    )
    text, inactive_count = add_view_mode_to_parameter(
        text, "ПоказыватьНеактивныхПользователей"
    )

    expected = {
        "user filters": (user_filter_count, 4),
        "only measured": (only_measured_count, 4),
        "inactive": (inactive_count, 4),
    }
    errors = [
        f"{name}: changed {actual}, expected {wanted}"
        for name, (actual, wanted) in expected.items()
        if actual != wanted
    ]
    if errors:
        raise RuntimeError("; ".join(errors))

    if text.count("<dcsset:viewMode>QuickAccess</dcsset:viewMode>") < 4:
        raise RuntimeError("QuickAccess view mode was not added to all user filters")

    SCHEMA_PATH.write_text("\ufeff" + text, encoding="utf-8")


if __name__ == "__main__":
    main()
