# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import configo
import iamraw
import utila

ASSERT_HORIZONTAL_DIFF_MAX = configo.HV_FLOAT_PLUS(default=5.0)


def match(
    content: iamraw.PageContentHorizontals,
    expected: float,
    diff_max: float = 2.0,
) -> list:
    """Check if any horizontal match the `vertical_position`.

    Args:
        content(PageContentHorizontals): list with horizontal lines,
                                         mostly one page
        expected(float): position on the page in 'pixel'
        diff_max(float): max difference which matchs to `expected`
    Returns:
        True if any horizontal line match the `expected`
    """
    # TODO: Check y0/y1
    result = [
        item for item in content
        if utila.near(item.box.y0, expected, diff=diff_max)
    ]
    result = [tuple(item.box) for item in result]
    return result


def assert_horizontal(bounding):
    # assert abs(bounding.y0 - bounding.y1) < 2.0, str(bounding)
    # assert that item is horizontal
    diff = abs(bounding.y0 - bounding.y1)
    assert diff < ASSERT_HORIZONTAL_DIFF_MAX, str(bounding)


def biggest_hlinecluster_in_area(
    clusters: list,
    ymin: float,
    ymax: float,
    max_group_count: int = 1,  # pylint:disable=W0613
    min_group_size: int = 1,
) -> list[int]:
    """Determine cluster with maximal horizontal line count which fits
    in area between [ymin and ymax]. Return y-coordinate of cluster as a
    footer/header-border.

    Args:
        clusters: list of horizontal line cluster
        ymin: top y-bound of valid area
        ymax: bottom y-bound of valid area
        max_group_count: number of groups to detect(not supported yet)
        min_group_size: minimal amout of member in valid cluster
    Returns:
        `y-coordinate` of most matching cluster
        `None` if no cluster match [ymin,ymax] area
    """
    assert len(clusters) >= 1, 'no clusters provided'
    valid = cluster_in_area(clusters, ymin, ymax)
    if not any(valid):
        # no cluster is in range
        return None
    # remove clusters with to few elements
    valid = [item for item in valid if len(item) >= min_group_size]
    maximized = utila.select_maxi(
        valid,
        count=max_group_count,
    )
    result = []
    for cluster in maximized:
        bounding = cluster[0]
        result.append(bounding.y1)
    return result


def cluster_in_area(clusters, ymin, ymax):
    """How many horizontals lines of `cluster` are in range of [ymin,
    ymax].

    Iterate through `clusters` and check if `cluster` is in area of ymin
    to ymax."""
    result = []
    for cluster in clusters:
        # take first item in cluster to determine cluster location,
        # because all items in cluster have the same location.
        bounding = cluster[0]
        assert_horizontal(bounding)
        if iamraw.between(bounding, ymin, ymax):
            result.append(cluster)
    return result
