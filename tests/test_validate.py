# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import functools

import iamraw
import power
import pytest
import serializeraw
import utila
import utilatest

import headnote
import tests

ARCHIVE = utila.join(headnote.ROOT, 'tests/expected', exist=True)


def monday(item):
    if item in {
            power.DISS143_PDF,
            power.DISS144_PDF,
            power.HC_DISS171,
            power.HC_DISS193,
    }:
        return utilatest.monday
    return None


@pytest.mark.parametrize(
    'source',
    utilatest.test_resources(tests.conftest.RESOURCES, marker=monday),
)
@utilatest.nightly
def test_validate(source, td, mp):
    Evaluate(
        source=source,
        workdir=td.tmpdir,
        mp=mp,
    ).evaluate()


class Evaluate(utilatest.BaseLiner):

    def __init__(self, source, workdir, mp):
        super().__init__(
            program=functools.partial(tests.run, mp=mp),
            step='',
            pages=':',
            source=power.link(source),
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
        result = utila.NEWLINE.join(headers)
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
