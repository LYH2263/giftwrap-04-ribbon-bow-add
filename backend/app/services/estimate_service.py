from fastapi import HTTPException
from app.engines.wrap_math import paper_area, ribbon_estimate
from app.modules import ribbon_bow
from app.repositories import boxes, history, settings_repo

def run_estimate(
    box_id: int,
    overlap: float | None,
    wrap_style: str,
    save: bool,
    note: str,
    bow_enabled: bool = False,
    bow_m: float | None = None,
):
    box = boxes.get_box(box_id)
    if not box:
        raise HTTPException(404)
    if box.get("data_quality") == "dirty":
        raise HTTPException(422, "dirty box")

    if bow_enabled and bow_m is None:
        bow_m = settings_repo.get_bow_m()
    # 开启蝴蝶结必须给正结长；非法参数直接失败，绝不落库（calc_runs 不增加）
    if bow_enabled and float(bow_m) <= 0:
        raise HTTPException(400, "bow_m must be positive when bow is enabled")

    ov = float(overlap) if overlap is not None else settings_repo.get_overlap()
    calc = paper_area(box["length"], box["width"], box["height"], ov)
    ribbon = ribbon_estimate(box["length"], box["width"], box["height"], wrap_style)
    ribbon = ribbon_bow.apply_bow(ribbon, bow_enabled, bow_m or 0.0)

    # 结长只加在丝带上，用纸面积保持原值，不随结长变化
    payload = {
        **calc,
        "ribbon": ribbon,
        "box_id": box_id,
        "bow_enabled": ribbon["bow_enabled"],
        "bow_m": ribbon["bow_m"],
        "ribbon_m": ribbon["ribbon_m"],
    }
    run_id = history.insert_run(box_id, ov, payload, note) if save else None
    return {"box": box, "run_id": run_id, **calc, "ribbon": ribbon}
