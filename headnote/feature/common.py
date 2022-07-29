# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================
"""Footer Header Extraction Step
=============================

TODO:
    what should we do with empty header/footer
"""

import collections

import serializeraw
import utila

import headnote.common
import headnote.utils


def work(
    text: str,
    textpositions: str,
    # fontheader: str,
    # fontcontent: str,
    horizontals: str,
    pages=None,
) -> str:
    # load
    horizontals = serializeraw.load_horizontals(
        horizontals,
        pages=pages,
        width_min=50.0,
    )
    ptns = serializeraw.ptn_fromfile(
        text,
        textpositions,
        # fontheader,
        # fontcontent,
        pages=pages,
    )
    ptns = headnote.utils.rotate_ifrequired(ptns)
    # work
    result = headnote.common.CommonTextStrategy(
        horizontals,
        ptns,
    ).result()
    validate(result)
    # dump
    dumped = serializeraw.dump_headerfooter(result)
    return dumped


def validate(items: list):
    """Validate list of pageable items.

    If some `page` attribute is duplicated, raise ValueError.

    Args:
        items(list): list of objects with <page,content>
    Raises:
        ValueError: if some page attribute is duplicated.
    """
    # TODO: REMOVE AFTER UPGRADING IAMRAW
    counter = collections.Counter()
    for item in items:
        counter[item.page] += 1
    msg = []
    for page, value in counter.most_common():
        if value <= 1:
            continue
        msg.append(f'duplicated page: {page} ({value})')
    if msg:
        raise ValueError(utila.NEWLINE.join(msg))
