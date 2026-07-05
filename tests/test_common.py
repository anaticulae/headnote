# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import hoverpower
import iamraw
import serializeraw
import utilotest

import tests


@utilotest.requires(hoverpower.BACHELOR037_PDF)
def test_footer_regression_common_strategy(td, mp):
    """There was a bug in handling selective --pages=1 correctly.

    In the old implementation the page height of page zero was used for
    the whole document. Therefore selecting page one produces an None
    access error.
    """
    root = td.tmpdir
    source = hoverpower.link(hoverpower.BACHELOR037_PDF)
    page = 1
    cmd = f'-i {source} -o {root} --pages=0:10'
    tests.run(cmd, mp=mp)
    path = iamraw.path.headnote_common(root)
    headerfooter = serializeraw.load_headerfooter(path)
    assert len(headerfooter) == 8
    # Hint: this result is not produced by common strategy
    headerfooter = headerfooter[0]
    assert headerfooter.header
    assert headerfooter.page == page
