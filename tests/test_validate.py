# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import functools

import hoverpower
import iamraw
import pytest
import serializeraw
import utilo
import utilotest

import headnote
import tests

ARCHIVE = utilo.join(headnote.ROOT, 'tests/expected', exist=True)


def monday(item):
    if item in {
            hoverpower.DISS143_PDF,
            hoverpower.DISS144_PDF,
            hoverpower.HC_DISS171,
            hoverpower.HC_DISS193,
    }:
        return utilotest.monday
    return None


@pytest.mark.parametrize(
    'source',
    utilotest.test_resources(tests.conftest.RESOURCES, marker=monday),
)
@utilotest.nightly
def test_validate(source, td, mp):
    Evaluate(
        source=source,
        workdir=td.tmpdir,
        mp=mp,
    ).evaluate()


class Evaluate(utilotest.BaseLiner):

    def __init__(self, source, workdir, mp):
        super().__init__(
            program=functools.partial(tests.run, mp=mp),
            step='',
            pages=':',
            source=hoverpower.link(source),
            workdir=workdir,
            archive=ARCHIVE,
            loader=self.load_footnotes,
            convert_source=False,
        )

    def load_footnotes(self, _):  # pylint:disable=W0613
        path = iamraw.path.headnote_result(self.workdir)
        loaded = serializeraw.load_headerfooter(path)
        return loaded

    def raw(self, value) -> str:
        headers = []
        for item in value:
            if rendered := rawline(item.page, item.header):
                headers.append(rendered)
            if rendered := rawline(item.page, item.footer):
                headers.append(rendered)
        # remove empty items
        headers = [item for item in headers if item]
        result = utilo.NEWLINE.join(headers)
        return result


def rawline(pdfpage, header) -> str:
    if not header:
        return ''
    if not any((header.title, header.undefined)):
        return ''
    result = str(pdfpage).zfill(4) + ' '
    if header.title:
        result += header.title.raw
    undefined = ' '.join(item.text for item in header.undefined)
    if undefined:
        result += undefined
    return result
