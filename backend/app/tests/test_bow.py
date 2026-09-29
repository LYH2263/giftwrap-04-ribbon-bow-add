import pytest
from fastapi import HTTPException

from app.engines.wrap_math import paper_area, ribbon_estimate
from app.modules import ribbon_bow
from app.repositories import history, settings_repo
from app.services import estimate_service

pytestmark = pytest.mark.usefixtures("gw_db")

# 种子盒 1：书型盒 0.30 × 0.20 × 0.15
# cross 基准 = 2*(0.2+0.15)*2 + 0.3 + 0.5 = 2.20 m
# band  基准 = 2*(0.2+0.15) + 0.3 = 1.00 m
# 用纸面积（overlap 1.15）= 2*(.06+.045+.03)*1.15 = 0.3105 → 0.31 m²


def test_bow_off_equals_legacy_ribbon():
    cross = ribbon_estimate(0.30, 0.20, 0.15, "cross")
    band = ribbon_estimate(0.30, 0.20, 0.15, "band")
    off_cross = estimate_service.run_estimate(1, None, "cross", False, "", False)
    off_band = estimate_service.run_estimate(1, None, "band", False, "", False)
    assert off_cross["ribbon"]["ribbon_m"] == cross["ribbon_m"] == 2.2
    assert off_band["ribbon"]["ribbon_m"] == band["ribbon_m"] == 1.0
    assert off_cross["ribbon"]["bow_enabled"] is False
    assert off_cross["ribbon"]["bow_m"] == 0.0


def test_bow_on_adds_length_but_paper_never_moves():
    p0 = estimate_service.run_estimate(1, None, "cross", False, "", False)
    p1 = estimate_service.run_estimate(1, None, "cross", False, "", True, 0.3)
    p2 = estimate_service.run_estimate(1, None, "cross", False, "", True, 0.9)
    assert p1["ribbon"]["ribbon_m"] == 2.5
    assert p2["ribbon"]["ribbon_m"] == 3.1
    assert p0["paper_m2"] == p1["paper_m2"] == p2["paper_m2"] == 0.31
    assert p1["ribbon"]["bow_enabled"] is True and p1["ribbon"]["bow_m"] == 0.3


def test_bow_enabled_with_nonpositive_bow_fails_and_no_run_inserted():
    assert history.count_runs() == 0
    for bad in (0.0, -0.5):
        with pytest.raises(HTTPException) as ei:
            estimate_service.run_estimate(1, None, "cross", True, "", True, bad)
        assert ei.value.status_code == 400
    # 即便 save=True，也必须在落库前失败
    assert history.count_runs() == 0


def test_default_bow_m_used_when_enabled_without_explicit_value():
    r = estimate_service.run_estimate(1, None, "cross", False, "", True, None)
    assert r["ribbon"]["ribbon_m"] == round(2.2 + settings_repo.get_bow_m(), 2)


def test_saved_run_is_truth_and_pinned_after_default_changes():
    saved = estimate_service.run_estimate(1, None, "cross", True, "首单", True, 0.3)
    run_id = saved["run_id"]
    assert run_id is not None

    row = history.get_run(run_id)
    result = row["result"]
    # 落库须含三件套
    assert result["bow_enabled"] is True
    assert result["bow_m"] == 0.3
    assert result["ribbon_m"] == 2.5
    assert result["paper_m2"] == 0.31

    # 写入后改丝带页默认结长
    settings_repo.set_value("bow_m", "1.23")

    listed = history.list_runs()[0]
    assert listed["result"]["ribbon_m"] == 2.5
    assert listed["result"]["bow_m"] == 0.3
    again = history.get_run(run_id)["result"]
    # 列表摘要与详情一致，且钉住写入值，不按新默认重算
    assert again["ribbon_m"] == listed["result"]["ribbon_m"] == 2.5
    assert again["paper_m2"] == listed["result"]["paper_m2"] == 0.31

    # 同参再干算丝带，须与回看互证
    dry = estimate_service.run_estimate(1, None, "cross", False, "", True, 0.3)
    assert dry["ribbon"]["ribbon_m"] == again["ribbon_m"]
    assert dry["paper_m2"] == again["paper_m2"]

    # 改默认只影响新的、未显式给结长的计算
    fresh = estimate_service.run_estimate(1, None, "cross", False, "", True, None)
    assert fresh["ribbon"]["ribbon_m"] == round(2.2 + 1.23, 2)
    # 旧档仍是旧值
    assert history.get_run(run_id)["result"]["ribbon_m"] == 2.5
