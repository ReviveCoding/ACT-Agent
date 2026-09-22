from act_agent.preference.generate import generate_candidates


def test_scripted_pairs_have_ties_and_matched_seeds(tmp_path) -> None:
    manifest = generate_candidates(tmp_path / "pairs.parquet", worlds=10, keep_pairs=30)
    assert manifest["raw_candidates"] == 80
    assert manifest["ties_or_drops"] >= 10
    assert manifest["retained_pairs"] == 30
