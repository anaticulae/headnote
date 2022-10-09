# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import collections
import typing

import iamraw
import serializeraw
import utila


def work(
    xcommon: str,
    xfixed: str,
    pages: tuple = None,
) -> str:
    common = serializeraw.load_headerfooter(
        xcommon,
        pages=pages,
    )
    fixed = serializeraw.load_headerfooter(
        xfixed,
        pages=pages,
    )
    results = [
        common,
        fixed,
    ]
    juged = judge_strategy(results)
    dumped = serializeraw.dump_headerfooter(juged)
    return dumped


def judge_strategy(
    results: typing.List[iamraw.PageContentFooterHeaders],
) -> iamraw.PageContentFooterHeaders:
    """Decide which results fits best.

    Zip result of different strategies. Sometimes there are multiple
    options, therefore we have to use the priorities below.

    Sources/Concept:

        - Common:           header
        - FixedFooter:      header and footer

    Args:
        results: lists of `groupme.footer.FooterHeaderDetectionStrategy`.result
    Returns:
        list of zipped result
    """
    assert results is not None, 'require list of strategy results'
    qualities = quality(results)
    result = []
    for pagenumber, (
            common,
            fixed,
    ) in utila.sync_pages(results):
        header = fixed.header if fixed else None
        footer = fixed.footer if fixed else None
        footer_best = 'fixed' if fixed else None
        if common and common.header:
            if not header:
                header = common.header
            elif qualities[0] == max(qualities):
                # compare quality of both extractions
                # TODO: MORE THAN ONE EXTRACTION CAN HAVE BEST
                # EXTRACTION QUALITY.
                header = common.header
        if common and common.footer:
            if not footer:
                footer = common.footer
            elif qualities[0] == max(qualities):
                # compare quality of both extractions
                # TODO: MORE THAN ONE EXTRACTION CAN HAVE BEST
                # EXTRACTION QUALITY.
                footer = common.footer
        if not header and not footer:
            continue
        # log footer best
        if footer_best:
            utila.verbose(f'footer: {pagenumber} {footer_best}')
        current = iamraw.PageContentFooterHeader(
            header=header,
            footer=footer,
            page=pagenumber,
        )
        result.append(current)
    validate(result)
    page_order = [item.page for item in result]
    assert utila.isascending(page_order), page_order
    return result


def quality(results: list) -> tuple:
    """Determine quality[0.0, 1.0] of every extraction strategy."""
    # count number of page
    pages = set()
    # count result for every strategy
    counter = collections.defaultdict(int)
    for pagenumber, data in utila.sync_pages(results):
        pages.add(pagenumber)
        for index, item in enumerate(data):
            if not item:
                continue
            counter[index] += 1
    result = tuple(counter[index] / len(pages) if pages else 0
                   for index, _ in enumerate(results))
    return result


def validate(items: list):
    """Validate list of pageable items.

    If some `page` attribute is duplicated, raise ValueError.

    Args:
        items(list): list of objects with <page,content>
    Raises:
        ValueError: if some page attribute is duplicated.
    """
    # TODO: REMOVE AFTER UPGRADING IAMRAW
    counter = collections.Counter()
    for item in items:
        counter[item.page] += 1
    msg = []
    for page, value in counter.most_common():
        if value <= 1:
            continue
        msg.append(f'duplicated page: {page} ({value})')
    if msg:
        raise ValueError(utila.NEWLINE.join(msg))
