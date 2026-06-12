---
title: "Pattern trong React"
description: "Cách React kết hợp bitmask, double buffering, cooperative scheduling, min heap và diff/patch trong một chu trình render duy nhất."
---

# Pattern trong React

Reconciler của React là một lớp học mẫu mực về cách kết hợp các pattern cấp thấp. Năm pattern đầu tiên xuất hiện trong cùng một chu trình render.

## Pattern trong chu trình render

| Pattern | Ở đâu trong React | Tác dụng |
|---------|---------------|--------------|
| [Bitmask](/patterns/bitmask/) | [`ReactFiberFlags.js`](https://github.com/facebook/react/blob/34b78a2897cc208260a88e6b62ecaf9ca2a9dfe4/packages/react-reconciler/src/ReactFiberFlags.js#L14-L36) | Flag tác động phụ trên node fiber |
| [Double Buffering](/patterns/double-buffering/) | [Fiber `current` / `alternate`](https://github.com/facebook/react/blob/34b78a2897cc208260a88e6b62ecaf9ca2a9dfe4/packages/react-reconciler/src/ReactFiber.js#L327-L355) | Hoán đổi cây nguyên tử khi reconciliation |
| [Cooperative Scheduling](/patterns/cooperative-scheduling/) | [`workLoopConcurrent`](https://github.com/facebook/react/blob/34b78a2897cc208260a88e6b62ecaf9ca2a9dfe4/packages/scheduler/src/forks/Scheduler.js#L188-L258) | Yield mỗi 5ms để giữ UI phản hồi |
| [Min Heap](/patterns/min-heap/) | [`SchedulerMinHeap.js`](https://github.com/facebook/react/blob/34b78a2897cc208260a88e6b62ecaf9ca2a9dfe4/packages/scheduler/src/SchedulerMinHeap.js#L17-L90) | Hàng đợi ưu tiên cho task đã lập lịch |
| [Diff / Patch](/patterns/diff-patch/) | [`ReactChildFiber.js`](https://github.com/facebook/react/blob/34b78a2897cc208260a88e6b62ecaf9ca2a9dfe4/packages/react-reconciler/src/ReactChildFiber.js#L1169-L1340) | Reconcile danh sách con cũ và mới |

### Cách chúng kết hợp: Một chu trình render

Khi bạn gọi `setState`, cả năm pattern bắn theo thứ tự:

<CompositionFlow variant="react-render" />

Insight then chốt: **các pattern này không phải tính năng độc lập — chúng tạo thành một pipeline.** Heap quyết định *cái gì* để render, cooperative scheduling quyết định *khi nào* render, diff/patch quyết định *cái gì đã đổi*, bitmask mã hoá *nó đổi như thế nào* và double buffering đảm bảo hoán đổi là nguyên tử.

Xem [Liên kết giữa các pattern](/guide/pattern-connections) để có sơ đồ kết hợp tương tác đầy đủ.

## Thêm pattern trong React

| Pattern | Ở đâu trong React | Tác dụng |
|---------|---------------|--------------|
| [Batch Processing](/patterns/batch-processing/) | `unstable_batchedUpdates` | Nhiều cuộc gọi `setState` được gom vào một lần re-render |
| [Dirty Flag](/patterns/dirty-flag/) | [`ReactFiberFlags.js`](https://github.com/facebook/react/blob/34b78a2897cc208260a88e6b62ecaf9ca2a9dfe4/packages/react-reconciler/src/ReactFiberFlags.js#L18-L22) | Flag fiber (`Placement`, `Update`, `Deletion`) đánh dấu subtree cần xử lý |
| [Observer](/patterns/observer/) | Mẫu cleanup `useEffect` | Đăng ký khi mount, huỷ đăng ký khi cleanup — quan sát state tách rời |

## Đọc thêm

- [Source React (GitHub)](https://github.com/facebook/react)
- [Kiến trúc React Fiber](https://github.com/acdlite/react-fiber-architecture)
