# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import itertools

import hoverpower
import iamraw
import serializeraw
import utilo
import utilotest

import headnote.strategy
import headnote.strategy.fixed


def test_docu027_extract_common_header():
    _, __, top, bottom, ___ = _docu027()
    assert top  # document has header
    assert bottom  # document has footer
    assert top < bottom


def test_docu027_extract_page_header_footer():
    horizontals, _, top, bottom, ptns = _docu027()
    top, bottom = top[0], bottom[0]
    extracted = headnote.strategy.fixed.extract_page_header_footer(
        horizontals,
        top,
        bottom,
        ptns,
    )
    allfooter = [
        item.footer is not None for item in extracted if item.page >= 2
    ]
    assert all(allfooter), utilo.log_raw(allfooter)


@utilotest.longrun
def test_bachelor111page_extract_common_header():
    _, __, top, bottom, ___ = _bachelor111()
    assert top  # document has header
    assert bottom  # document has footer
    assert top < bottom


@utilotest.longrun
def test_bachelor111page_extract_page_header_footer():
    """Use more than one group to detect all headers.

    There are ordered from biggest to smallest.
    """
    footerheader = _bachelor111_footerheader()
    msg = 'more footer than pages, remove duplication'
    bachelor111pagecount = 111
    assert len(footerheader) < bachelor111pagecount, msg

    header = [item.header for item in footerheader if item.header]
    assert len(header) == 94, utilo.log_raw(header)

    # assert that strategy detect no invalid fixed footer
    footer = [item.footer for item in footerheader if item.footer]
    assert not footer, utilo.log_raw(footer)


@utilotest.longrun
def test_bachelor111page_extract_page_header():
    footerheader = _bachelor111_footerheader()
    pages = [item.page for item in footerheader]
    assert all(pages)
    title = [
        item.header.title
        for item in footerheader
        if item.header and item.header.title
    ]
    assert len(title) >= 68, 'not enough title'


@utilotest.longrun
def test_footer_dump_and_load_bachelor111():
    footerheader = _bachelor111_footerheader()
    dumped = serializeraw.dump_headerfooter(footerheader)
    loaded = serializeraw.load_headerfooter(dumped)
    assert loaded == footerheader


def _docu027():
    utilotest.fixture_requires(hoverpower.DOCU027_PDF)
    source = hoverpower.link(hoverpower.DOCU027_PDF)
    horizontals = iamraw.path.horizontals(source)
    horizontals = serializeraw.load_horizontals(horizontals)
    navigators = serializeraw.ptn_frompath(source)
    pageheight = navigators[0].height
    top, bottom = headnote.strategy.fixed.extract_common_header(
        horizontals=horizontals,
        pageheight=pageheight,
    )
    return horizontals, pageheight, top, bottom, navigators


def _bachelor111():
    utilotest.fixture_requires(hoverpower.BACHELOR111_PDF)
    source = hoverpower.link(hoverpower.BACHELOR111_PDF)
    horizontals = iamraw.path.horizontals(source)
    horizontals = serializeraw.load_horizontals(horizontals)
    navigators = serializeraw.ptn_frompath(source)
    pageheight = navigators[0].height
    top, bottom = headnote.strategy.fixed.extract_common_header(
        horizontals=horizontals,
        pageheight=pageheight,
    )
    return horizontals, pageheight, top, bottom, navigators


def _bachelor111_footerheader():
    horizontals, _, top, bottom, ptns = _bachelor111()
    footerheader = []
    for top, bottom in itertools.zip_longest(top, bottom):
        extracted = headnote.strategy.fixed.extract_page_header_footer(
            horizontals,
            top,
            bottom,
            ptns,
        )
        footerheader.extend(extracted)
    footerheader = headnote.strategy.fixed.decide_multiple(footerheader)
    result = iamraw.PageContentFooterHeaders(content=footerheader)
    result.__strategy__ = iamraw.PageContentFooterHeaders.__name__
    return result
