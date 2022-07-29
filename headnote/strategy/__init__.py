# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================
"""The `headnote` module extract the header and footer area out of
pdf-pages.

There are one different strategies:

- CommonTextStrategy
- Fixed
"""

import abc
import collections
import dataclasses
import typing

import iamraw
import texmex
import utila


@dataclasses.dataclass  # pylint:disable=R0903
class HeadnoteStrategyReport:
    pass


class HeadnoteDetectionStrategy(abc.ABC):

    def __init__(
        self,
        horizontals: iamraw.PagesWithHorizontalList,
        pagetextnavigators: texmex.PageTextNavigators,
    ):
        assert isinstance(horizontals, typing.List), str(horizontals)
        self.horizontals = horizontals
        self.pagetextnavigators = pagetextnavigators

        self.result__ = {}

        self.post_init()

    def post_init(self):
        """Run after __init__"""

    def result(self) -> iamraw.PageContentFooterHeaders:
        raise NotImplementedError()

    def report(self) -> HeadnoteStrategyReport:
        """Return meta data to determined `result`. The main propose of
        this report is to have a better view why the algorithm produces
        this given result."""
        raise NotImplementedError()

    def pageheight(self, page) -> int:
        """Determine `pageheight` of current `page` in `pixel`.

        Args:
            page(int): page of pdf document
        Returns:
            pageheight if pageheight exists
            None if pageheight not exists
        """
        selected = utila.select_page(self.pagetextnavigators, page)
        if selected is None:
            return None
        pageheight = selected.height
        return pageheight


def remove_duplication(items: list) -> list:
    """In some cases more than one potential header or footer are
    detected for one page. This method judges the problem and select the
    `best` result.

    Args:
        items: list of `PageContentFooterHeader`
    Returns:
        sorted list without page duplications
    """
    source = collections.defaultdict(list)
    for item in items:
        source[item.page].append(item)
    result = [multijudgement(item) for item in source.values()]
    result = sorted(result, key=lambda x: x.page)
    return result


def multijudgement(judges):
    # TODO: Strategy how to judge multiple matches
    # BIGGER ONE, ITEM OF BIGGER CLUSTER?

    def count_item(item):
        return int(item.footer is not None) + int(item.header is not None)

    current = judges[0]
    count = count_item(current)
    for item in judges[1:]:
        cur_count = count_item(item)
        if cur_count < count:
            continue
        current = item
        count = cur_count
    return current
