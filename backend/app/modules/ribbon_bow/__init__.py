"""ribbon_bow: 蝴蝶结加长丝带。

在「改造前」的捆扎丝带长度（同盒、同 wrap_style）之上，打结时另加一段结长。
- 不打结：ribbon_m 与改造前完全一致。
- 打结：ribbon_m = base_m + bow_m，paper_m2 不参与、不受影响。
- 打结但 bow_m <= 0：非法，抛 ValueError，调用方须拒绝并禁止落库。
"""

def apply_bow(ribbon: dict, enabled: bool, bow_m: float) -> dict:
    base_m = float(ribbon["ribbon_m"])
    enabled = bool(enabled)
    if not enabled:
        ribbon["base_m"] = round(base_m, 2)
        ribbon["bow_enabled"] = False
        ribbon["bow_m"] = 0.0
        ribbon["ribbon_m"] = round(base_m, 2)
        return ribbon
    bow_m = float(bow_m)
    if bow_m <= 0:
        raise ValueError("bow_m must be positive when bow is enabled")
    ribbon["base_m"] = round(base_m, 2)
    ribbon["bow_enabled"] = True
    ribbon["bow_m"] = round(bow_m, 3)
    ribbon["ribbon_m"] = round(base_m + bow_m, 2)
    return ribbon
