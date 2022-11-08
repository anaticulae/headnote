# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import iamraw
import power
import serializeraw
import utila
import utilatest

import tests


def run_headnotes(td, mp, pages: str) -> iamraw.PageContentFooterHeaders:
    utilatest.fixture_requires(power.BACHELOR063_PDF)
    source = power.link(power.BACHELOR063_PDF)
    cmd = f'-i {source} -o {td.tmpdir} --pages={pages}'
    tests.run(cmd, mp=mp)
    path = iamraw.path.headnote_result(td.tmpdir)
    loaded = serializeraw.load_headerfooter(path)
    return loaded


def test_bachelor063_page1(td, mp):
    result = run_headnotes(td, mp, pages='0:10')
    selected = utila.select_page(result, page=1)
    # header
    header_y0 = selected.header.begin
    header_y1 = selected.header.end
    assert header_y1 >= 0.06, header_y1
    assert 0.0 <= header_y0 <= header_y1 <= 0.08
    # footer
    footer_y0 = selected.footer.begin
    footer_y1 = selected.footer.end
    assert 0.93 <= footer_y0 <= footer_y1 <= 1.0


def test_bachelor063_all(td, mp):
    result = run_headnotes(td, mp, pages='0:30')
    selected = utila.select_page(result, page=1)
    # header
    header_y0 = selected.header.begin
    header_y1 = selected.header.end
    assert header_y1 >= 0.06, header_y1
    assert 0.0 <= header_y0 <= header_y1 <= 0.08
    # footer
    footer_y0 = selected.footer.begin
    footer_y1 = selected.footer.end
    assert 0.93 <= footer_y0 <= footer_y1 <= 1.0
