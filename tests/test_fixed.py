# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import itertools

import iamraw
import iamraw.path
import power
import serializeraw
import utila
import utilatest

import headnote.strategy
import headnote.strategy.fixed


def _docu027():
    source = power.link(power.DOCU027_PDF)
    horizontals = iamraw.path.horizontals(source)
    horizontals = serializeraw.load_horizontals(horizontals)
    navigators = serializeraw.ptn_frompath(source)
    pageheight = navigators[0].height
    top, bottom = headnote.strategy.fixed.extract_common_footer(
        horizontals=horizontals,
        pageheight=pageheight,
    )
    return horizontals, pageheight, top, bottom, navigators


def test_docu027_extract_common_footer():
    _, __, top, bottom, ___ = _docu027()
    assert top  # document has header
    assert bottom  # document has footer
    assert top < bottom


def test_docu027_extract_page_footerheader():
    horizontals, _, top, bottom, ptns = _docu027()
    top, bottom = top[0], bottom[0]
    extracted = headnote.strategy.fixed.extract_page_footerheader(
        horizontals,
        top,
        bottom,
        ptns,
    )
    allfooter = [
        item.footer is not None for item in extracted if item.page >= 2
    ]
    assert all(allfooter), utila.log_raw(allfooter)


def _bachelor111():
    source = power.link(power.BACHELOR111_PDF)
    horizontals = iamraw.path.horizontals(source)
    horizontals = serializeraw.load_horizontals(horizontals)
    navigators = serializeraw.ptn_frompath(source)
    pageheight = navigators[0].height
    top, bottom = headnote.strategy.fixed.extract_common_footer(
        horizontals=horizontals,
        pageheight=pageheight,
    )
    return horizontals, pageheight, top, bottom, navigators


def _bachelor111_footerheader():
    horizontals, _, top, bottom, ptns = _bachelor111()
    footerheader = []
    for top, bottom in itertools.zip_longest(top, bottom):
        extracted = headnote.strategy.fixed.extract_page_footerheader(
            horizontals,
            top,
            bottom,
            ptns,
        )
        footerheader.extend(extracted)
    footerheader = headnote.strategy.remove_duplication(footerheader)
    return footerheader


@utilatest.longrun
def test_bachelor111page_extract_common_footer():
    _, __, top, bottom, ___ = _bachelor111()
    assert top  # document has header
    assert bottom  # document has footer
    assert top < bottom


@utilatest.longrun
def test_bachelor111page_extract_page_footerheader():
    """Use more than one group to detect all headers.

    There are ordered from biggest to smallest.
    """
    footerheader = _bachelor111_footerheader()
    msg = 'more footer than pages, remove duplication'
    bachelor111pagecount = 111
    assert len(footerheader) < bachelor111pagecount, msg

    header = [item.header for item in footerheader if item.header]
    assert len(header) == 94, utila.log_raw(header)

    # assert that strategy detect no invalid fixed footer
    footer = [item.footer for item in footerheader if item.footer]
    assert not footer, utila.log_raw(footer)


@utilatest.longrun
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


@utilatest.longrun
def test_footer_dump_and_load_bachelor111():
    footerheader = _bachelor111_footerheader()

    dumped = serializeraw.dump_headerfooter(footerheader)
    loaded = serializeraw.load_headerfooter(dumped)

    assert loaded == footerheader
