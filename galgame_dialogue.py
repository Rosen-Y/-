"""A small original choice-based romance dialogue demo.

The story aims for a bright school-life visual-novel mood: a memorable first
meeting, playful banter, warm character routes, and choices that change the
ending. It does not use any copyrighted characters, settings, or plotlines.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping, Sequence


@dataclass(frozen=True)
class Heroine:
    """A heroine profile used to render greetings and route text."""

    key: str
    name: str
    archetype: str
    introduction: str
    favorite_place: str
    gift_hint: str
    good_response: str
    normal_response: str
    ending: str


HEROINES: Mapping[str, Heroine] = {
    "1": Heroine(
        key="1",
        name="白羽澪",
        archetype="温柔可靠的学生会前辈",
        introduction="她抱着文件夹站在樱花树下，笑容像春日午后的牛奶茶。",
        favorite_place="旧图书馆",
        gift_hint="热可可",
        good_response="澪轻轻合上书页：『你居然记得……那今晚就让我多陪你一会儿吧。』",
        normal_response="澪温和地笑了笑：『谢谢你。下次，也让我了解你的喜好吧。』",
        ending="晚风吹过旧图书馆的窗帘，澪把书签夹进你们共同读完的书里。\n『明天，也一起回家吗？』她小声问。你的回答，被钟声温柔地盖住。",
    ),
    "2": Heroine(
        key="2",
        name="七濑葵",
        archetype="元气直球的青梅竹马",
        introduction="她从便利店门口冲出来，把一袋团子塞进你怀里，像夏天本身一样吵闹。",
        favorite_place="河堤",
        gift_hint="草莓团子",
        good_response="葵的眼睛一下亮起来：『嘿嘿，果然你懂我！奖励你陪我散步到河堤尽头！』",
        normal_response="葵鼓起脸颊：『也不是不开心啦……只是你还可以更懂我一点！』",
        ending="夕阳把河面染成橘色，葵突然跑到你前面倒着走。\n『以后不准一个人烦恼。因为——我会一直在你旁边！』",
    ),
    "3": Heroine(
        key="3",
        name="月城凛",
        archetype="外冷内热的天文社少女",
        introduction="天台的门被风推开，她正调试望远镜，语气冷淡却没有赶你离开。",
        favorite_place="天台",
        gift_hint="星图笔记本",
        good_response="凛别过脸：『只是普通的笔记本而已……但我会珍惜。今晚的观测，给你留位置。』",
        normal_response="凛点点头：『心意我收下了。至于谢礼……等你认出夏季大三角再说。』",
        ending="夜色降临，凛把望远镜让给你，指尖轻轻碰到你的手背。\n『星星很远，』她说，『但如果是和你一起看，好像就没那么远了。』",
    ),
}


@dataclass(frozen=True)
class GameState:
    """Result of a completed route."""

    heroine: Heroine
    affection: int
    choices: tuple[str, ...]

    @property
    def rank(self) -> str:
        if self.affection >= 3:
            return "恋人结局"
        if self.affection == 2:
            return "心动结局"
        return "朋友结局"


def describe_heroines() -> str:
    """Return a menu-friendly list of available heroines."""
    lines = ["可攻略角色："]
    for key, heroine in HEROINES.items():
        lines.append(f"{key}. {heroine.name} —— {heroine.archetype}")
    return "\n".join(lines)


def normalize_choice(choice: str, valid_choices: Sequence[str]) -> str:
    """Normalize player input and validate it against a set of string options."""
    normalized = choice.strip()
    if normalized not in valid_choices:
        valid = "/".join(valid_choices)
        raise ValueError(f"请输入有效选项：{valid}")
    return normalized


def select_heroine(choice: str) -> Heroine:
    """Select a heroine by menu choice."""
    normalized = normalize_choice(choice, tuple(HEROINES.keys()))
    return HEROINES[normalized]


def play_route(heroine_choice: str, place_choice: str, gift_choice: str) -> GameState:
    """Play a route from pre-supplied choices and return the final game state.

    This pure function keeps the dialogue engine easy to test while the CLI uses
    the same route logic for interactive play.
    """
    heroine = select_heroine(heroine_choice)
    affection = 1

    place_choice = normalize_choice(place_choice, ("1", "2", "3"))
    gift_choice = normalize_choice(gift_choice, ("1", "2", "3"))

    ideal_place = {"旧图书馆": "1", "河堤": "2", "天台": "3"}[heroine.favorite_place]
    ideal_gift = {"热可可": "1", "草莓团子": "2", "星图笔记本": "3"}[heroine.gift_hint]

    if place_choice == ideal_place:
        affection += 1
    if gift_choice == ideal_gift:
        affection += 1

    return GameState(heroine=heroine, affection=affection, choices=(heroine_choice, place_choice, gift_choice))


def build_scene(state: GameState) -> str:
    """Build the final route text for a completed game state."""
    heroine = state.heroine
    response = heroine.good_response if state.affection >= 3 else heroine.normal_response
    lines = [
        f"【{heroine.name}线】{state.rank}",
        heroine.introduction,
        response,
        "",
        heroine.ending if state.affection >= 2 else f"你们交换了联系方式。{heroine.name}说：『今天很开心，下次再聊吧。』",
    ]
    return "\n".join(lines)


def prompt_choice(prompt: str, valid_choices: Sequence[str], input_func: Callable[[str], str] = input) -> str:
    """Prompt until the player enters a valid choice."""
    while True:
        raw = input_func(prompt)
        try:
            return normalize_choice(raw, valid_choices)
        except ValueError as error:
            print(error)


def main() -> None:
    print("《春色心跳练习曲》—— 简易恋爱选项对话 Demo")
    print("灵感来自经典校园恋爱喜剧的明快节奏，但角色与剧情均为原创。\n")
    print(describe_heroines())
    heroine_choice = prompt_choice("\n想和谁展开今天的故事？请输入 1/2/3：", tuple(HEROINES.keys()))

    heroine = select_heroine(heroine_choice)
    print(f"\n{heroine.introduction}")
    print("\n放学后，你准备邀请她去一个地方：")
    print("1. 旧图书馆\n2. 河堤\n3. 天台")
    place_choice = prompt_choice("请选择 1/2/3：", ("1", "2", "3"))

    print("\n你想带一份小礼物：")
    print("1. 热可可\n2. 草莓团子\n3. 星图笔记本")
    gift_choice = prompt_choice("请选择 1/2/3：", ("1", "2", "3"))

    state = play_route(heroine_choice, place_choice, gift_choice)
    print("\n" + build_scene(state))


if __name__ == "__main__":
    main()
