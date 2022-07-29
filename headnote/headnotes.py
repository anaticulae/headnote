# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================
"""Analyze content and structure of header area
============================================
"""

import elements
import iamraw
import utila


def parse(content: str):
    result = []
    strategies = [
        parse_title,
        parse_pagenumber,
        parse_rawtext,
    ]
    for item in content:
        parsed = None
        for strategy in strategies:
            parsed = strategy(item.text, item.bounding)
            if parsed:
                break
        if not parsed:
            parsed: iamraw.RawText = iamraw.RawText(text=item.text.strip())
        result.append(parsed)
    return result


def parse_rawtext(text: str, _=None):  # pylint:disable=W0613
    if text.count(utila.NEWLINE) <= 2:
        return None
    return iamraw.RawText(text=text.strip())


def parse_pagenumber(text: str, _=None):  # pylint:disable=W0613
    text = text.strip()
    if not elements.ispagenumber(text):
        return None
    return iamraw.PageInformation(value=text, raw=text)


def parse_title(text: str, _=None) -> iamraw.HeaderTitle:  # pylint:disable=W0613
    regex = parse_title_regex(text)
    if regex:
        return regex
    contemporary = parse_title_contemporary(text)
    if contemporary:
        return contemporary
    return None


def parse_title_regex(text: str) -> iamraw.HeaderTitle:
    parsed = elements.parse_headline(text)
    if not parsed:
        return None
    result = iamraw.HeaderTitle(
        title=parsed[0],
        raw=text,
    )
    return result


def parse_title_contemporary(text: str) -> iamraw.HeaderTitle:
    """Analyze `text` based on a contemporary(`TITLES`) lookup"""
    if not elements.isheadline(text):
        return None
    title = text.strip().title()
    return iamraw.HeaderTitle(title=title, raw=text)
