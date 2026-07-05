#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

import utilo

import headnote

DESCRIPTION = 'TODO'

WORKPLAN = [
    utilo.create_step(
        'common',
        inputs=[
            utilo.ResultFile(producer='rawmaker', name='text_text'),
            utilo.ResultFile(producer='rawmaker', name='text_positions'),
            utilo.ResultFile('rawmaker', 'horizontals_horizontals'),
        ],
        output=('common',),
    ),
    utilo.create_step(
        'fixed',
        inputs=[
            utilo.ResultFile(producer='rawmaker', name='text_text'),
            utilo.ResultFile(producer='rawmaker', name='text_positions'),
            utilo.ResultFile('rawmaker', 'horizontals_horizontals'),
        ],
        output=('fixed',),
    ),
    utilo.create_step(
        'result',
        inputs=[
            utilo.ResultFile(producer='headnote', name='common_common'),
            utilo.ResultFile(producer='headnote', name='fixed_fixed'),
        ],
        output=('result',),
    ),
]


def main():
    utilo.featurepack(
        workplan=WORKPLAN,
        root=headnote.ROOT,
        featurepackage='headnote.feature',
        config=utilo.FeaturePackConfig(
            description=DESCRIPTION,
            name=headnote.PROCESS,
            multiprocessed=True,
            pages=True,
            version=headnote.__version__,
        ),
    )
