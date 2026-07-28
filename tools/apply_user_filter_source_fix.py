from __future__ import annotations

import re
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "src/АнализЗамеровПроизводительности/Ext/ObjectModule.bsl"
SCD_PATH = ROOT / "src/АнализЗамеровПроизводительности/Templates/ОсновнаяСхемаКомпоновкиДанных/Ext/Template.xml"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8-sig", newline="\n")


def update_module() -> None:
    text = read_text(MODULE_PATH)

    new_region = '''#Область НастройкиФормыОтчета

Процедура ОпределитьНастройкиФормы(Форма, КлючВарианта, Настройки) Экспорт
	
	Настройки.События.ПередЗагрузкойНастроекВКомпоновщик = Истина;
	Настройки.События.ПриОпределенииПараметровВыбора = Истина;
	
	ПараметрыПерезагрузки = Новый Массив;
	ПараметрыПерезагрузки.Добавить(Новый ПараметрКомпоновкиДанных("Период"));
	ПараметрыПерезагрузки.Добавить(Новый ПараметрКомпоновкиДанных("ТолькоПользователиСЗамерами"));
	ПараметрыПерезагрузки.Добавить(Новый ПараметрКомпоновкиДанных("ПоказыватьНеактивныхПользователей"));
	Настройки.ЗагрузитьНастройкиПриИзмененииПараметров = ПараметрыПерезагрузки;
	
КонецПроцедуры

Процедура ПередЗагрузкойНастроекВКомпоновщик(
	Контекст,
	КлючСхемы,
	КлючВарианта,
	НовыеНастройкиКД,
	НовыеПользовательскиеНастройкиКД) Экспорт
	
	Если НовыеНастройкиКД = Неопределено Тогда
		Возврат;
	КонецЕсли;
	
	ЭлементОтбораПользователь = НайтиЭлементОтбораПользователь(НовыеНастройкиКД);
	Если ЭлементОтбораПользователь = Неопределено Тогда
		Возврат;
	КонецЕсли;
	
	Если Не ДоступенСписокПользователейИБ() Тогда
		ЭлементОтбораПользователь.Использование = Ложь;
		СообщитьОНедоступностиСпискаПользователей();
	КонецЕсли;
	
КонецПроцедуры

Процедура ПриОпределенииПараметровВыбора(Форма, СвойстваНастройки) Экспорт
	
	Если Строка(СвойстваНастройки.ПолеКД) <> "Пользователь" Тогда
		Возврат;
	КонецЕсли;
	
	СвойстваНастройки.ЗапросЗначенийВыбора.Текст = "";
	
	Если ТипЗнч(СвойстваНастройки.ЗначенияДляВыбора) <> Тип("СписокЗначений") Тогда
		Возврат;
	КонецЕсли;
	
	Если Не ДоступенСписокПользователейИБ() Тогда
		СвойстваНастройки.ЗначенияДляВыбора.Очистить();
		СвойстваНастройки.ОграничиватьВыборУказаннымиЗначениями = Истина;
		СообщитьОНедоступностиСпискаПользователей();
		Возврат;
	КонецЕсли;
	
	ТолькоПользователиСЗамерами = ЗначениеБулевогоПараметраОтчета(
		Форма,
		"ТолькоПользователиСЗамерами",
		Ложь);
	
	ПоказыватьНеактивныхПользователей = ЗначениеБулевогоПараметраОтчета(
		Форма,
		"ПоказыватьНеактивныхПользователей",
		Истина);
	
	ИсторическиеЗначения = ПолучитьИсторическиеПредставленияПользователей(Форма);
	РезультатПолучения = ПолучитьТекущиеПредставленияПользователей(
		ИсторическиеЗначения,
		ТолькоПользователиСЗамерами,
		ПоказыватьНеактивныхПользователей);
	
	Если Не РезультатПолучения.Доступен Тогда
		СвойстваНастройки.ЗначенияДляВыбора.Очистить();
		СвойстваНастройки.ОграничиватьВыборУказаннымиЗначениями = Истина;
		СообщитьОНедоступностиСпискаПользователей();
		Возврат;
	КонецЕсли;
	
	СвойстваНастройки.ЗначенияДляВыбора.Очистить();
	ДобавленныеЗначения = Новый Соответствие;
	
	Для Каждого ЭлементСписка Из РезультатПолучения.Значения Цикл
		ДобавитьЗначениеВыбора(
			СвойстваНастройки.ЗначенияДляВыбора,
			ДобавленныеЗначения,
			ЭлементСписка.Значение,
			ЭлементСписка.Представление);
	КонецЦикла;
	
	Для Каждого ЭлементСписка Из ИсторическиеЗначения Цикл
		Если ДобавленныеЗначения.Получить(Строка(ЭлементСписка.Значение)) = Неопределено Тогда
			ДобавитьЗначениеВыбора(
				СвойстваНастройки.ЗначенияДляВыбора,
				ДобавленныеЗначения,
				ЭлементСписка.Значение,
				НСтр("ru = '[Исторический] '") + ЭлементСписка.Представление);
		КонецЕсли;
	КонецЦикла;
	
	СвойстваНастройки.ОграничиватьВыборУказаннымиЗначениями = Истина;
	
КонецПроцедуры

#КонецОбласти'''

    text, count = re.subn(
        r"#Область НастройкиФормыОтчета.*?#КонецОбласти",
        new_region,
        text,
        count=1,
        flags=re.S,
    )
    if count != 1:
        raise RuntimeError("Не найдена единственная область НастройкиФормыОтчета")

    text, count = re.subn(
        r"Процедура ДобавитьПараметрСхемыСпискаПользователей\(.*?(?=Функция НайтиЭлементОтбораПользователь\()",
        "",
        text,
        count=1,
        flags=re.S,
    )
    if count != 1:
        raise RuntimeError("Не найден блок программного создания настроек пользователей")

    text, count = re.subn(
        r"Функция ЭтоПараметрНастройкиСпискаПользователей\(.*?КонецФункции\s*",
        "",
        text,
        count=1,
        flags=re.S,
    )
    if count != 1:
        raise RuntimeError("Не найдена функция определения программных параметров")

    forbidden = (
        "ДобавитьПараметрСхемыСпискаПользователей",
        "ДобавитьНастройкиПользователейВВариантыСхемы",
        "НастроитьНастройкиПользователей",
        "НастроитьЭлементОтбораПользователь",
        "ДобавитьПользовательскийПараметрНастроек",
        "ЭтоПараметрНастройкиСпискаПользователей",
    )
    remaining = [name for name in forbidden if name in text]
    if remaining:
        raise RuntimeError(f"В модуле осталась программная модификация СКД: {remaining}")

    write_text(MODULE_PATH, text)


def schema_parameter(name: str, title: str, default: bool) -> str:
    value = "true" if default else "false"
    return f'''\n\t<parameter>
\t\t<name>{name}</name>
\t\t<title xsi:type="v8:LocalStringType">
\t\t\t<v8:item>
\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t<v8:content>{title}</v8:content>
\t\t\t</v8:item>
\t\t</title>
\t\t<valueType>
\t\t\t<v8:Type>xs:boolean</v8:Type>
\t\t</valueType>
\t\t<value xsi:type="xs:boolean">{value}</value>
\t\t<useRestriction>false</useRestriction>
\t\t<use>Always</use>
\t</parameter>'''


def variant_parameter(indent: str, variant: str, name: str, title: str, default: bool) -> str:
    value = "true" if default else "false"
    setting_id = uuid.uuid5(
        uuid.NAMESPACE_URL,
        f"PerformanceMeasurementsAnalyzer/{variant}/{name}",
    )
    item_indent = indent + "\t"
    inner = item_indent + "\t"
    return (
        f"\n{item_indent}<dcscor:item xsi:type=\"dcsset:SettingsParameterValue\">"
        f"\n{inner}<dcscor:parameter>{name}</dcscor:parameter>"
        f"\n{inner}<dcscor:value xsi:type=\"xs:boolean\">{value}</dcscor:value>"
        f"\n{inner}<dcsset:userSettingID>{setting_id}</dcsset:userSettingID>"
        f"\n{inner}<dcsset:userSettingPresentation xsi:type=\"xs:string\">{title}</dcsset:userSettingPresentation>"
        f"\n{item_indent}</dcscor:item>"
    )


def update_scd() -> None:
    text = read_text(SCD_PATH)

    if "<name>ТолькоПользователиСЗамерами</name>" not in text:
        marker = "\n\t<settingsVariant>"
        position = text.find(marker)
        if position < 0:
            raise RuntimeError("Не найден первый вариант настроек СКД")
        additions = schema_parameter(
            "ТолькоПользователиСЗамерами",
            "Только пользователи с замерами за период",
            False,
        ) + schema_parameter(
            "ПоказыватьНеактивныхПользователей",
            "Показывать неактивных и служебных пользователей",
            True,
        )
        text = text[:position] + additions + text[position:]

    user_filter_pattern = re.compile(
        r'(?P<prefix><dcsset:item xsi:type="dcsset:FilterItemComparison">\s*'
        r'<dcsset:use>false</dcsset:use>\s*'
        r'<dcsset:left xsi:type="dcscor:Field">Пользователь</dcsset:left>\s*)'
        r'<dcsset:comparisonType>Contains</dcsset:comparisonType>\s*'
        r'<dcsset:right xsi:type="xs:string"/>',
        re.S,
    )

    def replace_user_filter(match: re.Match[str]) -> str:
        indent_match = re.search(r"\n([\t ]*)<dcsset:comparisonType>", match.group(0))
        if indent_match is None:
            raise RuntimeError("Не определён отступ отбора Пользователь")
        indent = indent_match.group(1)
        inner = indent + "\t"
        right = (
            f'<dcsset:comparisonType>InList</dcsset:comparisonType>'
            f'\n{indent}<dcsset:right xsi:type="v8:ValueListType">'
            f'\n{inner}<v8:valueType/>'
            f'\n{inner}<v8:lastId xsi:type="xs:decimal">-1</v8:lastId>'
            f'\n{indent}</dcsset:right>'
        )
        return match.group("prefix") + right

    text, filter_count = user_filter_pattern.subn(replace_user_filter, text)
    if filter_count != 4:
        raise RuntimeError(f"Ожидалось 4 отбора Пользователь, изменено: {filter_count}")

    variants = (
        "АнализПроизводительностиAPDEX",
        "ДинамикаДлительностиОпераций_Час",
        "ДинамикаДлительностиОпераций_День",
        "ДинамикаДлительностиОперацийПоПользователям_Час",
    )

    variant_pattern = re.compile(
        r"<settingsVariant>\s*<dcsset:name>(?P<name>[^<]+)</dcsset:name>.*?</settingsVariant>",
        re.S,
    )
    changed_variants: set[str] = set()

    def add_variant_parameters(match: re.Match[str]) -> str:
        block = match.group(0)
        name = match.group("name")
        if name not in variants:
            return block
        if "<dcscor:parameter>ТолькоПользователиСЗамерами</dcscor:parameter>" in block:
            return block
        close_match = re.search(r"\n(?P<indent>[\t ]*)</dcsset:dataParameters>", block)
        if close_match is None:
            raise RuntimeError(f"В варианте {name} не найден dataParameters")
        indent = close_match.group("indent")
        additions = variant_parameter(
            indent,
            name,
            "ТолькоПользователиСЗамерами",
            "Только пользователи с замерами за период",
            False,
        ) + variant_parameter(
            indent,
            name,
            "ПоказыватьНеактивныхПользователей",
            "Показывать неактивных и служебных пользователей",
            True,
        )
        insertion = close_match.start()
        changed_variants.add(name)
        return block[:insertion] + additions + block[insertion:]

    text = variant_pattern.sub(add_variant_parameters, text)
    if changed_variants != set(variants):
        raise RuntimeError(
            "Параметры добавлены не во все варианты: "
            f"{sorted(changed_variants)}"
        )

    if text.count("<dcsset:comparisonType>InList</dcsset:comparisonType>") < 4:
        raise RuntimeError("После преобразования отсутствуют четыре отбора InList")
    if text.count("<dcscor:parameter>ТолькоПользователиСЗамерами</dcscor:parameter>") != 4:
        raise RuntimeError("Параметр ТолькоПользователиСЗамерами добавлен не во все варианты")
    if text.count("<dcscor:parameter>ПоказыватьНеактивныхПользователей</dcscor:parameter>") != 4:
        raise RuntimeError("Параметр ПоказыватьНеактивныхПользователей добавлен не во все варианты")

    write_text(SCD_PATH, text)
    ET.parse(SCD_PATH)


if __name__ == "__main__":
    update_module()
    update_scd()
    print("Канонические исходники внешнего отчёта исправлены и проверены.")
