# -*- coding: utf-8 -*-
"""Chương 2 — Phân tích và thiết kế hệ thống (phiên bản mở rộng, chuyên sâu)."""

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


def add_chuong_2(doc, add_heading, add_body, add_bullets, add_page_break,
                 add_caption, add_diagram, add_table, add_image=None, **kwargs):
    add_heading(doc, "CHƯƠNG 2. PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG")

    # ══════════════════════════════════════════════════════════════════
    # 2.1 PHÂN TÍCH BÀI TOÁN
    # ══════════════════════════════════════════════════════════════════
    add_heading(doc, "2.1. Phân tích bài toán", level=2)

    add_heading(doc, "2.1.1. Mô tả bài toán thực tế", level=3)
    add_body(doc,
        "Trong bối cảnh giao tiếp di động hiện đại, nhu cầu trao đổi tin nhắn riêng tư giữa hai cá nhân "
        "ngày càng phổ biến. Tuy nhiên, hầu hết ứng dụng nhắn tin thương mại (Zalo, Messenger, Telegram "
        "ở chế độ mặc định) đều lưu trữ nội dung hội thoại trên máy chủ trung tâm. Khi server bị tấn công, "
        "dữ liệu người dùng có thể bị lộ; ngay cả khi không bị tấn công, nhà cung cấp dịch vụ vẫn có khả năng "
        "đọc được nội dung (trừ khi triển khai E2E đúng chuẩn và không có backdoor).")
    add_body(doc,
        "Bài toán đặt ra trong khóa luận: thiết kế và xây dựng hệ thống nhắn tin thời gian thực cho "
        "hai người dùng trên hai thiết bị di động (Android/iOS), kết nối qua mạng 4G hoặc WiFi, "
        "không yêu cầu cấu hình địa chỉ IP tĩnh, không cần cùng mạng LAN, và đặc biệt không lưu "
        "nội dung tin nhắn trên máy chủ ở chế độ vận hành mặc định. Hệ thống phải đảm bảo chỉ người gửi "
        "và người nhận có thể đọc được nội dung (mã hóa đầu cuối — E2E), đồng thời vẫn hoạt động ổn định "
        "trong điều kiện NAT carrier-grade phổ biến trên mạng di động Việt Nam.")

    add_heading(doc, "2.1.2. Yêu cầu chức năng", level=3)
    add_body(doc,
        "Dựa trên mục tiêu đề tài và khảo sát nhu cầu sử dụng thực tế, hệ thống Secure P2P Chat "
        "cần đáp ứng các yêu cầu chức năng (Functional Requirements — FR) sau:")
    add_table(doc,
        ["Mã FR", "Yêu cầu", "Mô tả chi tiết", "Độ ưu tiên"],
        [
            ["FR01", "Đăng ký tài khoản", "Tạo username/password, sinh cặp khóa X25519, lưu public key lên server", "Cao"],
            ["FR02", "Đăng nhập", "Xác thực JWT qua HTTPS, thiết lập phiên Socket.IO", "Cao"],
            ["FR03", "Ghép cặp theo mã phòng", "Hai user nhập cùng mã phòng (≥ 4 ký tự) để vào cùng phòng chat", "Cao"],
            ["FR04", "Chat E2E realtime", "Gửi/nhận tin nhắn văn bản mã hóa AES-GCM trong thời gian thực", "Cao"],
            ["FR05", "Relay ciphertext", "Khi P2P thất bại, server relay blob mã hóa mà không đọc được nội dung", "Cao"],
            ["FR06", "WebRTC P2P", "Thử thiết lập kênh DataChannel trực tiếp song song với relay", "Trung bình"],
            ["FR07", "Lịch sử cục bộ", "Lưu và hiển thị tin nhắn đã gửi/nhận trong SQLite trên thiết bị", "Cao"],
            ["FR08", "Đăng xuất", "Hủy phiên JWT, ngắt socket, quay về màn đăng nhập", "Cao"],
            ["FR09", "Module demo /health", "Toggle lưu tin trên server để minh họa E2E trước hội đồng", "Trung bình"],
        ],
    )
    add_body(doc,
        "Các yêu cầu FR01–FR05 và FR07–FR08 tạo thành lõi chức năng bắt buộc của sản phẩm. "
        "FR06 (P2P trực tiếp) được triển khai song song nhưng không phải điều kiện tiên quyết "
        "vì thực tế thử nghiệm cho thấy NAT 4G thường chặn kết nối P2P. FR09 phục vụ mục đích "
        "trình diễn và so sánh bảo mật, không nằm trong luồng sản xuất mặc định.")

    add_heading(doc, "2.1.3. Yêu cầu phi chức năng", level=3)
    add_body(doc,
        "Ngoài chức năng, hệ thống phải đáp ứng các yêu cầu phi chức năng (Non-Functional Requirements — NFR) "
        "liên quan đến bảo mật, hiệu năng, khả dụng và trải nghiệm người dùng:")
    add_table(doc,
        ["Mã NFR", "Loại", "Tiêu chí đo lường", "Giải pháp thiết kế"],
        [
            ["NFR01", "Bảo mật", "Server không đọc được plaintext chat (mặc định)", "E2E: X25519 + HKDF + AES-GCM"],
            ["NFR02", "Bảo mật", "Mật khẩu không lưu plaintext", "bcrypt cost factor 10"],
            ["NFR03", "Bảo mật", "Private key không rời thiết bị", "Lưu SharedPreferences, không gửi lên server"],
            ["NFR04", "Bảo mật", "Chỉ peer cùng phòng mới relay tin", "Kiểm tra roomStore.areInSameRoom()"],
            ["NFR05", "Hiệu năng", "Tin nhắn relay đến trong < 3 giây (sau server awake)", "Socket.IO realtime, payload nhỏ"],
            ["NFR06", "Khả dụng", "Hoạt động trên 4G/WiFi không cần cấu hình IP", "Signaling cloud cố định trên Render"],
            ["NFR07", "UX", "Ghép cặp đơn giản, không cần danh bạ", "Mô hình mã phòng (room code)"],
            ["NFR08", "Privacy", "Thu thập metadata tối thiểu", "Không API /api/messages, không lưu tin mặc định"],
            ["NFR09", "Tính toàn vẹn", "Phát hiện sửa đổi ciphertext", "AES-GCM MAC xác thực (AEAD)"],
            ["NFR10", "Khả chuyển", "Chạy Android và iOS từ một codebase", "Flutter cross-platform"],
        ],
    )

    add_heading(doc, "2.1.4. Ràng buộc và giả định", level=3)
    add_body(doc,
        "Trong quá trình phân tích, em xác định các ràng buộc (constraints) ảnh hưởng trực tiếp đến thiết kế:")
    add_bullets(doc, [
        "Ràng buộc mạng: Thiết bị 4G thường nằm sau NAT cấp nhà mạng (carrier-grade NAT), "
        "khiến WebRTC P2P trực tiếp thất bại nếu không có TURN server — đề tài chưa triển khai TURN.",
        "Ràng buộc hạ tầng: Signaling server deploy trên Render free tier — có cold-start 30–90 giây "
        "khi idle, giới hạn băng thông và không đảm bảo SLA cao.",
        "Ràng buộc phạm vi: Chỉ hỗ trợ chat văn bản 1-1 trong phòng, chưa file đính kèm, group chat, "
        "push notification hay Double Ratchet (forward secrecy).",
        "Ràng buộc thiết bị: Private key lưu SharedPreferences — nếu thiết bị bị root/jailbreak hoặc "
        "bị đánh cắp vật lý, attacker có thể đọc SQLite và private key.",
        "Ràng buộc thời gian: Khóa luận tốt nghiệp có thời hạn cố định, ưu tiên giải pháp đơn giản, "
        "chứng minh được E2E thay vì tối ưu hóa toàn diện như Signal Protocol.",
    ])
    add_body(doc,
        "Các giả định (assumptions) đặt ra khi thiết kế:")
    add_bullets(doc, [
        "Người dùng có kết nối Internet ổn định (4G hoặc WiFi) khi chat.",
        "Hai người trao đổi mã phòng qua kênh ngoài băng (nói miệng, gọi điện, Zalo…) — out-of-band.",
        "Signaling server Render hoạt động bình thường (HTTPS/WSS), JWT_SECRET được cấu hình an toàn.",
        "Thiết bị người dùng không bị malware can thiệp vào quá trình mã hóa/giải mã.",
        "Mỗi phòng chỉ có tối đa vài peer (thiết kế cho 1-1, không tối ưu cho hội thoại nhóm lớn).",
    ])

    add_heading(doc, "2.1.5. Phương án giải quyết tổng thể", level=3)
    add_body(doc,
        "Từ phân tích trên, em lựa chọn kiến trúc lai (hybrid architecture) kết hợp ba thành phần chính:")
    add_bullets(doc, [
        "Client Flutter: Giao diện người dùng, mã hóa E2E (e2e_crypto.dart), quản lý phiên chat "
        "(chat_session.dart), lưu trữ cục bộ SQLite.",
        "Signaling Server Node.js trên Render: Xác thực JWT, quản lý phòng (roomStore), relay metadata "
        "WebRTC và ciphertext qua Socket.IO — không lưu tin nhắn mặc định.",
        "STUN Server công khai (Google): Hỗ trợ ICE candidate discovery cho WebRTC P2P.",
    ])
    add_body(doc,
        "Chiến lược vận chuyển tin nhắn được thiết kế theo mô hình relay-first: khi bắt đầu phiên chat, "
        "hệ thống kích hoạt relay E2E ngay lập tức để đảm bảo người dùng có thể gửi tin; đồng thời "
        "thử thiết lập kênh WebRTC P2P song song. Nếu P2P thành công trong thời gian chờ "
        "(AppConfig.p2pConnectTimeout), chế độ chuyển sang P2P; nếu thất bại, tiếp tục dùng relay. "
        "Cách tiếp cận này cân bằng giữa tính khả dụng (luôn chat được trên 4G) và mục tiêu P2P "
        "(giảm tải server khi môi trường mạng cho phép).")

    # ══════════════════════════════════════════════════════════════════
    # 2.2 SƠ ĐỒ NGỮ CẢNH VÀ TÁC NHÂN
    # ══════════════════════════════════════════════════════════════════
    add_heading(doc, "2.2. Sơ đồ ngữ cảnh và tác nhân", level=2)

    add_heading(doc, "2.2.1. Phân tích tác nhân", level=3)
    add_body(doc,
        "Theo phương pháp UML, tác nhân (actor) là thực thể bên ngoài tương tác trực tiếp với hệ thống. "
        "Secure P2P Chat có ba tác nhân chính và một tác nhân phụ:")
    add_table(doc,
        ["Tác nhân", "Loại", "Vai trò", "Tương tác chính"],
        [
            ["Người dùng (User)", "Chính", "Sử dụng app chat trên điện thoại",
             "Đăng ký, đăng nhập, vào phòng, chat, xem lịch sử, đăng xuất"],
            ["Signaling Server", "Chính", "Node.js trên Render — điều phối kết nối",
             "Auth JWT, ghép phòng, relay ciphertext/metadata, WebRTC signaling"],
            ["STUN Server", "Phụ", "Google STUN công khai (stun.l.google.com)",
             "Cung cấp địa chỉ public/reflexive cho ICE candidate"],
            ["Hội đồng / Người đánh giá", "Phụ", "Quan sát demo bảo mật",
             "Truy cập GET /health, xem dashboard messagesStored"],
        ],
    )
    add_body(doc,
        "Tác nhân Người dùng đại diện cho hai (hoặc nhiều) cá nhân sử dụng ứng dụng Flutter trên thiết bị "
        "Android/iOS. Mỗi user có danh tính riêng (username), cặp khóa X25519 riêng và phiên Socket.IO riêng. "
        "Signaling Server là thành phần duy nhất luôn online trên cloud; nó không phải là peer chat mà "
        "đóng vai trò trung gian tin cậy một phần (chỉ cho metadata và relay ciphertext). "
        "STUN Server là dịch vụ bên thứ ba, không thuộc phạm vi phát triển của đề tài.")

    add_heading(doc, "2.2.2. Sơ đồ ngữ cảnh hệ thống", level=3)
    add_body(doc,
        "Hình 2.1 mô tả ranh giới hệ thống (system boundary) và các luồng tương tác giữa tác nhân. "
        "Hệ thống Secure P2P Chat (trong khung) bao gồm Flutter App và Signaling Server. "
        "Bên ngoài ranh giới: người dùng, STUN server, và Internet.")
    _insert_diagram(doc, add_caption, add_diagram, add_image, "hinh_2_1_ngu_canh_he_thong")

    add_heading(doc, "2.2.3. Ranh giới tin cậy và dữ liệu qua ranh giới", level=3)
    add_body(doc,
        "Phân tích ranh giới tin cậy (trust boundary) giúp xác định dữ liệu nào được phép đi qua ranh giới "
        "và ở dạng nào:")
    add_table(doc,
        ["Luồng dữ liệu", "Hướng", "Dạng dữ liệu", "Server đọc được?"],
        [
            ["Đăng ký/đăng nhập", "Client → Server", "username, bcrypt hash, publicKey, JWT", "Có (metadata)"],
            ["Relay tin nhắn", "Client → Server → Client", "JSON ciphertext {n, c, m}", "Không (E2E)"],
            ["WebRTC SDP/ICE", "Client ↔ Server ↔ Client", "SDP offer/answer, ICE candidate", "Có (metadata)"],
            ["Lịch sử chat", "Nội bộ client", "SQLite plaintext local", "Không (không gửi lên server)"],
            ["Private key", "Nội bộ client", "X25519 private key Base64", "Không (không bao giờ gửi)"],
        ],
    )
    add_body(doc,
        "Điểm quan trọng: dù server relay ciphertext, nó chỉ nhận blob đã mã hóa AES-GCM mà không có "
        "private key của bất kỳ user nào, nên không thể giải mã. Đây là sự khác biệt cốt lõi so với "
        "mô hình chat server truyền thống, nơi server giải mã TLS rồi lưu plaintext vào database.")

    # ══════════════════════════════════════════════════════════════════
    # 2.3 USE CASE
    # ══════════════════════════════════════════════════════════════════
    add_heading(doc, "2.3. Phân tích use case", level=2)

    add_heading(doc, "2.3.1. Tổng quan use case", level=3)
    add_body(doc,
        "Hệ thống có bảy use case chính (UC01–UC07), bao phủ toàn bộ vòng đời tương tác của người dùng "
        "từ khởi tạo tài khoản đến trình diễn demo bảo mật. Bảng tổng hợp:")
    add_table(doc,
        ["Mã UC", "Tên", "Tác nhân", "Mô tả ngắn"],
        [
            ["UC01", "Đăng ký", "User", "Tạo tài khoản + sinh khóa X25519"],
            ["UC02", "Đăng nhập", "User", "Xác thực JWT, kết nối socket"],
            ["UC03", "Vào phòng", "User", "Nhập mã phòng, thấy peer"],
            ["UC04", "Chat E2E", "User", "Gửi/nhận tin relay hoặc P2P"],
            ["UC05", "Lịch sử local", "User", "Đọc SQLite sau khi mở lại app"],
            ["UC06", "Đăng xuất", "User", "AuthGate → LoginScreen"],
            ["UC07", "Demo /health", "User, Hội đồng", "Toggle lưu tin server cho minh chứng"],
        ],
    )

    add_heading(doc, "2.3.2. UC01 — Đăng ký tài khoản", level=3)
    add_table(doc,
        ["Hạng mục", "Nội dung"],
        [
            ["Mô tả", "Người dùng mới tạo tài khoản với username/password; hệ thống sinh cặp khóa X25519"],
            ["Tiền điều kiện", "App đã cài đặt; server Render online; username chưa tồn tại"],
            ["Luồng chính",
             "1. User nhập username/password trên LoginScreen\n"
             "2. App gọi E2ECrypto.generateKeyPair()\n"
             "3. App gửi POST /api/register {username, password, publicKey}\n"
             "4. Server bcrypt hash password, lưu users.json, trả JWT\n"
             "5. App lưu token + privateKey vào SharedPreferences\n"
             "6. AuthGate chuyển sang RoomScreen"],
            ["Luồng phụ A", "Username đã tồn tại → HTTP 409, hiển thị lỗi"],
            ["Luồng phụ B", "Server không phản hồi (cold-start) → hiển thị thông báo đợi"],
            ["Hậu điều kiện", "Tài khoản tạo thành công; user online; private key chỉ trên thiết bị"],
        ],
    )

    add_heading(doc, "2.3.3. UC02 — Đăng nhập", level=3)
    add_table(doc,
        ["Hạng mục", "Nội dung"],
        [
            ["Mô tả", "User đã có tài khoản xác thực và thiết lập phiên Socket.IO"],
            ["Tiền điều kiện", "Tài khoản đã đăng ký; app có private key local (hoặc tạo mới nếu mất)"],
            ["Luồng chính",
             "1. User nhập username/password\n"
             "2. App gửi POST /api/login\n"
             "3. Server xác minh bcrypt, trả JWT + publicKey\n"
             "4. App lưu token, kết nối Socket.IO\n"
             "5. App emit authenticate {token}\n"
             "6. Server verify JWT, emit authenticated\n"
             "7. AuthGate → RoomScreen"],
            ["Luồng phụ", "Sai mật khẩu → HTTP 401; token hết hạn → yêu cầu đăng nhập lại"],
            ["Hậu điều kiện", "Phiên JWT hợp lệ; socket authenticated; user trong userStore online"],
        ],
    )

    add_heading(doc, "2.3.4. UC03 — Vào phòng chat", level=3)
    add_table(doc,
        ["Hạng mục", "Nội dung"],
        [
            ["Mô tả", "User nhập mã phòng để ghép cặp với peer khác đang online"],
            ["Tiền điều kiện", "Đã đăng nhập; socket authenticated"],
            ["Luồng chính",
             "1. User nhập mã phòng (ví dụ KLTN2026) trên RoomScreen\n"
             "2. App emit join-room {roomCode}\n"
             "3. Server normalize mã, thêm user vào roomStore\n"
             "4. Server emit room-joined {roomCode, users[]} kèm publicKey peer\n"
             "5. Server broadcast room-users cho tất cả member\n"
             "6. UI hiển thị danh sách peer trong phòng"],
            ["Luồng phụ A", "Mã phòng < 4 ký tự → room-error"],
            ["Luồng phụ B", "Chưa có peer → danh sách trống, chờ user khác vào"],
            ["Hậu điều kiện", "User thuộc phòng; có thể bắt đầu chat với peer cùng phòng"],
        ],
    )

    add_heading(doc, "2.3.5. UC04 — Chat E2E", level=3)
    add_table(doc,
        ["Hạng mục", "Nội dung"],
        [
            ["Mô tả", "Trao đổi tin nhắn văn bản mã hóa E2E qua relay hoặc P2P DataChannel"],
            ["Tiền điều kiện", "Đã vào phòng; có ít nhất 1 peer; peer có publicKey"],
            ["Luồng chính",
             "1. User chọn peer → mở ChatScreen\n"
             "2. ChatSession.start(): derive shared secret, bật relay mode\n"
             "3. User nhập tin → ChatSession.sendMessage(plaintext)\n"
             "4. App mã hóa AES-GCM → emit e2e-message {to, payload}\n"
             "5. Server relay → peer nhận e2e-message\n"
             "6. Peer giải mã → hiển thị + lưu SQLite"],
            ["Luồng phụ A", "P2P thành công → chuyển sang ChatTransportMode.p2p"],
            ["Luồng phụ B", "Giải mã thất bại → log lỗi, bỏ qua tin (MAC invalid)"],
            ["Hậu điều kiện", "Tin hiển thị trên cả hai thiết bị; lưu local SQLite"],
        ],
    )

    add_heading(doc, "2.3.6. UC05 — Xem lịch sử cục bộ", level=3)
    add_table(doc,
        ["Hạng mục", "Nội dung"],
        [
            ["Mô tả", "Đọc tin nhắn đã lưu trong SQLite khi mở lại app hoặc quay lại màn chat"],
            ["Tiền điều kiện", "Đã từng chat với peer; dữ liệu còn trong secure_p2p_chat.db"],
            ["Luồng chính",
             "1. User mở ChatScreen với peer\n"
             "2. LocalDbService.getMessages(peerUsername)\n"
             "3. Hiển thị danh sách tin theo timestamp ASC"],
            ["Hậu điều kiện", "Lịch sử hiển thị đúng; không cần kết nối server để đọc lịch sử cũ"],
        ],
    )

    add_heading(doc, "2.3.7. UC06 — Đăng xuất", level=3)
    add_table(doc,
        ["Hạng mục", "Nội dung"],
        [
            ["Mô tả", "Kết thúc phiên làm việc, quay về màn đăng nhập"],
            ["Luồng chính",
             "1. User bấm Logout trên RoomScreen\n"
             "2. App xóa token SharedPreferences, disconnect socket\n"
             "3. AppState.isLoggedIn = false\n"
             "4. AuthGate rebuild → LoginScreen"],
            ["Hậu điều kiện", "Socket ngắt; user offline trên server; private key vẫn local"],
        ],
    )

    add_heading(doc, "2.3.8. UC07 — Demo bảo mật /health", level=3)
    add_table(doc,
        ["Hạng mục", "Nội dung"],
        [
            ["Mô tả", "Bật/tắt chế độ lưu tin trên server để minh họa E2E trước hội đồng"],
            ["Luồng chính",
             "1. User mở Demo Settings Sheet\n"
             "2. POST /api/demo/settings {storeMessagesOnServer, storePlaintextOnServer}\n"
             "3. Chat vài tin nhắn\n"
             "4. Hội đồng mở GET /health trên trình duyệt\n"
             "5. Quan sát bảng: Từ | Đến | Nội dung server thấy | Đọc được?"],
            ["Hậu điều kiện", "Chứng minh trực quan: ciphertext không đọc được; plaintext đọc được"],
        ],
    )

    # ══════════════════════════════════════════════════════════════════
    # 2.4 THIẾT KẾ LUỒNG DỮ LIỆU
    # ══════════════════════════════════════════════════════════════════
    add_heading(doc, "2.4. Thiết kế luồng dữ liệu", level=2)
    add_body(doc,
        "Luồng dữ liệu (data flow) mô tả cách thông tin di chuyển giữa các thành phần hệ thống "
        "trong từng kịch bản sử dụng. Phần này trình bày chi tiết năm luồng chính, kèm phân tích "
        "dạng dữ liệu tại mỗi bước.")

    add_heading(doc, "2.4.1. Luồng đăng ký tài khoản", level=3)
    add_body(doc,
        "Luồng đăng ký là điểm khởi đầu của vòng đời người dùng. Đặc biệt quan trọng: cặp khóa X25519 "
        "được sinh ngay trên thiết bị client, private key không bao giờ truyền qua mạng.")
    add_bullets(doc, [
        "Bước 1 — Nhập liệu UI: User nhập username (duy nhất) và password trên LoginScreen. "
        "Password chỉ tồn tại trong bộ nhớ tạm của app.",
        "Bước 2 — Sinh khóa: App gọi E2ECrypto.generateKeyPair() sử dụng package cryptography. "
        "Kết quả: SimpleKeyPair gồm private key (32 byte) và public key (32 byte).",
        "Bước 3 — Gửi đăng ký: POST /api/register với body JSON "
        "{username, password, publicKey} — publicKey là Base64 của public key bytes.",
        "Bước 4 — Xử lý server: Server kiểm tra username chưa tồn tại, bcrypt.hash(password, 10), "
        "lưu vào users.json: {id, username, passwordHash, publicKey, createdAt}. Trả JWT (exp 7 ngày).",
        "Bước 5 — Lưu local: App lưu jwt_token và private_key (Base64) vào SharedPreferences. "
        "Đây là vùng tin cậy duy nhất chứa private key.",
        "Bước 6 — Chuyển màn hình: AuthGate phát hiện isLoggedIn=true → hiển thị RoomScreen.",
    ])
    _insert_diagram(doc, add_caption, add_diagram, add_image, "hinh_2_2_luong_dang_ky")
    add_body(doc,
        "Phân tích bảo mật luồng đăng ký: password truyền qua HTTPS nên được bảo vệ bởi TLS trong transit. "
        "Trên server chỉ lưu bcrypt hash — ngay cả khi users.json bị lộ, attacker vẫn phải brute-force. "
        "Public key công khai là thiết kế đúng của E2E; private key không xuất hiện trong bất kỳ HTTP request nào.")

    add_heading(doc, "2.4.2. Luồng đăng nhập và xác thực socket", level=3)
    add_body(doc,
        "Sau đăng ký hoặc khi mở lại app, user cần đăng nhập để thiết lập phiên. Luồng gồm hai giai đoạn: "
        "HTTP auth (JWT) và Socket.IO auth (gắn socket với user identity).")
    add_bullets(doc, [
        "Giai đoạn HTTP: POST /api/login {username, password} → server bcrypt.compare → trả {token, user}.",
        "Giai đoạn Socket: App kết nối wss://server/socket.io/, emit authenticate {token}.",
        "Server verify JWT bằng jsonwebtoken, tìm user trong userStore, gọi setOnline(username, socketId).",
        "Server emit authenticated {user} — app biết socket đã được gắn danh tính.",
        "Mọi event sau đó (join-room, e2e-message) đều yêu cầu currentUser != null trên server.",
    ])
    add_body(doc,
        "Thiết kế tách HTTP auth và socket auth cho phép REST API và realtime channel độc lập. "
        "JWT có thời hạn (exp) buộc re-login định kỳ. Nếu token không hợp lệ, server emit auth-error "
        "và không xử lý các event tiếp theo — nguyên tắc fail-secure.")

    add_heading(doc, "2.4.3. Luồng vào phòng (room matching)", level=3)
    add_body(doc,
        "Mô hình ghép cặp theo mã phòng thay thế danh bạ/ID cố định. Hai user chỉ cần thỏa thuận "
        "một chuỗi ký tự (out-of-band) để vào cùng phòng — đơn giản cho demo và phù hợp mobile.")
    add_bullets(doc, [
        "User A nhập 'KLTN2026' → join-room → server normalize (uppercase, trim) → roomStore.joinRoom().",
        "User B nhập cùng mã → join-room → server thêm B vào phòng, emit room-joined cho B kèm danh sách peer (gồm A và publicKey).",
        "Server broadcast room-users cho tất cả member — A cũng thấy B xuất hiện.",
        "roomStore lưu mapping: roomCode → Set<username> và username → roomCode (mỗi user chỉ ở 1 phòng).",
        "Khi user disconnect: server tự leave-room, broadcast user-left-room cho peer còn lại.",
    ])
    _insert_diagram(doc, add_caption, add_diagram, add_image, "hinh_2_3_luong_vao_phong")
    add_body(doc,
        "Ràng buộc bảo mật: hàm canTalk() trên server kiểm tra roomStore.areInSameRoom(sender, receiver) "
        "trước khi relay bất kỳ e2e-message hay webrtc-signaling nào. User ở phòng khác nhau không thể "
        "gửi tin cho nhau dù biết username — ngăn chặn spam và lộ ciphertext ngoài phòng.")

    add_heading(doc, "2.4.4. Luồng gửi tin E2E qua relay", level=3)
    add_body(doc,
        "Đây là luồng vận hành chính trên mạng 4G. Plaintext chỉ tồn tại trong RAM của thiết bị gửi "
        "và thiết bị nhận; mọi dữ liệu qua server đều là ciphertext.")
    add_bullets(doc, [
        "Bước 1 — Derive shared secret: ChatSession gọi E2ECrypto.deriveSharedSecret(localKeyPair, remotePublicKey). "
        "Bên trong: X25519 ECDH → raw secret → HKDF (salt='secure-p2p-chat', info='e2e-aes-gcm') → AES-256 key.",
        "Bước 2 — Mã hóa: encryptMessage() sinh nonce 12 byte ngẫu nhiên, AES-GCM encrypt → "
        "payload JSON {n: nonce_b64, c: ciphertext_b64, m: mac_b64}.",
        "Bước 3 — Gửi relay: signaling.sendEncryptedMessage(to, payload) → emit e2e-message qua Socket.IO.",
        "Bước 4 — Server relay: handlers.js nhận event, kiểm tra canTalk(), forward emit e2e-message "
        "đến socketId của peer. Ở chế độ mặc định: KHÔNG ghi messageStore.",
        "Bước 5 — Giải mã peer: handleRelayPayload() → decryptMessage() → onIncomingMessage(plaintext).",
        "Bước 6 — Lưu local: LocalDbService.saveMessage() ghi vào bảng messages và cập nhật conversations.",
    ])
    _insert_diagram(doc, add_caption, add_diagram, add_image, "hinh_2_4_luong_gui_tin_e2e")
    add_body(doc,
        "Phân tích độ phức tạp: mỗi tin nhắn thực hiện 1 lần ECDH derive (có thể cache shared secret trong "
        "ChatSession), 1 lần AES-GCM encrypt/decrypt — độ trễ crypto < 10ms trên thiết bị di động hiện đại, "
        "không đáng kể so với độ trễ mạng (50–500ms trên 4G).")

    add_heading(doc, "2.4.5. Luồng WebRTC P2P (song song)", level=3)
    add_body(doc,
        "Song song với relay, ChatSession khởi tạo PeerConnectionManager để thử kết nối P2P trực tiếp:")
    add_bullets(doc, [
        "Initiator tạo RTCPeerConnection, add DataChannel 'chat', createOffer() → emit webrtc-offer qua signaling.",
        "Responder nhận offer → setRemoteDescription → createAnswer() → emit webrtc-answer.",
        "Cả hai bên trao đổi ice-candidate qua signaling server.",
        "STUN (stun.l.google.com:19302) giúp discovery địa chỉ srflx candidate.",
        "Khi PeerConnectionState.connected: ChatSession chuyển mode sang p2p; tin gửi qua DataChannel (plaintext "
        "trên kênh đã mã hóa DTLS của WebRTC — lớp bảo vệ khác với E2E application layer).",
        "Nếu timeout (p2pConnectTimeout): giữ nguyên relay mode — đảm bảo UX không bị chặn.",
    ])
    add_body(doc,
        "Lưu ý thiết kế: trên 4G thực tế, P2P thường thất bại do symmetric NAT. Relay E2E vẫn là "
        "phương án chính; P2P là tối ưu hóa khi môi trường WiFi/LAN cho phép. Cả hai đều không "
        "làm server lưu tin nhắn ở chế độ mặc định.")

    add_heading(doc, "2.4.6. Chiến lược relay-first", level=3)
    add_body(doc,
        "Em thiết kế chiến lược relay-first dựa trên nguyên tắc availability-over-purity: "
        "người dùng phải chat được ngay, không cần đợi P2P handshake (có thể mất 10–30 giây hoặc thất bại).")
    add_table(doc,
        ["Giai đoạn", "ChatTransportMode", "Hành vi"],
        [
            ["Khởi tạo ChatSession", "connecting → relay", "Bật relay ngay; bắt đầu P2P song song"],
            ["P2P thành công", "p2p", "Ưu tiên gửi qua DataChannel; fallback relay nếu send fail"],
            ["P2P thất bại/timeout", "relay", "Tiếp tục relay E2E — trạng thái ổn định trên 4G"],
            ["P2P init error", "relay", "Bắt lỗi, log debug, không chặn người dùng"],
        ],
    )

    # ══════════════════════════════════════════════════════════════════
    # 2.5 THIẾT KẾ CẤU TRÚC CHƯƠNG TRÌNH
    # ══════════════════════════════════════════════════════════════════
    add_heading(doc, "2.5. Thiết kế cấu trúc chương trình", level=2)
    add_body(doc,
        "Kiến trúc phần mềm được thiết kế theo mô hình phân tầng (layered architecture) trên client "
        "và mô hình module hóa (modular) trên server. Nguyên tắc: separation of concerns — "
        "mỗi module có trách nhiệm duy nhất, giao tiếp qua interface rõ ràng.")

    add_heading(doc, "2.5.1. Flutter App — kiến trúc phân tầng", level=3)
    _insert_diagram(doc, add_caption, add_diagram, add_image, "hinh_2_5_cau_truc_flutter")
    add_table(doc,
        ["Tầng", "Module / File", "Trách nhiệm", "Phụ thuộc"],
        [
            ["Presentation", "login_screen, room_screen, chat_screen", "UI, input validation, hiển thị", "AppState, Services"],
            ["Navigation", "auth_gate.dart", "Điều hướng Login ↔ Room theo isLoggedIn", "AppState"],
            ["State Management", "app_state.dart (ChangeNotifier)", "Session, phòng, demo flags, chat map", "Services"],
            ["Domain / Chat", "chat_session.dart", "Orchestrate E2E + transport mode", "Crypto, Signaling, WebRTC"],
            ["Domain / Crypto", "e2e_crypto.dart", "X25519, HKDF, AES-GCM", "cryptography package"],
            ["Domain / WebRTC", "peer_connection_manager.dart", "RTCPeerConnection, DataChannel", "flutter_webrtc"],
            ["Infrastructure", "signaling_service.dart", "Socket.IO client wrapper", "socket_io_client"],
            ["Infrastructure", "auth_service.dart", "HTTP register/login", "http package"],
            ["Infrastructure", "local_db_service.dart", "SQLite CRUD", "sqflite"],
            ["Infrastructure", "demo_service.dart", "POST demo settings", "http package"],
            ["Config", "app_config.dart", "Server URL, STUN, timeout", "—"],
        ],
    )
    add_body(doc,
        "Phân tích từng module quan trọng:")
    add_body(doc,
        "app_state.dart đóng vai trò trung tâm điều phối (Mediator pattern). Nó giữ: AuthSession (token, "
        "keyPair, username), roomCode hiện tại, Map<String, ChatSession> cho mỗi peer, và cờ demo settings. "
        "UI layer chỉ đọc/ghi qua AppState, không gọi trực tiếp socket hay crypto — giảm coupling.")
    add_body(doc,
        "chat_session.dart encapsulate toàn bộ logic phiên chat 1-1: derive key, chọn transport, "
        "gửi/nhận, chuyển mode. ChatScreen chỉ gọi session.sendMessage() và lắng nghe onIncomingMessage — "
        "tuân thủ Single Responsibility Principle.")
    add_body(doc,
        "e2e_crypto.dart là pure static class — không side effect, dễ unit test. Tách biệt crypto "
        "khỏi networking là best practice: nếu sau này đổi transport (MQTT, QUIC…), crypto layer không đổi.")

    add_heading(doc, "2.5.2. Signaling Server — kiến trúc module", level=3)
    _insert_diagram(doc, add_caption, add_diagram, add_image, "hinh_2_6_cau_truc_server")
    add_table(doc,
        ["Module", "File / Thư mục", "Trách nhiệm"],
        [
            ["Entry point", "server.js", "Express app, HTTPS, mount routes, init Socket.IO"],
            ["Auth routes", "routes/auth.js", "POST /api/register, /api/login — JWT, bcrypt"],
            ["Demo routes", "routes/demo.js", "POST /api/demo/settings, GET /health"],
            ["Socket handlers", "socket/handlers.js", "authenticate, join-room, e2e-message, webrtc-*"],
            ["User store", "store/userStore.js", "users.json CRUD, online status, socketId mapping"],
            ["Room store", "store/roomStore.js", "roomCode ↔ members, normalize, areInSameRoom"],
            ["Message store", "store/messageStore.js", "In-memory demo messages (chỉ khi bật demo)"],
            ["Demo settings", "store/demoSettings.js", "storeMessagesOnServer, storePlaintextOnServer flags"],
            ["Health page", "healthPage.js", "HTML dashboard cho /health"],
        ],
    )
    add_body(doc,
        "Thiết kế store tách biệt (in-memory + file JSON) thay vì database quan hệ — phù hợp quy mô "
        "đề tài (vài chục user demo). userStore đọc/ghi users.json đồng bộ; roomStore và messageStore "
        "hoàn toàn in-memory, mất khi restart server (chấp nhận được vì không lưu tin mặc định).")
    add_body(doc,
        "handlers.js triển khai kiểm soát truy cập ở tầng socket: mọi event nhạy cảm đều kiểm tra "
        "currentUser và canTalk() trước khi relay. Đây là lớp authorization bổ sung cho authentication JWT.")

    add_heading(doc, "2.5.3. Các mẫu thiết kế áp dụng", level=3)
    add_table(doc,
        ["Mẫu thiết kế", "Vị trí áp dụng", "Lợi ích"],
        [
            ["Layered Architecture", "Flutter app (UI → State → Domain → Infra)", "Tách biệt concerns, dễ bảo trì"],
            ["Mediator", "AppState điều phối UI và services", "Giảm coupling giữa screens"],
            ["Strategy", "ChatTransportMode: p2p vs relay", "Chuyển đổi transport runtime"],
            ["Observer", "ChangeNotifier (AppState), Stream (modeStream)", "UI reactive cập nhật"],
            ["Singleton (de facto)", "LocalDbService, SignalingService", "Một instance kết nối/DB"],
            ["Fail-secure", "Server từ chối event khi chưa auth", "Không relay ẩn danh"],
        ],
    )

    # ══════════════════════════════════════════════════════════════════
    # 2.6 SEQUENCE DIAGRAM
    # ══════════════════════════════════════════════════════════════════
    add_heading(doc, "2.6. Biểu đồ trình tự — bắt đầu phiên chat", level=2)
    add_body(doc,
        "Biểu đồ trình tự (Sequence Diagram) mô tả tương tác theo thời gian giữa User A, App A, "
        "Signaling Server, App B và User B khi bắt đầu chat. Hình 2.7 thể hiện các message "
        "theo thứ tự chronology:")
    _insert_diagram(doc, add_caption, add_diagram, add_image, "hinh_2_7_sequence_chat")
    add_body(doc,
        "Phân tích sequence: sau khi cả hai user đã join-room và thấy nhau trong lobby, User A chọn "
        "peer B để mở ChatScreen. App A tạo ChatSession(isInitiator=true), derive shared secret, "
        "bật relay mode. Đồng thời emit webrtc-offer cho B. App B nhận offer (hoặc tự tạo session "
        "khi user mở chat), derive cùng shared secret (tính chất đối xứng ECDH). Khi A gửi tin, "
        "luồng e2e-message đi qua server trong < 1 round-trip. Server không giải mã payload.")

    # ══════════════════════════════════════════════════════════════════
    # 2.7 THIẾT KẾ CSDL
    # ══════════════════════════════════════════════════════════════════
    add_heading(doc, "2.7. Thiết kế cơ sở dữ liệu", level=2)
    add_body(doc,
        "Hệ thống áp dụng mô hình lưu trữ lai: dữ liệu nhạy cảm (tin nhắn) lưu local-first trên client; "
        "server chỉ lưu metadata tối thiểu phục vụ xác thực và ghép phòng.")

    add_heading(doc, "2.7.1. SQLite local (client)", level=3)
    _insert_diagram(doc, add_caption, add_diagram, add_image, "hinh_2_8_csdl_local")
    add_body(doc,
        "Database file: secure_p2p_chat.db trong thư mục databases của app (sandboxed trên Android/iOS). "
        "Schema version 1, tạo bởi onCreate callback của sqflite.")
    add_table(doc,
        ["Bảng", "Cột", "Kiểu", "Ràng buộc", "Mô tả"],
        [
            ["messages", "id", "INTEGER", "PK, AUTOINCREMENT", "Khóa chính"],
            ["messages", "peer_username", "TEXT", "NOT NULL", "Username đối tác chat"],
            ["messages", "content", "TEXT", "NOT NULL", "Nội dung plaintext (đã giải mã)"],
            ["messages", "is_mine", "INTEGER", "NOT NULL", "1 = tin gửi, 0 = tin nhận"],
            ["messages", "timestamp", "INTEGER", "NOT NULL", "Unix epoch milliseconds"],
            ["messages", "encrypted", "INTEGER", "DEFAULT 1", "Cờ E2E (luôn 1 trong đề tài)"],
            ["conversations", "peer_username", "TEXT", "PK", "Username đối tác"],
            ["conversations", "last_message", "TEXT", "", "Tin nhắn cuối (preview)"],
            ["conversations", "last_timestamp", "INTEGER", "", "Thời điểm tin cuối"],
        ],
    )
    add_body(doc,
        "Thiết kế hai bảng messages + conversations tách biệt: messages lưu toàn bộ lịch sử chi tiết; "
        "conversations là bảng tổng hợp (denormalized) phục vụ hiển thị danh sách hội thoại nhanh "
        "mà không cần GROUP BY trên messages. Khi saveMessage(), app insert cả hai bảng trong "
        "cùng transaction logic (insert + upsert conflictAlgorithm.replace).")
    add_body(doc,
        "Lưu ý bảo mật: content lưu plaintext sau giải mã — đây là chủ đích (local-first). "
        "Dữ liệu được bảo vệ bởi sandbox OS (Android Keystore/iOS Data Protection). "
        "Nếu cần bảo vệ cao hơn trong tương lai: mã hóa SQLite bằng SQLCipher với key dẫn xuất từ PIN sinh trắc học.")

    add_heading(doc, "2.7.2. Server — users.json và messageStore", level=3)
    add_body(doc,
        "Server không sử dụng database quan hệ. Cấu trúc lưu trữ gồm hai phần:")
    add_table(doc,
        ["Kho", "Kiểu", "Cấu trúc", "Khi nào dùng"],
        [
            ["users.json", "File JSON persistent", "{username, passwordHash, publicKey, createdAt, id}", "Luôn — auth"],
            ["roomStore", "In-memory Map", "roomCode → Set<username>", "Runtime — ghép phòng"],
            ["messageStore", "In-memory Array", "{from, to, content, encrypted, timestamp}", "Chỉ khi demo bật"],
            ["demoSettings", "In-memory Object", "{storeMessagesOnServer, storePlaintextOnServer}", "Runtime — demo"],
        ],
    )
    add_body(doc,
        "Thiết kế cố ý không có bảng messages persistent trên server. messageStore chỉ ghi khi "
        "demoSettings.storeMessagesOnServer = true — phục vụ minh họa trước hội đồng, không phải "
        "chế độ production. Khi server restart, messageStore và roomStore reset — tin nhắn demo mất, "
        "users.json vẫn giữ (tài khoản không mất).")

    # ══════════════════════════════════════════════════════════════════
    # 2.8 SOCKET.IO PROTOCOL
    # ══════════════════════════════════════════════════════════════════
    add_heading(doc, "2.8. Thiết kế giao thức Socket.IO", level=2)
    add_body(doc,
        "Socket.IO được chọn vì hỗ trợ realtime bidirectional, auto-reconnect, fallback polling, "
        "và room abstraction sẵn có. Giao thức ứng dụng định nghĩa các event sau:")

    add_heading(doc, "2.8.1. Bảng event Socket.IO", level=3)
    add_table(doc,
        ["Event", "Hướng", "Payload", "Điều kiện", "Mô tả"],
        [
            ["authenticate", "C→S", "{token: string}", "Sau khi connect", "Gắn socket với user JWT"],
            ["authenticated", "S→C", "{user: object}", "Token hợp lệ", "Xác nhận auth thành công"],
            ["auth-error", "S→C", "{message: string}", "Token invalid", "Từ chối phiên"],
            ["join-room", "C→S", "{roomCode: string}", "Đã auth", "Tham gia phòng"],
            ["room-joined", "S→C", "{roomCode, users[]}", "Join OK", "Trả danh sách peer"],
            ["room-error", "S→C", "{message: string}", "Mã < 4 ký tự", "Lỗi validation"],
            ["room-users", "S→C", "{roomCode, users[]}", "Broadcast", "Cập nhật lobby"],
            ["user-joined-room", "S→C", "{roomCode, user}", "Peer mới vào", "Thông báo cho phòng"],
            ["user-left-room", "S→C", "{username, roomCode}", "Peer rời/disconnect", "Cập nhật lobby"],
            ["leave-room", "C→S", "{}", "Đã auth", "Rời phòng chủ động"],
            ["e2e-message", "C→S→C", "{to, payload, demoPlaintext?}", "Cùng phòng", "Relay ciphertext"],
            ["webrtc-offer", "C→S→C", "{to, offer}", "Cùng phòng", "SDP offer"],
            ["webrtc-answer", "C→S→C", "{to, answer}", "Cùng phòng", "SDP answer"],
            ["ice-candidate", "C→S→C", "{to, candidate}", "Cùng phòng", "ICE candidate"],
        ],
    )

    add_heading(doc, "2.8.2. Ví dụ payload JSON", level=3)
    add_body(doc, "Ví dụ event e2e-message từ client gửi lên server:")
    add_bullets(doc, [
        'Request (C→S): { "to": "user2", "payload": "{\\"n\\":\\"abc=\\",\\"c\\":\\"xyz=\\",\\"m\\":\\"mac=\\"}", '
        '"demoPlaintext": null }',
        'Relay (S→C): { "from": "user1", "payload": "{\\"n\\":\\"abc=\\",\\"c\\":\\"xyz=\\",\\"m\\":\\"mac=\\"}" }',
    ])
    add_body(doc,
        "Server chỉ đọc trường to (để routing) và payload (để forward). Trường demoPlaintext chỉ "
        "được xử lý khi demoSettings.storePlaintextOnServer = true — trường hợp minh họa rủi ro, "
        "không phải luồng E2E thông thường.")

    add_heading(doc, "2.8.3. REST API bổ trợ", level=3)
    add_table(doc,
        ["Method", "Endpoint", "Body", "Response", "Mô tả"],
        [
            ["POST", "/api/register", "{username, password, publicKey}", "201 + {token, user}", "Đăng ký"],
            ["POST", "/api/login", "{username, password}", "200 + {token, user}", "Đăng nhập"],
            ["POST", "/api/demo/settings", "{storeMessagesOnServer, storePlaintextOnServer}", "200", "Cấu hình demo"],
            ["GET", "/health", "—", "HTML dashboard", "Trạng thái server + tin demo"],
        ],
    )

    # ══════════════════════════════════════════════════════════════════
    # 2.9 DEMO MODULE
    # ══════════════════════════════════════════════════════════════════
    add_heading(doc, "2.9. Thiết kế module thực nghiệm và đánh giá (Demo hội đồng)", level=2)

    add_heading(doc, "2.9.1. Mục tiêu và chức năng của module", level=3)
    add_body(doc,
        "Module này được thiết kế nhằm mục đích kiểm thử độc lập và trình diễn trực quan khả năng bảo mật "
        "của hệ thống Secure P2P Chat trước Hội đồng chấm khóa luận. Chức năng cốt lõi của module là cung cấp "
        "một dashboard đối sánh thời gian thực (real-time) giữa cơ chế mã hóa đầu cuối (End-to-End Encryption — E2EE) "
        "và mô hình kiến trúc máy chủ truyền thống không mã hóa.")
    add_body(doc,
        "Thông qua việc giả lập các kịch bản cấu hình lưu trữ tại máy chủ, module chứng minh rằng dữ liệu khi "
        "đi qua hoặc lưu tại server trung gian trong kiến trúc E2EE hoàn toàn là các chuỗi ciphertext ngẫu nhiên "
        "(dạng JSON Base64 chứa nonce, cipher text và MAC), không thể bị khai thác hay đọc hiểu bởi quản trị viên "
        "hệ thống hoặc bên thứ ba. Ngược lại, khi bật chế độ lưu plaintext có chủ đích, module mô phỏng rủi ro "
        "của các nền tảng chat server truyền thống (Zalo, Messenger…) — nơi hacker chiếm database có thể đọc "
        "trực tiếp nội dung hội thoại.")
    add_body(doc,
        "Về mặt kiến trúc, module demo được triển khai trên cả hai phía client và server, tách biệt khỏi "
        "luồng nghiệp vụ chat chính để không ảnh hưởng chế độ vận hành mặc định (privacy by design):")
    add_table(doc,
        ["Thành phần", "File / Module", "Vai trò"],
        [
            ["Client UI", "demo_settings_sheet.dart", "Giao diện bật/tắt chế độ demo, copy URL /health"],
            ["Client Service", "demo_service.dart", "Gọi REST API cấu hình demo từ app"],
            ["Server Store", "demoSettings.js, messageStore.js", "Lưu cờ cấu hình và log tin nhắn in-memory"],
            ["Server Handler", "handlers.js (e2e-message)", "Ghi log khi demo bật, relay ciphertext như bình thường"],
            ["Dashboard", "healthPage.js", "Render HTML/JSON giám sát tại GET /health"],
        ],
    )
    add_body(doc,
        "Ba chế độ vận hành của module được thiết kế để phục vụ lần lượt các mục tiêu trình diễn:")
    add_table(doc,
        ["Chế độ", "storeMessagesOnServer", "storePlaintextOnServer", "Server lưu", "Đọc được?", "Mục đích demo"],
        [
            ["Mặc định (E2E)", "false", "false", "Không lưu tin", "—",
             "Chứng minh privacy by design — messagesStored = 0"],
            ["Lưu ciphertext", "true", "false", "Blob JSON mã hóa", "Không (E2E)",
             "Chứng minh E2E ngay cả khi server lưu dữ liệu"],
            ["Lưu plaintext", "true", "true", "Nội dung gốc", "Có (plaintext demo)",
             "Đối chứng rủi ro chat server truyền thống"],
        ],
    )

    add_heading(doc, "2.9.2. Đặc tả các cổng giao tiếp API (API Endpoints)", level=3)
    add_body(doc,
        "Hệ thống triển khai hai nhóm phương thức giao tiếp chính phục vụ riêng cho module thực nghiệm: "
        "(1) API cấu hình trạng thái lưu trữ trên server; (2) API truy xuất dữ liệu giám sát hệ thống.")

    add_heading(doc, "API cấu hình trạng thái lưu trữ — POST /api/demo/settings", level=3)
    add_body(doc,
        "Endpoint: POST /api/demo/settings\n"
        "Mục đích: Thay đổi động hành vi lưu trữ tin nhắn trên máy chủ để phục vụ kịch bản demo kiểm thử.")
    add_body(doc, "Cấu trúc dữ liệu yêu cầu (Request Body — JSON):")
    add_bullets(doc, [
        'storeMessagesOnServer (boolean): Bật/tắt quyền lưu trữ gói tin trên server.',
        'storePlaintextOnServer (boolean): Bật/tắt việc cố tình lưu bản rõ (chỉ dùng để đối chứng).',
        'clearMessages (boolean, tùy chọn): Xóa toàn bộ log tin nhắn demo trên messageStore.',
    ])
    add_body(doc, "Ví dụ request body:")
    add_bullets(doc, [
        '{ "storeMessagesOnServer": true, "storePlaintextOnServer": false }',
        '{ "storeMessagesOnServer": true, "storePlaintextOnServer": true }',
        '{ "clearMessages": true }',
    ])
    add_body(doc,
        "Nguyên lý hoạt động: Khi cấu hình storePlaintextOnServer nhận giá trị true, máy chủ sẽ thử nghiệm "
        "ghi lại dữ liệu thô nhận được từ client (trường demoPlaintext trong event e2e-message) để chứng minh "
        "tính năng bảo mật — nếu là kết nối truyền thống thì thấy bản rõ, nếu là E2EE thì chỉ thấy bản mã. "
        "Khi storeMessagesOnServer = false, server không ghi messageStore dù client vẫn relay ciphertext bình thường.")
    add_table(doc,
        ["Thuộc tính", "Giá trị"],
        [
            ["Phương thức", "POST"],
            ["Content-Type", "application/json"],
            ["Response", "200 OK + {storeMessagesOnServer, storePlaintextOnServer}"],
            ["Gọi từ", "DemoService.updateSettings() trên Flutter app"],
        ],
    )
    add_body(doc,
        "Bổ sung: GET /api/demo/settings trả về trạng thái cấu hình hiện tại — dùng khi app mở lại "
        "để đồng bộ toggle với server.")

    add_heading(doc, "API truy xuất dữ liệu giám sát — GET /health", level=3)
    add_body(doc,
        "Endpoint: GET /health\n"
        "Mục đích: Trả về giao diện trực quan giám sát các gói tin đang đi qua hoặc được lưu trữ tại "
        "bộ nhớ đệm (in-memory) của máy chủ.")
    add_table(doc,
        ["Tham số / Biến thể", "Kiểu phản hồi", "Mô tả"],
        [
            ["GET /health", "text/html", "Dashboard HTML động cho hội đồng chiếu màn hình"],
            ["GET /health?format=json", "application/json", "Dữ liệu máy đọc: status, messagesStored, demo, messages[]"],
        ],
    )
    add_body(doc,
        "Cấu trúc JSON phản hồi (buildHealthJson): { status, totalUsers, onlineUsers, messagesStored, "
        "demo: {storeMessagesOnServer, storePlaintextOnServer}, messages: [...] }. "
        "Khi demo tắt, messagesStored luôn trả về 0 và mảng messages rỗng — phản ánh đúng chế độ production.")

    add_heading(doc, "2.9.3. Thiết kế giao diện Dashboard đối sánh trực quan (GET /health)", level=3)
    add_body(doc,
        "Giao diện giám sát được thiết kế dưới dạng bảng quản trị (HTML Dashboard) tối giản, cập nhật trạng thái "
        "động khi hội đồng refresh trình duyệt. Module healthPage.js render trang HTML gồm các vùng thông tin sau:")
    add_bullets(doc, [
        "Thẻ thống kê (cards): Trạng thái server (OK), số tài khoản, số user online, số tin nhắn lưu trên server.",
        "Badge cấu hình demo: Hiển thị BẬT/TẮT cho storeMessagesOnServer và storePlaintextOnServer.",
        "Khung ghi chú (note): Giải thích ba chế độ — mặc định E2E, lưu ciphertext, lưu plaintext.",
        "Bảng đối chứng tin nhắn: Liệt kê từng gói tin đã ghi vào messageStore khi demo bật.",
    ])
    add_body(doc,
        "Bảng tin nhắn trên server được thiết kế với các cột kiểm thử sau:")
    add_table(doc,
        ["Tên cột", "Kiểu dữ liệu", "Mô tả chức năng"],
        [
            ["#", "Integer", "Số thứ tự bản ghi trong messageStore"],
            ["Từ (From)", "String", "Username người gửi (định danh client)"],
            ["Đến (To)", "String", "Username người nhận (định danh đích)"],
            ["Thời gian", "DateTime", "Timestamp lúc server nhận gói tin"],
            ["Nội dung server thấy (Server Content)", "String (JSON/Base64)",
             "Dữ liệu thực tế server lưu: bản rõ (plaintext demo) hoặc chuỗi mã hóa (E2EE)"],
            ["Đọc được? (Readable?)", "Label / Boolean",
             "CÓ — nếu server đọc được nội dung (plaintext demo); "
             "KHÔNG (E2E) — nếu chỉ thấy ciphertext"],
        ],
    )
    add_body(doc,
        "Trên giao diện client, DemoSettingsSheet cung cấp hai SwitchListTile tương ứng hai cờ cấu hình, "
        "kèm URL /health có thể copy để hội đồng mở trên laptop. Nút \"Xóa log server\" gọi "
        "POST /api/demo/settings với clearMessages=true — reset messageStore trước mỗi lượt trình diễn.")
    add_body(doc,
        "Luồng trình diễn đề xuất trước hội đồng: (1) Mở /health — xác nhận messagesStored = 0; "
        "(2) Hai điện thoại chat ở chế độ mặc định — refresh /health vẫn 0; (3) Bật lưu ciphertext — "
        "chat thêm — /health hiện blob mã hóa, cột Đọc được? = Không; (4) Bật thêm plaintext — "
        "so sánh rủi ro; (5) Tắt demo — nhấn mạnh chế độ thực của sản phẩm.")

    # ══════════════════════════════════════════════════════════════════
    # 2.10 KẾT LUẬN CHƯƠNG
    # ══════════════════════════════════════════════════════════════════
    add_heading(doc, "2.10. Kết luận chương", level=2)
    add_body(doc,
        "Chương 2 đã hoàn thành giai đoạn phân tích và thiết kế hệ thống Secure P2P Chat một cách "
        "toàn diện. Mục 2.1 phân tích bài toán từ góc độ thực tế, xác định 9 yêu cầu chức năng (FR01–FR09), "
        "10 yêu cầu phi chức năng (NFR01–NFR10), các ràng buộc mạng/hạ tầng/phạm vi, và đề xuất "
        "kiến trúc lai Flutter + Signaling Server + chiến lược relay-first.")
    add_body(doc,
        "Mục 2.2 và 2.3 xác định ba tác nhân chính, phân tích ranh giới tin cậy, và mô tả chi tiết "
        "bảy use case (UC01–UC07) với tiền điều kiện, luồng chính, luồng phụ và hậu điều kiện. "
        "Mục 2.4 trình bày sáu luồng dữ liệu: đăng ký, đăng nhập, vào phòng, gửi tin E2E relay, "
        "WebRTC P2P song song, và chiến lược relay-first — đảm bảo plaintext chỉ tồn tại trên thiết bị client.")
    add_body(doc,
        "Mục 2.5 phân rã kiến trúc phần mềm thành 11 module Flutter và 9 module Node.js, áp dụng "
        "các mẫu thiết kế Layered Architecture, Mediator, Strategy và Fail-secure. "
        "Mục 2.6 bổ sung biểu đồ trình tự cho quy trình bắt đầu phiên chat. "
        "Mục 2.7 thiết kế schema SQLite (2 bảng messages/conversations) và mô hình lưu trữ server "
        "local-first (users.json, không bảng messages mặc định). "
        "Mục 2.8 quy định 14 event Socket.IO và 4 REST endpoint. "
        "Mục 2.9 thiết kế module thực nghiệm và đánh giá (Demo hội đồng) với mục tiêu, đặc tả API "
        "(POST /api/demo/settings, GET /health) và dashboard đối sánh trực quan ba chế độ E2E.")
    add_body(doc,
        "Như vậy, Chương 2 đã chuyển hóa nền tảng lý thuyết Chương 1 thành bản thiết kế cụ thể, "
        "có thể triển khai và kiểm thử được. Chương 3 sẽ trình bày quá trình cài đặt mã nguồn, "
        "triển khai trên Render, thực hiện bảy kịch bản kiểm thử và đánh giá mức độ đáp ứng "
        "các yêu cầu FR/NFR đã đề ra.")
    add_page_break(doc)
