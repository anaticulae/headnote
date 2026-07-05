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

import elementae
import iamraw
import utilo


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
            parsed = strategy(item.text)
            if parsed:
                parsed.box = tuple(item.bounding)
                break
        if not parsed:
            parsed: iamraw.RawText = iamraw.RawText(
                text=item.text.strip(),
                box=tuple(item.bounding),
            )
        result.append(parsed)
    return result


@utilo.cacheme
def parse_rawtext(text: str):
    if text.count(utilo.NEWLINE) <= 2:
        return None
    result = iamraw.RawText(text=text.strip())
    return result


@utilo.cacheme
def parse_pagenumber(text: str):
    text = text.strip()
    if not elementae.ispagenumber(text):
        return None
    result = iamraw.PageInformation(value=text, raw=text)
    return result


@utilo.cacheme
def parse_title(text: str) -> iamraw.HeaderTitle:
    regex = parse_title_regex(text)
    if regex:
        return regex
    contemporary = parse_title_contemporary(text)
    if contemporary:
        return contemporary
    return None


def parse_title_regex(text: str) -> iamraw.HeaderTitle:
    parsed = elementae.parse_headline(text)
    if not parsed:
        return None
    result = iamraw.HeaderTitle(
        title=parsed[0],
        raw=text,
    )
    return result


def parse_title_contemporary(text: str) -> iamraw.HeaderTitle:
    """Analyze `text` based on a contemporary(`TITLES`) lookup"""
    if not elementae.isheadline(text):
        return None
    title = text.strip().title()
    result = iamraw.HeaderTitle(
        title=title,
        raw=text,
    )
    return result
