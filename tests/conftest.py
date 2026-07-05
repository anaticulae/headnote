# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import gennex
import hoverpower
import utilotest
from utilotest import mp  # pylint:disable=W0611
from utilotest import td  # pylint:disable=W0611

import headnote

pytest_plugins = ['pytester', 'xdist']  # pylint: disable=invalid-name

PACKAGE = headnote.PROCESS

RESOURCES = [
    (hoverpower.BACHELOR090_PDF, '0:25'),
    (hoverpower.BOOK173_PDF, '0:100'),
    (hoverpower.DISS264_PDF, '0:50'),
    (hoverpower.DISS406_PDF, '0:75,100:150'),
    (hoverpower.MASTER116_PDF, '50:117'),
    gennex.todo(
        hoverpower.DISS172_PDF,
        rawmaker=gennex.CONFIG,
        figureo=True,
        tablero=True,
        cleanup=True,
    ),
    hoverpower.BACHELOR026_PDF,
    hoverpower.BACHELOR037_PDF,
    hoverpower.BACHELOR063_PDF,
    hoverpower.BACHELOR111_PDF,
    hoverpower.BACHELOR128_PDF,
    hoverpower.DISS144_PDF,
    hoverpower.DISS148_PDF,
    hoverpower.DOCU027_PDF,
    hoverpower.HC_DISS128,
    hoverpower.HC_DISS148,
    hoverpower.HC_DISS166,
    hoverpower.HC_DISS171,
    hoverpower.HC_DISS193,
    hoverpower.MASTER072_PDF,
    hoverpower.MASTER075_PDF,
    hoverpower.MASTER110_PDF,
    hoverpower.MASTER155_PDF,
    hoverpower.MASTER193_PDF,
    hoverpower.TECH019_PDF,
    hoverpower.TECH024_PDF,
]

WORKER = utilotest.worker_count(6, onci=len(RESOURCES))


def pytest_sessionstart(session):  # pylint:disable=W0613
    hoverpower.run()


RAWMAKER = '--text --line --horizontals ' + gennex.CONFIG


def extract(resources):
    gennex.extract(
        resources,
        cleanup=True,
        oneline=None,
        pagenumber=True,
        footnote=True,
        rawmaker=RAWMAKER,
        worker=WORKER,
    )
