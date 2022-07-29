# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import texmex


def rotate_ifrequired(navigators):
    result = []
    for ptn in navigators:
        if ptn.rotated:
            ptn = texmex.rotate_left(ptn)
        result.append(ptn)
    return result
