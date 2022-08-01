# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================
"""Fixed Footer Extraction Strategy
================================

Examples:

- bachelor/page_111_images_toc.pdf
- docu/restructuredtext.pdf

Master of the art:

- docu/vimguide.pdf: This example contains a lot of tables, therefore we
  have a lot of horizontal lines which challenges the algorithm.
"""

import itertools
import typing

import configo
import iamraw
import texmex
import utila

import headnote.headnotes
import headnote.horizontals
import headnote.strategy

NO_CLUSTER = [texmex.START], [texmex.END] # yapf:disable

# max difference between left and right y-coordinate
COMMON_HORIZONTAL_CLASSIFIER_ERROR_MAX = configo.HV_FLOAT_PLUS(default=2.0)

# minimal horizontal line count in cluster to avoid low item cluster
CLUSTER_SIZE_MIN = configo.HV_INT_PLUS(default=10)

# maximal count of different header/footer areas
FOOTERHEADER_AREA_COUNT_MAX = configo.HV_INT_PLUS(default=5)

# maximal distance from page top in percent where header can be detected
HEADER_SIZE_MAX = configo.HV_PERCENT_PLUS(default=15, limit=100)

# maximal distance from page bottom in percent where footer can be detected
FOOTER_SIZE_MAX = configo.HV_PERCENT_PLUS(default=20, limit=100)

HORIZONTALS_MATCH_DIFF_MAX = configo.HV_INT_PLUS(default=10)


class FixedHeadnoteStrategy(headnote.strategy.HeadnoteDetectionStrategy):
    """The `FixedHeadnoteStategy` detects footer and header depending on
    horizontal line position. The strategy detects the most common
    border for header and footer.

    The header is located in [top, `HEADER_SIZE_MAX`]
    The footer is located in [bottom-`FOOTER_SIZE_MAX`, bottom].

    TODO: Run strategy with second common, third common header/footer again.
    """

    def result(self):
        if not self.pagetextnavigators:
            return []
        # TODO: HOW TO HANDLE DIFFERENT PAGE HEIGHTS
        # TODO: GROUP PAGE BY PAGESIZE FIRST AND THEN COMPUTE FOR EVERY
        # DIFFERENT PAGE SIZE
        first_page = self.pagetextnavigators[0].page
        pageheight = self.pageheight(first_page)
        # determine most common border for all pages
        tops, bottoms = extract_common_footer(
            horizontals=self.horizontals,
            pageheight=pageheight,
            max_group_count=FOOTERHEADER_AREA_COUNT_MAX,
        )
        footerheader = []
        for top, bottom in itertools.zip_longest(tops, bottoms):
            # look for every page if footer/header are present
            extracted = extract_page_footerheader(
                horizontals=self.horizontals,
                top=top,
                bottom=bottom,
                pagetextnavigators=self.pagetextnavigators,
            )
            footerheader.extend(extracted)
        footerheader = decide_multiple(footerheader)
        return footerheader

    def report(self) -> headnote.strategy.HeadnoteStrategyReport:
        pass


def extract_common_footer(
    horizontals: iamraw.PagesWithHorizontalList,
    pageheight: int,
    max_group_count: int = 1,
) -> typing.Tuple[int, int]:
    """Extract common footer and header based on horizontal lines.

    Args:
        horizontals: list of extract horizontals for every page
        pageheight: height of the first page in the document
        max_group_count: max count of different areas
    Returns:
        a tuple with the `top` and `bottom` border of header and footer.
        None - If no header or footer is detected.
    """
    bounding = []
    for page in horizontals:
        for horizontal in page.content:
            bounding.append(horizontal.box)
    # Hint: Use same line cluster instead of same area cluster. In
    # documents with alternating left right pages the horizonal lines
    # alternates also. Therefore we have only check the y-direction
    # instead of the whole line.
    clusters = utila.same_line_cluster(
        todo=bounding,
        max_diff=COMMON_HORIZONTAL_CLASSIFIER_ERROR_MAX,
    )
    if not clusters:
        return NO_CLUSTER
    top = extract_inarea(
        clusters,
        pageheight=pageheight,
        upper_bound=texmex.START,
        lower_bound=HEADER_SIZE_MAX,
        max_group_count=max_group_count,
    )
    bottom = extract_inarea(
        clusters,
        pageheight=pageheight,
        upper_bound=texmex.END - FOOTER_SIZE_MAX,
        lower_bound=texmex.END,
        max_group_count=max_group_count,
    )
    if top is None:
        # could not detect any header
        top = [texmex.START]
    if bottom is None:
        # could not detect any footer
        bottom = [pageheight]
    # the header is on the top(0.0) and the footer is on the bottom(1.0)
    assert max(top) < min(bottom), f'{top} < {bottom}'
    return top, bottom


def extract_page_footerheader(
    horizontals: iamraw.PagesWithHorizontalList,
    top: float,
    bottom: float,
    pagetextnavigators: texmex.PageTextNavigators,
) -> iamraw.PageContentFooterHeaders:
    """Extract footer and header which matches `top` and `bottom`.

    Args:
        horizontals: pages with horizontal lines
        top(pixel): position of header-border horizontal line
        bottom(pixel): position of footer-border horizontal line
        pagetextnavigators: list of page content
    Returns:
        list of `iamraw.PageContentFooterHeader` for every
        page with header and footer information.
    """
    result = []
    for page in horizontals:
        textnavigator = utila.select_page(pagetextnavigators, page.page)
        header = None
        if top is not None and headnote.horizontals.match(
                content=page.content,
                expected=top,
                diff_max=HORIZONTALS_MATCH_DIFF_MAX,
        ):
            header = create_header(top / textnavigator.height, textnavigator)
        footer = None
        if bottom is not None and headnote.horizontals.match(
                content=page.content,
                expected=bottom,
                diff_max=HORIZONTALS_MATCH_DIFF_MAX,
        ):
            footer = create_footer(
                bottom=utila.roundme(bottom / textnavigator.height),
                navigator=textnavigator,
            )
        if header is None and footer is None:
            # no matching horizontals
            continue
        footer_header = iamraw.PageContentFooterHeader(
            header=header,
            footer=footer,
            page=page.page,
        )
        result.append(footer_header)
    return result


# 10% percent cause of bad font-bounding-boxing
HEADER_PARSING_TOL = configo.HV_PERCENT_PLUS(default=10, limit=25)
# TODO: PRECENT_MINUS
FOOTER_PARSING_TOL = configo.HV_PERCENT_PLUS(default=0, limit=25)


def create_header(top: float, navigator):
    top = utila.roundme(top * (1 + HEADER_PARSING_TOL))
    headercontent = navigator.between(
        texmex.START,
        top,
    )
    parsed = headnote.headnotes.parse(headercontent)
    result = iamraw.FixedHeaderInformation(begin=texmex.START, end=top)
    for item in parsed:
        if isinstance(item, iamraw.HeaderTitle):
            result.title = item
        if isinstance(item, iamraw.RawText):
            result.undefined.append(item)
        if isinstance(item, iamraw.PageInformation):
            result.page = item
    return result


def create_footer(bottom: float, navigator):
    bottom = utila.roundme(bottom * (1 + FOOTER_PARSING_TOL))
    headercontent = navigator.between(
        bottom,
        texmex.END,
    )
    parsed = headnote.headnotes.parse(headercontent)
    result = iamraw.FixedFooterInformation(begin=bottom, end=texmex.END)
    for item in parsed:
        if isinstance(item, iamraw.HeaderTitle):
            result.title = item
        if isinstance(item, iamraw.RawText):
            result.undefined.append(item)
        if isinstance(item, iamraw.PageInformation):
            result.page = item
    return result


def extract_inarea(
    clusters: typing.List,
    pageheight: int,
    upper_bound: float = texmex.START,
    lower_bound: float = texmex.END,
    max_group_count: int = 1,
    min_group_size: int = CLUSTER_SIZE_MIN,
) -> float:
    """Determine all elements in the potential footer/header area"""
    ymin = pageheight * upper_bound
    ymax = pageheight * lower_bound

    result = headnote.horizontals.biggest_hlinecluster_in_area(
        clusters,
        ymin=ymin,
        ymax=ymax,
        max_group_count=max_group_count,
        min_group_size=min_group_size,
    )
    if not result:
        return None
    return result


def decide_multiple(items):
    """Decide for a single page which extracted header/footer is correct.

    In some cases there are more than one possible horizontal headlines
    or footlines. This can happen when having different FixedHeader or
    MovingFooter. This strategy decides on the count of extracted
    header. The main propose is to have a single header/footer per page.
    """
    selected = {}
    for item in items:
        try:
            cur = selected[item.page]
            itemcount = len([it for it in [item.header, item.footer] if it])
            currentcount = len([it for it in [cur.header, cur.footer] if it])
            if itemcount > currentcount:
                # replace current result with better result
                selected[item.page] = item
        except KeyError:
            selected[item.page] = item
    result = list(selected.values())
    result = sorted(result, key=lambda x: x.page)
    return result
