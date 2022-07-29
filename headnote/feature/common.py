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

import serializeraw

import headnote.strategy.common
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
    horizontals = headnote.utils.rotate_horizontals_ifrequired(
        horizontals,
        ptns,
    )
    # work
    result = headnote.strategy.common.CommonTextStrategy(
        horizontals,
        ptns,
    ).result()
    # dump
    dumped = serializeraw.dump_headerfooter(result)
    return dumped
