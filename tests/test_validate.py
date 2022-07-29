# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import functools

import power
import pytest
import serializeraw
import utila
import utilatest

import headnote
import tests

ARCHIVE = utila.join(headnote.ROOT, 'tests/expected', exist=True)

step = lambda x: pytest.param(x, ':', utila.file_name(x), id=utila.file_name(x))


@pytest.mark.parametrize('source, pages, expected', [
    pytest.param(power.DISS148_PDF, '40:120', 'diss148', id='diss148'),
    pytest.param(power.HC_DISS148, ':', 'hcdiss148', id='hcdiss148'),
    step(power.BOOK173_PDF),
    step(power.HC_DISS128),
    step(power.HC_DISS166),
    step(power.HC_DISS171),
    step(power.HC_DISS193),
    step(power.TECH019_PDF),
])
@utilatest.nightly
def test_validate(source, pages, expected, td, mp):
    Evaluate(
        source=source,
        pages=pages,
        expected=expected,
        workdir=td.tmpdir,
        mp=mp,
    ).evaluate()


class Evaluate(utilatest.BaseLiner):

    def __init__(self, source, pages, expected, workdir, mp):
        super().__init__(
            program=functools.partial(
                tests.run,
                mp=mp,
            ),
            step='',
            pages=pages,
            source=power.link(source),
            workdir=workdir,
            archive=ARCHIVE,
            loader=self.load_footnotes,
            convert_source=False,
            index=expected,
        )

    def load_footnotes(self, _):  # pylint:disable=W0613
        loaded = serializeraw.load_headerfooter(
            utila.join(
                self.workdir,
                'headnote__result_result.yaml',
            ))
        return loaded

    def raw(self, value) -> str:
        headers = [rawline(item.page, item.header) for item in value]
        # remove empty items
        headers = [item for item in headers if item]
        result = utila.NEWLINE.join(headers)
        return result


def rawline(pdfpage, header) -> str:
    if not header:
        return None
    if not any((header.title, header.undefined)):
        return None
    result = str(pdfpage).zfill(4) + ' '
    if header.title:
        result += header.title.raw
    undefined = ' '.join(item.text for item in header.undefined)
    if undefined:
        result += undefined
    return result
