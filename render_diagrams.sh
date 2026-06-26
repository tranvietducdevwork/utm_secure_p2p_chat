#!/bin/bash
# Render Mermaid .mmd → PNG cho KLTN
set -e
DIR="$(cd "$(dirname "$0")/diagrams" && pwd)"
cd "$DIR"

render() {
  local mmd="$1"
  local png="$2"
  echo "→ $png"
  npx --yes @mermaid-js/mermaid-cli@11.4.0 \
    -i "$mmd" -o "$png" \
    -b white -w 1400 -H 900 --scale 2
}

render hinh_1_1_kien_truc_tong_quan.mmd hinh_1_1_kien_truc_tong_quan.png
render hinh_2_1_ngu_canh.mmd hinh_2_1_ngu_canh.png
render hinh_2_2_dang_ky.mmd hinh_2_2_dang_ky.png
render hinh_2_3_vao_phong.mmd hinh_2_3_vao_phong.png
render hinh_2_4_gui_tin_e2e.mmd hinh_2_4_gui_tin_e2e.png
render hinh_2_5_flutter_layers.mmd hinh_2_5_flutter_layers.png
render hinh_2_6_server_modules.mmd hinh_2_6_server_modules.png
render hinh_2_7_bat_dau_chat.mmd hinh_2_7_bat_dau_chat.png
render hinh_2_8_sqlite_er.mmd hinh_2_8_sqlite_er.png

echo "Done — $(ls -1 *.png | wc -l | tr -d ' ') PNG files in $DIR"
