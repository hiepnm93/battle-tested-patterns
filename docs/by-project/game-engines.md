---
title: "Pattern trong Game Engine"
description: "Pattern game engine từ Godot và SDL: object pool, tagged union, double buffering và dirty flag cho hiệu năng 60fps."
---

# Pattern trong Game Engine

Game engine đẩy các pattern tới giới hạn — mỗi frame đều quan trọng khi chạy 60fps.

| Pattern | Dự án | Ở đâu | Tác dụng |
|---------|---------|-------|--------------|
| [Object Pool](/patterns/object-pool/) | Godot | [`core/templates/pooled_list.h`](https://github.com/godotengine/godot/blob/ec67cbe92628bdaf979b10594359ba6f02cf8838/core/templates/pooled_list.h#L35-L100) | Pool dựa trên freelist cho entity, particle, physics body |
| [Double Buffering](/patterns/double-buffering/) | SDL | [`src/render/SDL_render.c`](https://github.com/libsdl-org/SDL/blob/14b0e9d922da78001223e563efd2f54f473a4115/src/render/SDL_render.c#L5535-L5570) | Hoán đổi front/back buffer cho render không tearing |
| [Free List](/patterns/free-list/) | Godot | [`core/templates/pooled_list.h`](https://github.com/godotengine/godot/blob/ec67cbe92628bdaf979b10594359ba6f02cf8838/core/templates/pooled_list.h#L35-L100) | Allocator freelist không xen cho cấp/giải phóng entity O(1) |
| [Ring Buffer](/patterns/ring-buffer/) | Audio game | Nhiều engine | Buffer streaming audio lock-free giữa main thread và audio thread |
| [State Machine](/patterns/state-machine/) | Godot | [`scene/animation/animation_tree.h`](https://github.com/godotengine/godot/blob/ec67cbe92628bdaf979b10594359ba6f02cf8838/scene/animation/animation_tree.h) | State machine animation cho blending hoạt cảnh nhân vật |
| [Arena Allocator](/patterns/arena-allocator/) | Frame allocator | Pattern phổ biến | Bump allocator mỗi frame — reset mỗi frame, chi phí giải phóng bằng 0 |
| [Flyweight](/patterns/flyweight/) | Godot | [`servers/rendering/`](https://github.com/godotengine/godot/tree/ec67cbe92628bdaf979b10594359ba6f02cf8838/servers/rendering) | Tài nguyên mesh/texture chia sẻ được tham chiếu bởi nhiều instance |
| [Batch Processing](/patterns/batch-processing/) | Godot / Unity | Render batching | Gom các draw call để giảm tối đa thay đổi state GPU |
| [Tagged Union](/patterns/tagged-union/) | Godot | [`variant.h`](https://github.com/godotengine/godot/blob/ec67cbe92628bdaf979b10594359ba6f02cf8838/core/variant/variant.h#L78-L120) | Enum `Variant::Type` + union — mọi giá trị GDScript đều là một `Variant` |
| [Dirty Flag](/patterns/dirty-flag/) | Godot / Unity | Hệ transform | Dirty flag trên transform cha vô hiệu ma trận thế giới của con — tính lại chỉ khi truy cập |
| [Event Loop](/patterns/event-loop/) | Godot | [`main_loop.h`](https://github.com/godotengine/godot/blob/ec67cbe92628bdaf979b10594359ba6f02cf8838/core/os/main_loop.h) | Vòng lặp game chính — xử lý input, update, render theo chu kỳ bước cố định |

## Cách chúng kết hợp: Một frame game

Ở 60fps, mỗi frame có ~16ms. Nhiều pattern phối hợp trong khoảng thời gian đó:

<CompositionFlow variant="game-frame" />

Insight then chốt: game engine giảm tối đa overhead mỗi object. Pool tránh malloc, dirty flag tránh tính lại, batching tránh GPU call và arena tránh giải phóng từng object. Tất cả đều chia sẻ cùng triết lý thiết kế — trả O(1) mỗi thao tác, hoãn hoặc phân bổ công việc tốn kém.

## Đọc thêm

- [Godot Engine (GitHub)](https://github.com/godotengine/godot) · [SDL (GitHub)](https://github.com/libsdl-org/SDL)
- [Game Programming Patterns (sách)](https://gameprogrammingpatterns.com/) của Robert Nystrom
