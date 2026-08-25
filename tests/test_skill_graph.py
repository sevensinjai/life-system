"""The shape of the skill graph: nesting, moving, archiving."""

import pytest

from app.services.skills import (
    ancestor_ids,
    build_forest,
    depth_of,
    descendant_ids,
    rollup_shares,
    subtree_height,
    would_cycle,
)

# Singing(1) -> Pitch accuracy(2) -> Interval jumps(3), Breath control(4)
TREE = {1: None, 2: 1, 3: 2, 4: 1}


class FakeSkill:
    """Stand-in for a row, so the pure helpers can be tested without a session."""

    def __init__(self, id: int, parent_id: int | None) -> None:
        self.id = id
        self.parent_id = parent_id


def test_ancestors_run_from_the_nearest_parent_upward() -> None:
    assert ancestor_ids(TREE, 3) == [2, 1]
    assert ancestor_ids(TREE, 1) == []


def test_depth_counts_from_one() -> None:
    assert depth_of(TREE, 1) == 1
    assert depth_of(TREE, 2) == 2
    assert depth_of(TREE, 3) == 3


def test_descendants_cover_the_whole_subtree() -> None:
    assert sorted(descendant_ids(TREE, 1)) == [2, 3, 4]
    assert descendant_ids(TREE, 3) == []


def test_subtree_height_measures_the_branch_not_the_tree() -> None:
    assert subtree_height(TREE, 1) == 3  # Singing down to Interval jumps
    assert subtree_height(TREE, 2) == 2
    assert subtree_height(TREE, 3) == 1  # a leaf


def test_a_skill_cannot_become_its_own_ancestor() -> None:
    assert would_cycle(TREE, 1, 1) is True  # under itself
    assert would_cycle(TREE, 1, 3) is True  # under its own grandchild
    assert would_cycle(TREE, 3, 4) is False  # a genuine move
    assert would_cycle(TREE, 3, None) is False  # promoting to the top level


def test_a_malformed_map_does_not_hang() -> None:
    """A cycle in the data must not spin the walker forever."""
    broken = {1: 2, 2: 1}

    assert ancestor_ids(broken, 1) == [2, 1]


def test_full_rollup_credits_the_whole_branch() -> None:
    assert rollup_shares(100, 3, 1.0) == [100, 100, 100]


def test_reduced_rollup_decays_with_distance() -> None:
    assert rollup_shares(100, 4, 0.5) == [100, 50, 25, 12]


def test_rollup_stops_once_nothing_arrives() -> None:
    """No point walking further up a branch that receives zero."""
    assert rollup_shares(10, 5, 0.1) == [10, 1]


def test_no_rollup_credits_only_the_skill_trained() -> None:
    assert rollup_shares(100, 4, 0.0) == [100]


def test_build_forest_nests_children_under_parents() -> None:
    rows = [FakeSkill(1, None), FakeSkill(2, 1), FakeSkill(3, 2), FakeSkill(4, 1)]

    roots = build_forest(rows)

    assert [node.skill.id for node in roots] == [1]
    assert [node.skill.id for node in roots[0].children] == [2, 4]
    assert [node.skill.id for node in roots[0].children[0].children] == [3]
    assert roots[0].children[0].children[0].depth == 3


def test_build_forest_keeps_a_skill_whose_parent_was_filtered_out() -> None:
    """Hiding an archived parent must not make its children vanish."""
    roots = build_forest([FakeSkill(2, 1), FakeSkill(3, 2)])

    assert [node.skill.id for node in roots] == [2]
    assert [node.skill.id for node in roots[0].children] == [3]


# --------------------------------------------------------------------------
# Through the API
# --------------------------------------------------------------------------


def add(auth_client, name: str, parent_id: int | None = None) -> dict:
    response = auth_client.post(
        "/skills", json={"name": name, "parent_id": parent_id}
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_authoring_a_skill_and_a_sub_skill(auth_client) -> None:
    singing = add(auth_client, "Singing")
    pitch = add(auth_client, "Pitch accuracy", singing["id"])

    assert singing["level"] == 1 and singing["exp"] == 0
    assert singing["depth"] == 1
    assert pitch["depth"] == 2
    assert pitch["parent_id"] == singing["id"]


def test_the_graph_comes_back_nested(auth_client) -> None:
    singing = add(auth_client, "Singing")
    pitch = add(auth_client, "Pitch accuracy", singing["id"])
    add(auth_client, "Interval jumps", pitch["id"])
    add(auth_client, "Guitar")

    graph = auth_client.get("/skills").json()

    assert [node["name"] for node in graph] == ["Singing", "Guitar"]
    assert graph[0]["children"][0]["name"] == "Pitch accuracy"
    assert graph[0]["children"][0]["children"][0]["name"] == "Interval jumps"
    assert graph[1]["children"] == []


def test_a_skill_detail_carries_its_breadcrumb(auth_client) -> None:
    singing = add(auth_client, "Singing")
    pitch = add(auth_client, "Pitch accuracy", singing["id"])
    jumps = add(auth_client, "Interval jumps", pitch["id"])

    detail = auth_client.get(f"/skills/{jumps['id']}").json()

    assert [step["name"] for step in detail["path"]] == ["Singing", "Pitch accuracy"]
    assert detail["depth"] == 3
    assert detail["children"] == []


def test_siblings_cannot_share_a_name(auth_client) -> None:
    singing = add(auth_client, "Singing")
    add(auth_client, "Breath control", singing["id"])

    response = auth_client.post(
        "/skills", json={"name": "breath control", "parent_id": singing["id"]}
    )

    assert response.status_code == 422
    assert "already have a skill" in response.json()["error"]["message"]


def test_the_same_name_under_different_parents_is_fine(auth_client) -> None:
    singing = add(auth_client, "Singing")
    swimming = add(auth_client, "Swimming")

    add(auth_client, "Breath control", singing["id"])
    response = auth_client.post(
        "/skills", json={"name": "Breath control", "parent_id": swimming["id"]}
    )

    assert response.status_code == 201


def test_nesting_stops_at_the_depth_limit(auth_client) -> None:
    """Five deep by default; the sixth is refused."""
    parent = None
    for level in range(5):
        parent = add(auth_client, f"Level {level}", parent)["id"]

    response = auth_client.post("/skills", json={"name": "Too deep", "parent_id": parent})

    assert response.status_code == 422
    assert "limit is 5" in response.json()["error"]["message"]


def test_moving_a_skill_takes_its_subtree_along(auth_client) -> None:
    singing = add(auth_client, "Singing")
    guitar = add(auth_client, "Guitar")
    pitch = add(auth_client, "Pitch accuracy", singing["id"])
    jumps = add(auth_client, "Interval jumps", pitch["id"])

    auth_client.patch(f"/skills/{pitch['id']}", json={"parent_id": guitar["id"]})

    graph = {node["name"]: node for node in auth_client.get("/skills").json()}
    assert graph["Singing"]["children"] == []
    moved = graph["Guitar"]["children"][0]
    assert moved["name"] == "Pitch accuracy"
    assert moved["children"][0]["id"] == jumps["id"]
    assert moved["children"][0]["depth"] == 3


def test_a_skill_can_be_promoted_to_the_top_level(auth_client) -> None:
    singing = add(auth_client, "Singing")
    pitch = add(auth_client, "Pitch accuracy", singing["id"])

    promoted = auth_client.patch(
        f"/skills/{pitch['id']}", json={"parent_id": None}
    ).json()

    assert promoted["parent_id"] is None
    assert promoted["depth"] == 1


def test_a_move_that_would_make_a_cycle_is_refused(auth_client) -> None:
    singing = add(auth_client, "Singing")
    pitch = add(auth_client, "Pitch accuracy", singing["id"])

    response = auth_client.patch(
        f"/skills/{singing['id']}", json={"parent_id": pitch["id"]}
    )

    assert response.status_code == 422
    assert "its own ancestor" in response.json()["error"]["message"]


def test_a_move_that_would_breach_the_depth_limit_is_refused(auth_client) -> None:
    """The moved node fits; its subtree is what pushes past the limit."""
    deep = None
    for level in range(4):
        deep = add(auth_client, f"Level {level}", deep)["id"]

    root = add(auth_client, "Branch")["id"]
    middle = add(auth_client, "Middle", root)["id"]
    add(auth_client, "Leaf", middle)

    response = auth_client.patch(f"/skills/{root}", json={"parent_id": deep})

    assert response.status_code == 422
    assert "the limit is 5" in response.json()["error"]["message"]


def test_archiving_takes_the_subtree_with_it(auth_client) -> None:
    singing = add(auth_client, "Singing")
    pitch = add(auth_client, "Pitch accuracy", singing["id"])
    jumps = add(auth_client, "Interval jumps", pitch["id"])

    archived = auth_client.delete(f"/skills/{singing['id']}").json()

    assert {node["id"] for node in archived} == {
        singing["id"],
        pitch["id"],
        jumps["id"],
    }
    assert auth_client.get("/skills").json() == []
    assert len(auth_client.get("/skills?include_archived=true").json()) == 1


def test_restoring_a_skill_brings_its_ancestors_back(auth_client) -> None:
    """An active skill must never hang under an archived parent."""
    singing = add(auth_client, "Singing")
    pitch = add(auth_client, "Pitch accuracy", singing["id"])
    auth_client.delete(f"/skills/{singing['id']}")

    auth_client.patch(f"/skills/{pitch['id']}", json={"is_active": True})

    graph = auth_client.get("/skills").json()
    assert [node["name"] for node in graph] == ["Singing"]
    assert graph[0]["children"][0]["name"] == "Pitch accuracy"


def test_a_skill_cannot_be_nested_under_an_archived_one(auth_client) -> None:
    singing = add(auth_client, "Singing")
    auth_client.delete(f"/skills/{singing['id']}")

    response = auth_client.post(
        "/skills", json={"name": "Pitch accuracy", "parent_id": singing["id"]}
    )

    assert response.status_code == 422
    assert "archived" in response.json()["error"]["message"]


def test_renaming_and_describing_a_skill(auth_client) -> None:
    skill = add(auth_client, "Singing")

    edited = auth_client.patch(
        f"/skills/{skill['id']}",
        json={"name": "  Vocal   technique ", "description": "Range and control."},
    ).json()

    assert edited["name"] == "Vocal technique"
    assert edited["description"] == "Range and control."


def test_a_missing_skill_is_a_404(auth_client) -> None:
    response = auth_client.get("/skills/9999")

    assert response.status_code == 404
    assert response.json()["error"]["message"] == "No skill with id 9999."


def test_skills_are_private_to_their_owner(auth_client, client) -> None:
    mine = add(auth_client, "Singing")

    other = client.post(
        "/auth/register",
        json={
            "email": "other@example.com",
            "password": "another-hunter-1",
            "name": "Cha Hae-In",
            "timezone": "Asia/Seoul",
        },
    ).json()
    headers = {"Authorization": f"Bearer {other['access_token']}"}

    assert client.get("/skills", headers=headers).json() == []
    assert client.get(f"/skills/{mine['id']}", headers=headers).status_code == 404
    nested = client.post(
        "/skills", json={"name": "Theft", "parent_id": mine["id"]}, headers=headers
    )
    assert nested.status_code == 404


@pytest.mark.parametrize("payload", [{"name": "   "}, {"name": ""}])
def test_a_skill_needs_a_name(auth_client, payload) -> None:
    assert auth_client.post("/skills", json=payload).status_code == 422
