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
        ptns: texmex.PTNs,
    ):
        assert isinstance(horizontals, typing.List), str(horizontals)
        self.horizontals = horizontals
        self.ptns = ptns
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
        selected = utila.select_page(self.ptns, page)
        if selected is None:
            return None
        pageheight = selected.height
        return pageheight
