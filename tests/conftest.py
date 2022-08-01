# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import genex
import power
from utilatest import mp  # pylint:disable=W0611
from utilatest import td  # pylint:disable=W0611

import headnote

pytest_plugins = ['pytester', 'xdist']  # pylint: disable=invalid-name

PACKAGE = headnote.PROCESS

RESOURCES = [
    (power.BACHELOR090_PDF, '0:25'),
    (power.BOOK173_PDF, '0:100'),
    (power.DISS264_PDF, '0:50'),
    (power.DISS406_PDF, '0:75,100:150'),
    (power.MASTER116_PDF, '50:117'),
    genex.todo(
        power.DISS172_PDF,
        rawmaker=genex.CONFIG,
        figureo=True,
        tablero=True,
        cleanup=True,
    ),
    power.BACHELOR026_PDF,
    power.BACHELOR037_PDF,
    power.BACHELOR111_PDF,
    power.BACHELOR128_PDF,
    power.DISS144_PDF,
    power.DISS148_PDF,
    power.DOCU027_PDF,
    power.HC_DISS128,
    power.HC_DISS148,
    power.HC_DISS166,
    power.HC_DISS171,
    power.HC_DISS193,
    power.MASTER072_PDF,
    power.MASTER075_PDF,
    power.MASTER110_PDF,
    power.MASTER155_PDF,
    power.TECH019_PDF,
    power.TECH024_PDF,
]

WORKER = 5


def pytest_sessionstart(session):  # pylint:disable=W0613
    power.run()


RAWMAKER = '--text --line --horizontals ' + genex.CONFIG


def extract(resources):
    genex.extract(
        resources,
        cleanup=True,
        oneline=None,
        pagenumber=True,
        footnote=True,
        rawmaker=RAWMAKER,
        worker=WORKER,
    )
