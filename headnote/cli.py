#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

import utila

import headnote

DESCRIPTION = 'TODO'

WORKPLAN = [
    utila.create_step(
        'common',
        inputs=[
            utila.ResultFile(producer='rawmaker', name='text_text'),
            utila.ResultFile(producer='rawmaker', name='text_positions'),
            utila.ResultFile('rawmaker', 'horizontals_horizontals'),
        ],
        output=('common',),
    ),
    utila.create_step(
        'fixed',
        inputs=[
            utila.ResultFile(producer='rawmaker', name='text_text'),
            utila.ResultFile(producer='rawmaker', name='text_positions'),
            utila.ResultFile('rawmaker', 'horizontals_horizontals'),
        ],
        output=('fixed',),
    ),
    utila.create_step(
        'result',
        inputs=[
            utila.ResultFile(producer='headnote', name='common_common'),
            utila.ResultFile(producer='headnote', name='fixed_fixed'),
        ],
        output=('result',),
    ),
]


def main():
    utila.featurepack(
        workplan=WORKPLAN,
        root=headnote.ROOT,
        featurepackage='headnote.feature',
        config=utila.FeaturePackConfig(
            description=DESCRIPTION,
            name=headnote.PROCESS,
            multiprocessed=True,
            pages=True,
            version=headnote.__version__,
        ),
    )
