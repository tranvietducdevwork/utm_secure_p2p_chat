# -*- coding: utf-8 -*-
"""Nội dung 3 chương KLTN — lý thuyết chi tiết, thiết kế có sơ đồ, kịch bản có đánh giá."""

import os

from kltn_diagrams import DIAGRAMS


def _d(key):
    return DIAGRAMS[key]


def _insert_diagram(doc, add_caption, add_diagram, add_image, key):
    d = _d(key)
    image_path = d.get("image")
    if image_path and os.path.isfile(image_path):
        add_image(doc, image_path)
    else:
        add_diagram(doc, d["lines"])
    add_caption(doc, d["caption"])


def add_chuong_1(doc, add_heading, add_body, add_bullets, add_page_break,
                 add_caption, add_diagram, add_table, add_image=None, **kwargs):
    add_heading(doc, "CHƯƠNG 1. CƠ SỞ LÝ THUYẾT")

    # ── 1.1 ──
    add_heading(doc, "1.1. Bối cảnh và vấn đề bảo mật trong nhắn tin số", level=2)
    add_body(doc,
        "Nhắn tin tức thời đã trở thành hạ tầng giao tiếp hàng ngày. Tuy nhiên, mô hình client–server "
        "truyền thống (Zalo, Messenger, email…) thường lưu tin nhắn trên máy chủ trung tâm dưới dạng "
        "plaintext hoặc mã hóa mà nhà cung cấp có thể giải mã. Điều này tạo ra ba nhóm rủi ro: "
        "(1) rò rỉ dữ liệu do tấn công vào server; (2) truy cập trái phép nội bộ; "
        "(3) yêu cầu pháp lý buộc cung cấp dữ liệu.")
    add_body(doc,
        "Mã hóa đầu cuối (End-to-End Encryption – E2E) và kiến trúc phân tán (Peer-to-Peer – P2P) "
        "là hai hướng tiếp cận bổ sung cho nhau: E2E bảo vệ nội dung; P2P giảm phụ thuộc relay tập trung. "
        "Đề tài kết hợp cả hai, đồng thời bổ sung relay ciphertext khi NAT/4G chặn kết nối trực tiếp.")

    add_heading(doc, "1.1.1. Mô hình tin cậy (Trust Model)", level=3)
    add_body(doc,
        "Trong đề tài, vùng tin cậy (Trusted Computing Base) là thiết bị của người dùng — nơi lưu private key "
        "và thực hiện mã hóa/giải mã. Vùng không tin cậy gồm Internet, signaling server trên Render, "
        "và bất kỳ node relay nào. Server được phép biết: username, hash mật khẩu, public key, mã phòng, "
        "metadata kết nối (online, thời điểm join-room). Server không được đọc plaintext chat ở chế độ mặc định.")
    add_table(doc,
        ["Tiêu chí", "Chat server truyền thống", "Secure P2P Chat (đề tài)"],
        [
            ["Nơi lưu tin nhắn", "Server (plaintext)", "Thiết bị user (SQLite)"],
            ["Server đọc nội dung", "Có", "Không (E2E mặc định)"],
            ["Ghép cặp user", "Danh bạ / ID", "Mã phòng chung"],
            ["Triển khai", "Data center", "Cloud signaling + app mobile"],
        ],
    )

    add_heading(doc, "1.1.2. Sơ đồ kiến trúc tổng quan", level=3)
    add_body(doc,
        "Hình 1.1 mô tả các thành phần và luồng tương tác chính. Hai client Flutter kết nối signaling server "
        "qua HTTPS/WSS; sau khi ghép phòng, trao đổi tin qua relay E2E hoặc WebRTC P2P.")
    _insert_diagram(doc, add_caption, add_diagram, add_image, "hinh_1_1_kien_truc_tong_quan")

    # ── 1.2 E2E ──
    add_heading(doc, "1.2. Mã hóa đầu cuối (E2E)", level=2)
    add_heading(doc, "1.2.1. Nguyên lý hoạt động", level=3)
    add_body(doc,
        "E2E đảm bảo tính bảo mật (confidentiality): chỉ người gửi và người nhận có khóa giải mã. "
        "Tính toàn vẹn (integrity): phát hiện sửa đổi ciphertext. Tính xác thực (authentication): "
        "xác nhận nguồn gốc tin nhắn thông qua khóa dùng chung dẫn xuất từ cặp khóa bất đối xứng.")
    add_heading(doc, "1.2.2. Trao đổi khóa X25519 (ECDH)", level=3)
    add_body(doc,
        "X25519 là triển khai Diffie–Hellman trên đường cong Curve25519. Mỗi user sinh cặp khóa (private, public). "
        "Public key công khai trên server; private key không bao giờ rời thiết bị. "
        "Shared secret = X25519(priv_A, pub_B) = X25519(priv_B, pub_A).")
    add_body(doc,
        "Đề tài dùng HKDF (HMAC-based Key Derivation Function) để dẫn xuất khóa AES-256 từ shared secret, "
        "tránh dùng trực tiếp output ECDH làm khóa mã hóa — best practice trong RFC 5869.")
    add_heading(doc, "1.2.3. AES-GCM — Authenticated Encryption", level=3)
    add_body(doc,
        "AES-GCM (Galois/Counter Mode) vừa mã hóa vừa tạo MAC xác thực trong một bước (AEAD). "
        "Mỗi tin nhắn dùng nonce 12 byte ngẫu nhiên, tránh tái sử dụng nonce với cùng khóa. "
        "Payload truyền đi gồm JSON: {n: nonce, c: ciphertext, m: mac} mã hóa Base64.")
    add_heading(doc, "1.2.4. So sánh E2E với TLS/HTTPS", level=3)
    add_table(doc,
        ["Lớp bảo vệ", "Bảo vệ đến đâu", "Server thấy plaintext?"],
        [
            ["HTTPS/TLS", "Client ↔ Server", "Có (server giải mã)"],
            ["E2E (đề tài)", "Client A ↔ Client B", "Không"],
        ],
    )

    # ── 1.3 P2P / WebRTC ──
    add_heading(doc, "1.3. Kiến trúc Peer-to-Peer và WebRTC", level=2)
    add_heading(doc, "1.3.1. Khái niệm P2P", level=3)
    add_body(doc,
        "P2P cho phép hai peer truyền dữ liệu trực tiếp. Ưu điểm: giảm tải server, độ trễ thấp, "
        "tăng quyền riêng tư. Nhược điểm: phức tạp NAT traversal, không đảm bảo peer luôn online.")
    add_heading(doc, "1.3.2. Stack WebRTC", level=3)
    add_bullets(doc, [
        "RTCPeerConnection: quản lý kết nối P2P, ICE, SDP.",
        "RTCDataChannel: kênh truyền dữ liệu tùy ý (text/binary) — dùng cho chat.",
        "STUN: khám phá địa chỉ public và loại NAT.",
        "TURN: relay media khi P2P thất bại (chưa triển khai trong đề tài).",
    ])
    add_heading(doc, "1.3.3. ICE và thách thức NAT trên 4G", level=3)
    add_body(doc,
        "ICE (Interactive Connectivity Establishment) thử lần lượt các candidate: host (IP local), "
        "srflx (IP public qua STUN), relay (qua TURN). Thiết bị 4G thường behind carrier-grade NAT "
        "khiến P2P trực tiếp thất bại. Đề tài giải quyết bằng relay E2E: server chỉ chuyển ciphertext, "
        "không phá vỡ mô hình bảo mật.")

    # ── 1.4 Signaling ──
    add_heading(doc, "1.4. Signaling server và relay ciphertext", level=2)
    add_body(doc,
        "WebRTC yêu cầu kênh out-of-band để trao đổi SDP offer/answer và ICE candidates — gọi là signaling. "
        "Signaling server đề tài dùng Node.js + Socket.IO, deploy Render. Ngoài WebRTC signaling, server "
        "relay event e2e-message chứa payload đã mã hóa. Ở chế độ mặc định, server không ghi message vào DB.")
    add_body(doc,
        "Đây khác biệt cốt lõi với Telegram/WhatsApp server: họ lưu và xử lý nội dung; server đề tài chỉ "
        "chuyển tiếp metadata kết nối và blob ciphertext realtime.")

    # ── 1.5 Room model ──
    add_heading(doc, "1.5. Mô hình phòng chat (Room-based matching)", level=2)
    add_body(doc,
        "Thay vì hiển thị toàn bộ user online (lộ metadata, khó dùng trên mobile), hai người nhập cùng "
        "mã phòng (≥ 4 ký tự, ví dụ KLTN2026). Server ghép họ vào roomStore; chỉ peer cùng phòng mới "
        "được relay tin nhắn và WebRTC. Mô hình tương tự Zoom/Meet nhưng cho chat E2E 1-1.")

    # ── 1.6 Privacy / local storage ──
    add_heading(doc, "1.6. Privacy by design và lưu trữ local-first", level=2)
    add_body(doc,
        "Nguyên tắc thu thập tối thiểu: server lưu username, bcrypt password hash, public key (users.json). "
        "Không có API /api/messages. Lịch sử chat lưu SQLite trên điện thoại — user sở hữu dữ liệu của mình. "
        "Nếu hacker chiếm server: không có nội dung chat (chế độ mặc định). Nếu chiếm điện thoại: đọc được SQLite — "
        "rủi ro chung của mọi app chat local.")

    # ── 1.7 Công nghệ ──
    add_heading(doc, "1.7. Công nghệ và tiêu chuẩn liên quan", level=2)
    add_table(doc,
        ["Thành phần", "Công nghệ", "Vai trò"],
        [
            ["Client", "Flutter 3.x, Dart", "UI đa nền tảng"],
            ["WebRTC", "flutter_webrtc", "P2P DataChannel"],
            ["Crypto", "cryptography (X25519, AES-GCM)", "E2E"],
            ["Local DB", "sqflite", "Lịch sử chat"],
            ["Signaling", "Node.js, Express, Socket.IO", "Auth, room, relay"],
            ["Deploy", "Render.com, HTTPS", "Cloud signaling"],
            ["Auth", "JWT, bcrypt", "Phiên làm việc"],
        ],
    )

    add_heading(doc, "1.8. Kết luận chương", level=2)
    add_body(doc,
        "Chương 1 đã trình bày nền tảng lý thuyết: E2E (X25519, HKDF, AES-GCM), P2P/WebRTC, signaling, "
        "relay ciphertext, room-based matching và privacy by design. Đây là cơ sở để Chương 2 thiết kế "
        "chi tiết kiến trúc, luồng dữ liệu và cấu trúc chương trình.")
    add_page_break(doc)


from kltn_chapter2 import add_chuong_2  # noqa: F401 — phiên bản mở rộng, chuyên sâu


def add_chuong_3(doc, add_heading, add_body, add_bullets, add_page_break,
                 add_caption, add_diagram, add_table, **kwargs):
    add_heading(doc, "CHƯƠNG 3. CÀI ĐẶT, TRIỂN KHAI VÀ THỬ NGHIỆM")

    add_heading(doc, "3.1. Môi trường và triển khai", level=2)
    add_table(doc,
        ["Hạng mục", "Chi tiết"],
        [
            ["Client", "Flutter 3.x, Android/iOS"],
            ["Server", "Node.js 20, Render.com"],
            ["URL", "https://utm-secure-p2p-chat.onrender.com"],
            ["Repo", "github.com/tranvietducdevwork/utm_secure_p2p_chat"],
            ["JWT_SECRET", "Biến môi trường trên Render"],
        ],
    )

    add_heading(doc, "3.2. Cài đặt tóm tắt", level=2)
    add_bullets(doc, [
        "Server: signaling_server/ — npm install, npm start; deploy Render rootDir signaling_server.",
        "App: flutter_app/ — flutter pub get; app_config.dart trỏ URL cloud.",
        "Không cần nhập IP LAN trên UI — URL cố định trong mã nguồn.",
    ])

    add_heading(doc, "3.3. Kịch bản thử nghiệm chức năng", level=2)
    add_body(doc,
        "Các kịch bản được thiết kế theo mẫu: Mục tiêu → Các bước thực hiện → Kết quả mong đợi → "
        "Kết quả thực tế → Đánh giá (Đạt/Không đạt).")

    add_heading(doc, "Kịch bản KT01: Đăng ký và đăng nhập", level=3)
    add_table(doc,
        ["Hạng mục", "Nội dung"],
        [
            ["Mục tiêu", "Xác minh tạo tài khoản và đăng nhập qua server cloud"],
            ["Các bước", "1. Mở app → Đăng ký user1/123456\n2. Đăng xuất\n3. Đăng nhập lại user1"],
            ["Kết quả mong đợi", "HTTP 201/200; vào màn phòng; log [Auth] login status=200"],
            ["Kết quả thực tế", "Đạt — đăng nhập thành công, AuthGate chuyển RoomScreen"],
            ["Đánh giá", "ĐẠT — chức năng auth hoạt động ổn định sau khi sửa lỗi token socket"],
        ],
    )

    add_heading(doc, "Kịch bản KT02: Vào phòng và thấy peer", level=3)
    add_table(doc,
        ["Hạng mục", "Nội dung"],
        [
            ["Mục tiêu", "Hai máy cùng mã phòng thấy nhau"],
            ["Các bước", "1. user1 vào phòng KLTN2026\n2. user2 vào phòng KLTN2026\n3. Quan sát lobby"],
            ["Kết quả mong đợi", "Mỗi bên thấy 1 peer trong danh sách"],
            ["Kết quả thực tế", "Đạt — room-users cập nhật realtime"],
            ["Đánh giá", "ĐẠT — mô hình room code đơn giản, phù hợp demo 4G"],
        ],
    )

    add_heading(doc, "Kịch bản KT03: Chat E2E qua relay", level=3)
    add_table(doc,
        ["Hạng mục", "Nội dung"],
        [
            ["Mục tiêu", "Gửi/nhận tin mã hóa giữa 2 điện thoại 4G"],
            ["Các bước", "1. user1 mở chat với user2\n2. Gửi 'Xin chào KLTN'\n3. user2 kiểm tra tin nhận"],
            ["Kết quả mong đợi", "Tin hiển thị; trạng thái relay E2E; lưu SQLite"],
            ["Kết quả thực tế", "Đạt — tin nhận trong < 2s sau khi server awake"],
            ["Đánh giá", "ĐẠT — relay ciphertext đáp ứng mục tiêu khi P2P thất bại"],
        ],
    )

    add_heading(doc, "Kịch bản KT04: Server không lưu tin (mặc định)", level=3)
    add_table(doc,
        ["Hạng mục", "Nội dung"],
        [
            ["Mục tiêu", "Xác minh messagesStored = 0"],
            ["Các bước", "1. Toggle demo TẮT\n2. Chat vài tin\n3. Mở /health trên trình duyệt"],
            ["Kết quả mong đợi", "Tin nhắn lưu: 0; bảng trống"],
            ["Kết quả thực tế", "Đạt — JSON và HTML đều hiện 0"],
            ["Đánh giá", "ĐẠT — đúng chính sách privacy by design"],
        ],
    )

    add_heading(doc, "Kịch bản KT05: Demo lưu ciphertext", level=3)
    add_table(doc,
        ["Hạng mục", "Nội dung"],
        [
            ["Mục tiêu", "Minh họa server thấy ciphertext nhưng không đọc được"],
            ["Các bước", "1. Bật 'Server lưu tin nhắn' (tắt plaintext)\n2. Chat\n3. Xem /health"],
            ["Kết quả mong đợi", "Bảng có dòng from/to; nội dung là chuỗi mã hóa; Đọc được = Không"],
            ["Kết quả thực tế", "Đạt — cột 'Đọc được?' hiển thị Không (E2E)"],
            ["Đánh giá", "ĐẠT — chứng minh E2E ngay cả khi server lưu blob"],
        ],
    )

    add_heading(doc, "Kịch bản KT06: Demo lưu plaintext (so sánh)", level=3)
    add_table(doc,
        ["Hạng mục", "Nội dung"],
        [
            ["Mục tiêu", "So sánh với chat server truyền thống"],
            ["Các bước", "1. Bật thêm 'Lưu plaintext'\n2. Chat\n3. Xem /health"],
            ["Kết quả mong đợi", "Nội dung đọc được plaintext; cột Đọc được = Có"],
            ["Kết quả thực tế", "Đạt — hacker DB đọc được nội dung"],
            ["Đánh giá", "ĐẠT — minh họa rủi ro; nhấn mạnh chế độ mặc định an toàn hơn"],
        ],
    )

    add_heading(doc, "Kịch bản KT07: Đăng xuất", level=3)
    add_table(doc,
        ["Hạng mục", "Nội dung"],
        [
            ["Mục tiêu", "Logout về màn đăng nhập"],
            ["Các bước", "1. Đang ở RoomScreen → bấm Logout"],
            ["Kết quả mong đợi", "AuthGate hiện LoginScreen"],
            ["Kết quả thực tế", "Đạt — sau khi sửa AuthGate + popUntil"],
            ["Đánh giá", "ĐẠT"],
        ],
    )

    add_heading(doc, "3.4. Tổng hợp đánh giá kịch bản", level=2)
    add_table(doc,
        ["Mã KT", "Tên", "Đánh giá", "Ghi chú"],
        [
            ["KT01", "Đăng ký/đăng nhập", "ĐẠT", "Cloud cold-start cần đợi ~30–90s"],
            ["KT02", "Vào phòng", "ĐẠT", ""],
            ["KT03", "Chat E2E relay", "ĐẠT", "Phụ thuộc server Render online"],
            ["KT04", "Không lưu server", "ĐẠT", "Cốt lõi đề tài"],
            ["KT05", "Demo ciphertext", "ĐẠT", "Minh chứng E2E qua /health"],
            ["KT06", "Demo plaintext", "ĐẠT", "So sánh"],
            ["KT07", "Đăng xuất", "ĐẠT", ""],
        ],
    )
    add_body(doc,
        "Tỷ lệ đạt: 7/7 kịch bản (100%). Hạn chế: Render free tier ngủ khi idle; P2P trực tiếp "
        "không ổn định trên 4G — đã có relay thay thế.")

    add_heading(doc, "3.5. Đánh giá bảo mật", level=2)
    add_table(doc,
        ["Tình huống tấn công", "Mức độ", "Giải thích"],
        [
            ["Hack DB server (mặc định)", "Thấp", "Không có plaintext chat"],
            ["Hack DB + bật demo plaintext", "Cao", "Cố ý minh họa — không phải chế độ sản xuất"],
            ["Nghe lén relay ciphertext", "Thấp", "Không giải mã được không có private key"],
            ["Đánh cắp điện thoại", "Trung bình", "Đọc được SQLite local"],
            ["Brute-force password", "Thấp", "bcrypt cost 10"],
        ],
    )

    add_heading(doc, "3.6. Hạn chế và hướng phát triển", level=2)
    add_body(doc,
        "Sau khi hoàn thành cài đặt, triển khai và kiểm thử, em nhận thấy hệ thống Secure P2P Chat "
        "đã đáp ứng các mục tiêu cốt lõi của đề tài. Tuy nhiên, do giới hạn về thời gian, phạm vi "
        "khóa luận tốt nghiệp và điều kiện triển khai thực tế, sản phẩm vẫn còn một số hạn chế cần "
        "được ghi nhận trung thực — đây cũng là cơ sở để đề xuất các hướng phát triển tiếp theo.")

    add_heading(doc, "3.6.1. Hạn chế về kiến trúc mạng và vận chuyển", level=3)
    add_body(doc,
        "Thứ nhất, kết nối WebRTC P2P trực tiếp chưa ổn định trên mạng di động 4G do carrier-grade NAT. "
        "Đề tài chưa triển khai TURN server nên khi ICE thất bại, hệ thống phụ thuộc hoàn toàn vào "
        "relay ciphertext qua signaling server. Điều này không làm suy yếu E2E (server vẫn chỉ thấy "
        "blob mã hóa), nhưng tăng độ trễ và tải lên server so với P2P thuần.")
    add_body(doc,
        "Thứ hai, signaling server deploy trên Render free tier: có hiện tượng cold-start 30–90 giây "
        "khi không có request, giới hạn băng thông và không đảm bảo SLA. Trong thử nghiệm, lần kết nối "
        "đầu sau khi server ngủ cần chờ đáng kể — ảnh hưởng trải nghiệm người dùng dù không ảnh hưởng "
        "tính đúng đắn của chức năng sau khi server thức dậy.")

    add_heading(doc, "3.6.2. Hạn chế về bảo mật và mã hóa", level=3)
    add_body(doc,
        "Hệ thống dùng X25519 + HKDF + AES-GCM cho mỗi cặp peer — đủ cho demo và chứng minh E2E, "
        "nhưng chưa triển khai Double Ratchet hay forward secrecy như Signal Protocol. Nếu private key "
        "bị lộ trong tương lai, toàn bộ tin nhắn đã mã hóa bằng khóa dẫn xuất từ cặp khóa đó có thể "
        "bị giải mã hồi tố (không có ratchet rekey per message).")
    add_body(doc,
        "Private key lưu SharedPreferences trên thiết bị — chưa tích hợp Android Keystore / iOS Keychain "
        "với sinh trắc học. Thiết bị bị root/jailbreak hoặc bị chiếm vật lý có thể đọc được SQLite "
        "và private key. Đây là rủi ro chung của app lưu trữ local-first, cần hardening thêm cho môi trường "
        "sản xuất.")
    add_body(doc,
        "Đề tài chưa thực hiện penetration testing độc lập hay security audit chuyên sâu. Đánh giá bảo mật "
        "ở mục 3.5 dựa trên phân tích thiết kế và kiểm thử chức năng, chưa có báo cáo từ bên thứ ba.")

    add_heading(doc, "3.6.3. Hạn chế về chức năng và quy mô", level=3)
    add_table(doc,
        ["Hạng mục", "Hiện trạng", "Ảnh hưởng"],
        [
            ["Số người chat", "1-1 trong phòng", "Chưa hỗ trợ group chat"],
            ["Loại tin nhắn", "Văn bản thuần", "Chưa file, ảnh, voice"],
            ["Thông báo", "Không có", "User không nhận push khi app nền"],
            ["Danh bạ / tìm bạn", "Chỉ mã phòng", "Phải thỏa thuận mã out-of-band"],
            ["Server metadata", "users.json file", "Chưa DB quan hệ, khó scale"],
            ["Đa thiết bị", "Một phiên/socket", "Chưa đồng bộ nhiều máy cùng tài khoản"],
        ],
    )

    add_heading(doc, "3.6.4. Hướng phát triển", level=3)
    add_body(doc,
        "Dựa trên các hạn chế trên, em đề xuất các hướng phát triển theo thứ tự ưu tiên:")
    add_bullets(doc, [
        "Triển khai TURN server (coturn) để cải thiện tỷ lệ P2P thành công trên 4G; giữ relay E2E "
        "làm fallback — không thay đổi mô hình bảo mật.",
        "Nâng cấp giao thức mã hóa sang Double Ratchet (thư viện libsignal hoặc tương đương) để có "
        "forward secrecy và rekey tự động sau mỗi tin nhắn.",
        "Bảo vệ private key bằng Android Keystore / Secure Enclave; tùy chọn mã hóa SQLite bằng SQLCipher.",
        "Mở rộng chức năng: gửi file/ảnh (mã hóa E2E từng blob), group chat trong phòng, push notification "
        "qua FCM/APNs (chỉ metadata, không plaintext).",
        "Nâng cấp hạ tầng: plan trả phí Render hoặc VPS riêng, persistent PostgreSQL cho metadata user "
        "(vẫn không lưu nội dung tin nhắn), monitoring và backup users.json.",
        "Kiểm thử bảo mật chuyên sâu: OWASP MSTG checklist, fuzzing API, review mã nguồn định kỳ.",
    ])
    add_body(doc,
        "Về mặt học thuật, các hướng trên giữ nguyên nguyên tắc privacy by design đã đặt ra từ Chương 1: "
        "server không đọc được plaintext chat ở chế độ mặc định; mọi mở rộng chức năng đều phải mã hóa "
        "E2E trước khi rời thiết bị client.")

    add_heading(doc, "3.7. Kết luận chương", level=2)
    add_body(doc,
        "Chương 3 đã trình bày quá trình cài đặt môi trường, triển khai signaling server trên Render "
        "và ứng dụng Flutter trên Android/iOS. Bảy kịch bản kiểm thử (KT01–KT07) được thực hiện "
        "theo mẫu có đánh giá cụ thể, đạt tỷ lệ 100%, bao phủ xác thực, ghép phòng, chat E2E relay, "
        "chính sách không lưu tin server, module demo và đăng xuất.")
    add_body(doc,
        "Mục 3.5 phân tích năm tình huống tấn công — xác nhận mô hình E2E giảm rủi ro khi server bị "
        "xâm nhập ở chế độ mặc định. Mục 3.6 ghi nhận trung thực các hạn chế về NAT/P2P, hạ tầng cloud, "
        "mức độ hardening crypto và phạm vi chức năng; đồng thời đề xuất sáu hướng phát triển tiếp theo "
        "mà vẫn bám sát mục tiêu bảo mật đề tài.")
    add_body(doc,
        "Như vậy, hệ thống Secure P2P Chat đã được triển khai thành công, kiểm thử đầy đủ và sẵn sàng "
        "cho giai đoạn bảo vệ khóa luận. Kết quả chương này cùng với thiết kế Chương 2 và cơ sở lý thuyết "
        "Chương 1 tạo thành luồng chứng minh hoàn chỉnh: từ phân tích — thiết kế — cài đặt — đánh giá.")
    add_page_break(doc)


def add_ket_luan(doc, add_heading, add_body, add_bullets, add_page_break):
    add_heading(doc, "KẾT LUẬN VÀ KIẾN NGHỊ")
    add_heading(doc, "Kết quả đạt được", level=2)
    add_bullets(doc, [
        "Hoàn thành nghiên cứu lý thuyết E2E, P2P, WebRTC, relay ciphertext và privacy by design.",
        "Thiết kế hệ thống có sơ đồ luồng dữ liệu và cấu trúc chương trình minh họa.",
        "Triển khai app Flutter + server Render; chat 4G qua mã phòng.",
        "Kiểm thử 7 kịch bản đạt 100%; module demo /health phục vụ hội đồng.",
    ])
    add_heading(doc, "Hạn chế", level=2)
    add_bullets(doc, [
        "P2P trực tiếp hạn chế trên NAT 4G; phụ thuộc relay.",
        "Render free tier; chưa audit chuyên sâu.",
    ])
    add_heading(doc, "Kiến nghị", level=2)
    add_bullets(doc, [
        "TURN server, Double Ratchet, group chat.",
        "Persistent DB metadata; vẫn không lưu message.",
        "Penetration testing độc lập.",
    ])
    add_page_break(doc)
    add_heading(doc, "TÀI LIỆU THAM KHẢO")
    add_heading(doc, "I. Tài liệu tiếng Anh (Tác giả nước ngoài & Tổ chức quốc tế)", level=2)
    refs_en = [
        'IETF, "HMAC-based Extract-and-Expand Key Derivation Function (HKDF)," RFC 5869, May 2010.',
        'IETF, "Interactive Connectivity Establishment (ICE): A Protocol for Network Address Translator (NAT) Traversal," RFC 8445, July 2018.',
        'M. Marlinspike, "The Double Ratchet Algorithm," Advanced Cryptographic Systems, 2016. [Online]. Available: https://signal.org/docs/specifications/doubleratchet/.',
        'National Institute of Standards and Technology (NIST), "Recommendation for Block Cipher Modes of Operation: Galois/Counter Mode (GCM) and GMAC," NIST Special Publication 800-38D, Nov. 2007.',
        'OWASP, Mobile Security Testing Guide (MSTG), Open Web Application Security Project, 2023.',
        'W3C, "WebRTC 1.0: Real-Time Communication Between Browsers," W3C Recommendation, Jan. 2021. [Online]. Available: https://www.w3.org/TR/webrtc/.',
    ]
    for i, ref in enumerate(refs_en, 1):
        add_body(doc, f"[{i}] {ref}")

    add_heading(doc, "II. Tài liệu trực tuyến (Trang tin điện tử & Tài liệu kỹ thuật)", level=2)
    refs_online = [
        'Flutter Documentation, "Flutter documentation," 2026. [Online]. Available: https://docs.flutter.dev/. [Accessed: June 19, 2026].',
        'Render Documentation, "Render Quickstarts and Guides," 2026. [Online]. Available: https://render.com/docs. [Accessed: June 19, 2026].',
        'Socket.IO, "Socket.IO Documentation," 2026. [Online]. Available: https://socket.io/docs/. [Accessed: June 19, 2026].',
    ]
    for i, ref in enumerate(refs_online, 7):
        add_body(doc, f"[{i}] {ref}")
