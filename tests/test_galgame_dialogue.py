import pytest

from galgame_dialogue import (
    HEROINES,
    build_scene,
    describe_heroines,
    normalize_choice,
    play_route,
    select_heroine,
)


def test_describe_heroines_lists_three_distinct_personalities():
    menu = describe_heroines()

    assert "白羽澪" in menu
    assert "七濑葵" in menu
    assert "月城凛" in menu
    assert "温柔可靠" in menu
    assert "元气直球" in menu
    assert "外冷内热" in menu


def test_play_route_rewards_matching_place_and_gift():
    state = play_route("2", "2", "2")

    assert state.heroine.name == "七濑葵"
    assert state.affection == 3
    assert state.rank == "恋人结局"
    assert "陪我散步到河堤尽头" in build_scene(state)


def test_play_route_can_reach_friend_ending_with_mismatched_choices():
    state = play_route("3", "1", "1")

    assert state.heroine.name == "月城凛"
    assert state.affection == 1
    assert state.rank == "朋友结局"
    assert "交换了联系方式" in build_scene(state)


def test_select_heroine_and_validation_reject_invalid_choices():
    assert select_heroine(" 1 ") is HEROINES["1"]
    assert normalize_choice("3", ("1", "2", "3")) == "3"

    with pytest.raises(ValueError, match="请输入有效选项"):
        select_heroine("4")
