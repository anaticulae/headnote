# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================
"""common text strategy
====================

The ``common text strategy`` extracts header or footer based on common
text and images. There is no horizontal line required.

.. note ::
    TODO: SUPPORT COMMON IMAGES
"""

import collections
import math

import configo
import elements
import iamraw
import texmex
import utila

import headnote.headnotes
import headnote.strategy

COMMON_HEADER_ERROR_MAX = configo.HV_FLOAT_PLUS(default=10.0)
# minimal items in a cluster to be detected and accepted as feature.
OCCURRENCE_MIN = configo.HolyTable(
    items=(
        (0, 5),
        (10, 5),
        (15, 8),
        (30, 12),
        (50, 14),
        (100, 25),
    ),
    right_outranges_none=False,
)

AREA_TOP = configo.HV_PERCENT_PLUS(default=15)

AREA_BOTTOM = configo.HV_PERCENT_PLUS(default=75)


class CommonTextStrategy(headnote.strategy.HeadnoteDetectionStrategy):

    def result(self):
        headers = self.result_header()
        footers = self.result_footer()
        merged = sorted(
            headers + footers,
            key=lambda x: x.page,
        )
        if not merged:
            return []
        result = [merged[0]]
        for item in merged[1:]:
            before = result[-1]
            if item.page == before.page:
                if item.footer:
                    before.footer = item.footer
                if item.header:
                    before.header = item.header
            else:
                result.append(item)
        return result

    def result_header(self):
        headers, clusters = self.determine_header()
        if not headers:
            return []
        headers = self.second_try(
            headers,
            clusters,
            convert=create_fixedheader,
        )
        result = [
            iamraw.PageContentFooterHeader(
                header=header,
                footer=None,
                page=page,
            ) for (page, header) in headers
        ]
        result = self.verify_result(result)
        return result

    def result_footer(self):
        footers, clusters = self.determine_footer()
        if not footers:
            return []
        footers = self.second_try(
            footers,
            clusters,
            convert=create_fixedfooter,
        )
        result = [
            iamraw.PageContentFooterHeader(
                header=None,
                footer=footer,
                page=page,
            ) for (page, footer) in footers
        ]
        result = self.verify_result(result)
        return result

    def determine_header(self):
        extracted = cluster_pages(
            self.ptns,
            select=potential_header_data,
            convert=create_fixedheader,
        )
        tryagain = cluster_pages(
            self.ptns,
            select=potential_header_data,
            convert=create_fixedheader,
            tryagain=True,
        )
        clusters = None
        if extracted:
            headers = best(extracted[0], tryagain[0])
            if headers == extracted[0]:
                clusters = extracted[1]
            else:
                clusters = tryagain[1]
        else:
            headers = tryagain[0] if tryagain else []
            if tryagain:
                clusters = tryagain[1]
            else:
                clusters = None
        return headers, clusters

    def determine_footer(self):
        extracted = cluster_pages(
            self.ptns,
            select=potential_footer_data,
            convert=create_fixedfooter,
        )
        tryagain = cluster_pages(
            self.ptns,
            select=potential_footer_data,
            convert=create_fixedfooter,
            tryagain=True,
        )
        clusters = None
        if extracted:
            headers = best(extracted[0], tryagain[0])
            if headers == extracted[0]:
                clusters = extracted[1]
            else:
                clusters = tryagain[1]
        else:
            headers = tryagain[0] if tryagain else []
            if tryagain:
                clusters = tryagain[1]
            else:
                clusters = None
        return headers, clusters

    def second_try(self, headers, clusters, convert):
        # do not revisit pages with already detected header
        skip = {item[0] for item in headers}
        ptns_left = [page for page in self.ptns if page.page not in skip]
        result = more_magic(ptns_left, clusters, convert=convert)
        return result

    def verify_result(self, headers):
        pagecount = len(self.ptns)
        headercount = len([it for it in headers if it.header or it.footer])
        required = HEADER_OCCURRENCE_MIN(pagecount)
        if headercount < required:
            utila.debug(f'disable header common too few header: {headercount} '
                        f'pages: {pagecount} required: {required}')
            return []
        return headers


HEADER_OCCURRENCE_MIN = configo.HolyTable(
    items=(
        (0, 5),
        (10, 4),
        (15, 7),
        (30, 12),
        (50, 14),
        (100, 25),
    ),
    right_outranges_none=False,
)


def best(*items):
    result = items[0]
    value = count_empty(result)
    for current in items[1:]:
        wholes = count_empty(current)
        if wholes is None:
            # nothing to count
            continue
        if wholes >= value:
            # worser than current result
            continue
        # better
        result = current
        value = wholes
    return result


# count holes in [20%,80%]
COUNT_EMPTY_DOCUMENT_PAGE_START = configo.HV_PERCENT_PLUS(default=20)

COUNT_EMPTY_DOCUMENT_PAGE_END = configo.HV_PERCENT_PLUS(default=80)


def count_empty(collected) -> int:
    # count holes in [20%,80%]
    if not collected:
        return None
    # skip start and end of document cause we expect a lot of
    # empty/skipped header.
    start = int(len(collected) * COUNT_EMPTY_DOCUMENT_PAGE_START)
    end = int(len(collected) * COUNT_EMPTY_DOCUMENT_PAGE_END)
    empty = [
        item for item in collected[start:end]
        if not item[1].title and not item[1].undefined
    ]
    return len(empty)


# plus 1 percent off to ensure that content and header is separated correctly.
HEADER_TOL = configo.HV_FLOAT_PLUS(default=0.01)


def cluster_pages(
    ptns: texmex.PTNs,
    select: callable,
    convert: callable,
    tryagain: bool = False,
):
    occurrence_min = HEADER_TEXT_OCCURENCE_MIN
    if tryagain:
        # run algorithmn with lower bound to gather more data but may be
        # more instable.
        occurrence_min = HEADER_TEXT_OCCURENCE_TRYAGAIN_MIN
    # prepare data
    with_box = utila.flatten(
        prepare_clustering(
            ptns,
            select=select,
            occurrence_min=occurrence_min,
        ))
    page_count = len(ptns)
    cluster_length_min = OCCURRENCE_MIN(page_count)
    # TODO: REMOVE LATER, SWITCH TABLE BASED ENTROPY OF POTENTIAL HEADER AREA?
    cluster_length_min = 5
    clusters = utila.three_side_equal_cluster(  # pylint:disable=E1123
        todo=with_box,
        max_diff=COMMON_HEADER_ERROR_MAX,
        min_elements=cluster_length_min,
    )
    if not clusters:
        return None
    result = convert_cluster(
        clusters,
        convert=convert,
    )
    return result, clusters


def convert_cluster(
    clusters,
    convert: callable,
) -> list:
    grouped = {}
    for cluster in clusters:
        for bounding, text, pageheight, pagenumber in cluster:
            end = bounding.y1 / pageheight
            end = utila.roundme(HEADER_TOL + end)
            current = grouped.get(pagenumber, None)
            current = convert(current, text.text, pagenumber, end)
            grouped[pagenumber] = current
    result = list(grouped.items())
    # sort FixedHeaderInformation by page
    result.sort(key=lambda x: x[0])
    return result


def create_fixedheader(
    current,
    text: str,
    pagenumber,
    end,
) -> iamraw.FixedHeaderInformation:
    # remove newline at end TODO: REMOVE LATER
    text = text.strip()
    if current is None:
        current = iamraw.FixedHeaderInformation(
            begin=texmex.START,
            end=end,
            page=iamraw.PageInformation(value=pagenumber, raw=None),
        )
    title = headnote.headnotes.parse_title(text)
    if title:
        current.title = title
        return current
    parsed = headnote.headnotes.parse_pagenumber(text)
    if parsed:
        current.page = parsed
        return current
    current.undefined.append(iamraw.RawText(text=text))
    return current


def create_fixedfooter(
    current,
    text: str,
    pagenumber,
    begin,
) -> iamraw.FixedHeaderInformation:
    # remove newline at end TODO: REMOVE LATER
    text = text.strip()
    if current is None:
        current = iamraw.FixedFooterInformation(
            begin=begin,
            end=texmex.END,
            page=iamraw.PageInformation(value=pagenumber, raw=None),
        )
    title = headnote.headnotes.parse_title(text)
    if title:
        current.title = title
        return current
    parsed = headnote.headnotes.parse_pagenumber(text)
    if parsed:
        current.page = parsed
        return current
    current.undefined.append(iamraw.RawText(text=text))
    return current


HEADER_TEXT_OCCURENCE_MIN = configo.HV_INT_PLUS(default=5)

HEADER_TEXT_OCCURENCE_TRYAGAIN_MIN = configo.HV_INT_PLUS(default=3)


def prepare_clustering(
    ptns,
    select: callable,
    occurrence_min: int = HEADER_TEXT_OCCURENCE_MIN,
):
    collected = select(ptns)
    valid = header_content(collected, occurrence_min=occurrence_min)
    result = []
    for page in collected:
        content = [item for item in page if valid_line(item[1].text, valid)]
        result.append(content)
    return result


def valid_line(text: str, valid: set) -> bool:
    """Remove small text token trash.

    Skip very short elements:
    >>> assert not valid_line('-', valid={})
    """
    text = text.strip()
    if elements.ispagenumber(text):
        return True
    if len(text) <= 3:
        return False
    if text in valid:
        return True
    return False


def potential_header_data(ptns):
    collected = []
    for page in ptns:
        content = [(
            item.bounding,
            item,
            page.height,
            page.page,
        ) for item in page.before(AREA_TOP) if not noheader_content(item)]
        collected.append(content)
    return collected


def potential_footer_data(ptns):
    collected = []
    for page in ptns:
        content = [(
            item.bounding,
            item,
            page.height,
            page.page,
        ) for item in page.after(AREA_BOTTOM) if not noheader_content(item)]
        collected.append(content)
    return collected


HEADER_TEXT_SIZE_MAX = configo.HV_FLOAT_PLUS(default=13.9)


def noheader_content(item):
    if item.bounding_mean > HEADER_TEXT_SIZE_MAX:
        return True
    text = item.text.strip()
    if text.count('.') > 5:
        return True
    if text[0] in '•':
        return True
    return False


def header_content(pagecontents, occurrence_min: int) -> set:
    """Some documents does not have any header, but equal sized first line(s).

    We have to ignore these first content lines.
    """
    collected = collections.defaultdict(int)
    for pagecontent in pagecontents:
        for item in pagecontent:
            text = item[1].text.strip()
            collected[text] += 1
    # sum textual equal as equal items
    # 6.3 evaluation 106
    # 6.3 evaluation 107
    # 6.3 evaluation 108
    # HINT: if layout is better parsed page numbers are may not included
    maxdiff = 0.8  # TODO: HOLY VALUE
    counted = {
        key: sum([
            val for current, val in collected.items()
            if utila.similar(expected=key, current=current, maxdiff=maxdiff)
        ]) for key in collected.keys()
    }
    valid = {key for key in collected.keys() if counted[key] >= occurrence_min}
    return valid


def more_magic(ptns, clusters, convert: callable):
    """Revisit pages without detected header and try to match header
    items with already detected areas."""
    valid = utila.flatten([list(cluster) for cluster in clusters])
    data = potential_header_data(ptns)
    result = []
    for page in data:
        for item in page:
            if not any((matches(val, item) for val in valid)):
                continue
            result.append(item)
    result = convert_cluster(
        [result] + [valid],
        convert=convert,
    )
    return result


def matches(base, current) -> float:  # pylint:disable=R0911
    x0, y0, x1, y1 = base[0]
    xx0, yy0, xx1, yy1 = current[0]
    if utila.rectangle_inside(base[0], current[0]):
        return True
    if utila.norm(x0, y0, xx0, yy0) > 50.0:
        return False
    if utila.norm(x1, y1, xx1, yy1) > 50.0:
        return False
    if math.fabs(y1 - yy1) > 20.0:
        return False
    if math.fabs(y0 - yy0) > 20.0:
        return False
    # 30 percent
    fontdiff = not utila.pnear(
        reference=(y1 - y0),
        current=(yy1 - yy0),
        rel_tol=0.3,
    )
    if fontdiff:
        return False
    return True
