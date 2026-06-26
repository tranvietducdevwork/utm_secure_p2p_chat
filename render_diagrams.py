#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render diagrams/*.mmd → PNG qua Kroki (https://kroki.io)."""

import base64
import os
import urllib.request
import zlib

DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "diagrams")

FILES = [
    "hinh_1_1_kien_truc_tong_quan.mmd",
    "hinh_2_1_ngu_canh.mmd",
    "hinh_2_2_dang_ky.mmd",
    "hinh_2_3_vao_phong.mmd",
    "hinh_2_4_gui_tin_e2e.mmd",
    "hinh_2_5_flutter_layers.mmd",
    "hinh_2_6_server_modules.mmd",
    "hinh_2_7_bat_dau_chat.mmd",
    "hinh_2_8_sqlite_er.mmd",
]


def render_mermaid(mermaid_code: str, out_path: str) -> None:
    compressed = zlib.compress(mermaid_code.encode("utf-8"), 9)
    encoded = base64.urlsafe_b64encode(compressed).decode("ascii")
    url = f"https://kroki.io/mermaid/png/{encoded}"
    req = urllib.request.Request(url, headers={"User-Agent": "KLTN-render-diagrams"})
    with urllib.request.urlopen(req, timeout=90) as resp:
        data = resp.read()
    with open(out_path, "wb") as f:
        f.write(data)
    print(f"  ✓ {os.path.basename(out_path)} ({len(data):,} bytes)")


def main():
    print(f"Rendering {len(FILES)} diagrams → {DIR}/")
    for name in FILES:
        mmd_path = os.path.join(DIR, name)
        png_path = os.path.join(DIR, name.replace(".mmd", ".png"))
        with open(mmd_path, encoding="utf-8") as f:
            code = f.read()
        render_mermaid(code, png_path)
    print("Done.")


if __name__ == "__main__":
    main()
