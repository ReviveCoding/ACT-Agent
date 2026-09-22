from act_agent.training.pairwise import flip_preference_labels


def test_label_flips_are_seeded_and_do_not_mutate_source() -> None:
    pairs = [
        {
            "pair_id": f"p{i}",
            "chosen_ids": [i],
            "rejected_ids": [-i],
            "chosen_labels": [i],
            "rejected_labels": [-i],
            "chosen_assistant_tokens": 1,
            "rejected_assistant_tokens": 2,
        }
        for i in range(20)
    ]
    flipped, ids = flip_preference_labels(pairs, 0.2, 11)
    again, same_ids = flip_preference_labels(pairs, 0.2, 11)
    assert len(ids) == 4
    assert ids == same_ids
    assert flipped == again
    assert all(pair["chosen_ids"] == [i] for i, pair in enumerate(pairs))
    for before, after in zip(pairs, flipped, strict=True):
        assert after["chosen_ids"] == (
            before["rejected_ids"] if before["pair_id"] in ids else before["chosen_ids"]
        )
