# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import hoverpower
import iamraw
import pytest
import serializeraw
import utilotest

import tests


def extract_header(source, td, mp, pages=':'):
    utilotest.fixture_requires(source)
    cmd = f'-i {hoverpower.link(source)} --pages={pages}'
    tests.run(cmd, mp=mp)
    headerpath = iamraw.path.headnote_result(td.tmpdir)
    loaded = serializeraw.load_headerfooter(headerpath)
    header = [item.header for item in loaded if item.header]
    return header


def test_bachelor90(td, mp):
    header = extract_header(hoverpower.BACHELOR090_PDF, td, mp, '11:24')
    assert len(header) == 11


@utilotest.longrun
def test_bachelor37_starting_index(td, mp):
    """Ensure that parts of pages `4:20` for example are indexed correctly."""
    header = extract_header(hoverpower.BACHELOR037_PDF, td, mp, '4:20')
    assert header[0].page.value == 4


@pytest.mark.xfail(reason='detector is too optimistic')
@utilotest.longrun
def test_bachelor37_all(td, mp):
    header = extract_header(hoverpower.BACHELOR037_PDF, td, mp)
    noheader = [0, 5, 33]
    expected = [item for item in range(0, 37) if item not in noheader]
    current = [item.page.value for item in header]
    assert current == expected


@utilotest.longrun
def test_diss264_page0_40(td, mp):
    header = extract_header(
        hoverpower.DISS264_PDF,
        td,
        mp,
        pages='0:40',
    )
    assert len(header) in {36, 37}


@utilotest.longrun
def test_diss264_all(td, mp):
    """Ensure to parse header of alternating pages correctly."""
    loaded = extract_header(hoverpower.DISS264_PDF, td, mp, '0:150')
    assert len(loaded) in {46, 47}  # may change in the future


@utilotest.longrun
def test_under_line_master75(td, mp):
    """Ensure to parse header of alternating pages correctly."""
    loaded = extract_header(hoverpower.MASTER075_PDF, td, mp, '0:50')
    assert len(loaded) == 48, len(loaded)
    # TODO: MAY ENABLE LATER
    # first = loaded[0].header.undefined
    # use common extractor
    # assert len(first) == 2, str(first)


@utilotest.longrun
def test_master110(td, mp):
    loaded = extract_header(hoverpower.MASTER110_PDF, td, mp, '0:50')
    assert len(loaded) in {13, 25}  # may change in the future


@utilotest.nightly
def test_master155(td, mp):
    loaded = extract_header(hoverpower.MASTER155_PDF, td, mp)
    assert len(loaded) == 153  # do not change


def test_tech24(td, mp):
    loaded = extract_header(
        hoverpower.TECH024_PDF,
        td,
        mp,
        pages='0:10',
    )
    assert len(loaded) == 9  # do not change


@utilotest.nightly
def test_bachelor128(td, mp):
    loaded = extract_header(
        hoverpower.BACHELOR128_PDF,
        td,
        mp,
    )
    empty = [item for item in loaded if not item.title and not item.undefined]
    # three may reduces later if we get better algorithms, but for now
    # tuning this value will lead to more false positive.
    # HINT: common strategy skips pages which does not detect anything,
    # therefore it is 0 instead of 3.
    assert not empty
    # assert len(empty) == 3  # VALIDATED


@utilotest.longrun
def test_diss172page110p130(td, mp):
    loaded = extract_header(
        hoverpower.DISS172_PDF,
        td,
        mp,
        pages='110:130',
    )
    assert len(loaded) == 16  # MAY CHANGE LATER


@utilotest.nightly
def test_diss172(td, mp):
    loaded = extract_header(
        hoverpower.DISS172_PDF,
        td,
        mp,
    )
    assert len(loaded) in {147, 148, 152}  # NOT VALIDATED


@utilotest.nightly
def test_diss144(td, mp):
    loaded = extract_header(
        hoverpower.DISS144_PDF,
        td,
        mp,
    )
    assert len(loaded) in {140, 142}  # NOT VALIDATED


@utilotest.nightly
def test_diss406(td, mp):
    loaded = extract_header(
        hoverpower.DISS406_PDF,
        td,
        mp,
    )
    # this document does not contain any header
    assert not loaded
