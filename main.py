# -*- coding: utf-8 -*-
"""
HTML Generator
"""

import time
from datetime import datetime, timedelta
from itertools import groupby

from jinja2 import Environment, FileSystemLoader
from loglan_db import run_with_context
from loglan_db.model import Event, Key, Setting
from loglan_db.model_html import HTMLExportWord, HTMLExportDefinition

from config import HTML_EXPORT_DIRECTORY_PATH_LOCAL as EXPORT_PATH
from config import log, DEFAULT_LANGUAGE, DEFAULT_STYLE

# TODO Add other languages support


def prepare_dictionary_l(style: str = DEFAULT_STYLE, lex_event: Event = None):
    """

    :param style:
    :param lex_event:
    :return:
    """
    log.info("Start Loglan dictionary preparation")
    if lex_event is None:
        lex_event = Event.latest()
    log.debug("Required Lexical Event is %s", lex_event.name)

    log.debug("Get data from Database")
    all_words = HTMLExportWord.by_event(event_id=lex_event.id).all()[1350:1400]

    log.debug("Grouping total %s words by name", len(all_words))
    grouped_words = groupby(all_words, lambda ent: ent.name)
    log.debug("Making dictionary with grouped words")
    group_words = {k: list(g) for k, g in grouped_words}

    log.debug("Grouping %s word groups by first letter", len(group_words))
    grouped_letters = groupby(group_words, lambda ent: ent[0].upper())
    log.debug("Making dictionary with grouped letters")
    names_grouped_by_letter = {k: list(g) for k, g in grouped_letters}

    log.debug("Making main export dictionary with %s letters" % len(names_grouped_by_letter))
    dictionary = {}
    for letter, names in names_grouped_by_letter.items():
        log.debug("Current letter: %s" % letter)
        dictionary[letter] = [{
            "name": group_words[name][0].name,
            "meanings": [w.meaning(style=style) for w in group_words[name]]} for name in names]
    log.info("End Loglan dictionary preparation - %s letters totally", len(dictionary))
    return dictionary


def prepare_dictionary_e(
        style: str = DEFAULT_STYLE,
        key_language: str = DEFAULT_LANGUAGE,
        lex_event: Event = None):
    """

    :param style:
    :param key_language:
    :param lex_event:
    :return:
    """
    def check_events(definition: HTMLExportDefinition, event_id: int):
        if definition.source_word.event_start_id > event_id:
            return False
        if definition.source_word.event_end_id is None:
            return True
        if definition.source_word.event_end_id > event_id:
            return True
        return False
    log.info("Start %s dictionary preparation", key_language.capitalize())

    if not lex_event:
        lex_event = Event.latest()

    log.debug("Get Key's data from Database")
    all_keys = Key.query.order_by(Key.word)\
        .filter(Key.language == key_language).all()[1600:1700]
    all_keys_words = [key.word for key in all_keys]

    log.debug("Grouping %s keys by word", len(all_keys))
    grouped_keys = groupby(all_keys, lambda ent: ent.word)

    log.debug("Making dictionary with grouped keys")
    group_keys = {
        k: [HTMLExportDefinition.export_for_english(d, word=k, style=style)
            for d in list(g)[0].definitions if check_events(d, lex_event.id)]
        for k, g in grouped_keys}
    log.debug("Grouping keys by first letter")
    grouped_letters = groupby(all_keys_words, lambda ent: ent[0].upper())
    log.debug("Making dictionary with grouped letters")
    key_names_grouped_by_letter = {k: list(g) for k, g in grouped_letters}

    log.debug("Making main export dictionary")
    dictionary = {
        letter: {name: group_keys[name] for name in names}
        for letter, names in key_names_grouped_by_letter.items()}
    log.info("End %s dictionary preparation - %s items totally", key_language.capitalize(), len(dictionary))
    return dictionary


def prepare_technical_info(lex_event: Event = None):
    """
    :param lex_event:
    :return:
    """
    generation_date = datetime.now().strftime("%d.%m.%Y")
    db_release = Setting.query.order_by(-Setting.id).first().db_release
    if not lex_event:
        lex_event = Event.latest()

    return {
        "Generated": generation_date,
        "Database": db_release,
        "LexEvent": lex_event.annotation, }


@run_with_context
def generate_dictionary_file(
        entities_language: str = "loglan",
        style: str = DEFAULT_STYLE,
        lex_event: Event = None,
        timestamp: str = None):
    """
    :param entities_language: [ loglan, english ]
    :param style: [ normal, ultra ]
    :param lex_event:
    :param timestamp:
    """
    if not lex_event:
        lex_event = Event.latest()

    env = Environment(loader=FileSystemLoader('templates'))

    if entities_language == "loglan":
        data = prepare_dictionary_l(style=style, lex_event=lex_event)
    else:
        data = prepare_dictionary_e(style=style, lex_event=lex_event)

    template = env.get_template(f'{entities_language}/words_{style}.html')
    tech = prepare_technical_info(lex_event=lex_event)
    render = template.render(dictionary=data, technical=tech)

    name = "L-to-E" if entities_language == "loglan" else "E-to-L"
    timestamp = datetime.now().strftime('%y%m%d%H%M') if not timestamp else timestamp

    file = f"{EXPORT_PATH}{name}-{tech['Database']}-{timestamp}_{lex_event.suffix}_{style[0].lower()}.html"
    text_file = open(file, "w", encoding="utf-8")
    text_file.write(render)
    text_file.close()


def generate_dictionaries():
    """
    :return:
    """
    log.info("START DICTIONARY HTML CREATION")
    start_time = time.monotonic()
    timestamp = datetime.now().strftime('%y%m%d%H%M')
    generate_dictionary_file(entities_language="loglan", timestamp=timestamp)
    generate_dictionary_file(entities_language="english", timestamp=timestamp)
    log.info("ELAPSED TIME IN MINUTES: %s\n", timedelta(minutes=time.monotonic() - start_time))


if __name__ == "__main__":
    generate_dictionaries()
