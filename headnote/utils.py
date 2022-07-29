# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import math

import iamraw
import texmex
import utila


def rotate_ifrequired(navigators):
    result = []
    for ptn in navigators:
        if ptn.rotated:
            ptn = texmex.rotate_left(ptn)
        result.append(ptn)
    return result


def rotate_horizontals_ifrequired(horizontals, ptns):
    for horizontal in horizontals:
        pagewidth = utila.select_page(ptns, horizontal.page).height
        for hori in horizontal.content:
            x0, y0, x1, y1 = hori.box
            width = math.fabs(x0 - x1)
            height = math.fabs(y0 - y1)
            if height > width:
                # rotate
                # x0=113.8, y0=89.29, x1=113.8, y1=505.98
                hori.box = rotate_bounding(hori.box, width=pagewidth)
    return horizontals


def rotate_bounding(bounding: tuple, width: float) -> iamraw.BoundingBox:
    x0, y0, x1, y1 = bounding
    box = (
        y0,
        width - x1,
        y1,
        width - x0,
    )
    result = iamraw.BoundingBox.from_list(box)
    return result
