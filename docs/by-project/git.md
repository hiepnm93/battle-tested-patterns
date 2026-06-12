---
title: "Pattern trong Git"
description: "Cách Git dùng pattern: object copy-on-write, Merkle tree cho toàn vẹn và diff/patch cho thay đổi tối thiểu."
---

# Pattern trong Git

Mô hình dữ liệu của Git được xây dựng trên các object bất biến copy-on-write và diff hiệu quả.

| Pattern | Ở đâu | Tác dụng |
|---------|-------|--------------|
| [Copy-on-Write](/patterns/copy-on-write/) | [`object-file.c`](https://github.com/git/git/blob/1ff279f3404a482a83fb04c7457e41ab26884aea/object-file.c#L719-L730) | Object bất biến địa chỉ-theo-nội-dung; các branch chia sẻ dữ liệu, chỉ copy khi đổi |
| [Diff / Patch](/patterns/diff-patch/) | [`diff.c`](https://github.com/git/git/blob/1ff279f3404a482a83fb04c7457e41ab26884aea/diff.c#L5020-L5060), `xdiff/` | Thuật toán diff Myers cho khoảng cách chỉnh sửa tối thiểu giữa các phiên bản file |
| [Bitmask](/patterns/bitmask/) | [`read-cache-ll.h`](https://github.com/git/git/blob/1ff279f3404a482a83fb04c7457e41ab26884aea/read-cache-ll.h) | Flag entry cache `CE_*` — staged, valid, intent-to-add |
| [Bloom Filter](/patterns/bloom-filter/) | [`bloom.c`](https://github.com/git/git/blob/1ff279f3404a482a83fb04c7457e41ab26884aea/bloom.c) | Bloom filter cho đường dẫn đã đổi, giúp `git log -- <path>` nhanh hơn |
| [Trie](/patterns/trie/) | [`read-cache.c`](https://github.com/git/git/blob/1ff279f3404a482a83fb04c7457e41ab26884aea/read-cache.c) | Bảng hash tên cho tra cứu path cấp thư mục nhanh |
| [LRU Cache](/patterns/lru-cache/) | [`pack-objects.c`](https://github.com/git/git/blob/1ff279f3404a482a83fb04c7457e41ab26884aea/pack-objects.c) | Cache delta base để tái dùng delta đã tính khi pack |
| [Merkle Tree](/patterns/merkle-tree/) | [`tree.c`](https://github.com/git/git/blob/1ff279f3404a482a83fb04c7457e41ab26884aea/tree.c#L136-L171) | DAG Merkle địa chỉ-theo-nội-dung — mỗi commit, tree, blob đều được hash; đổi một byte là đổi tất cả hash lên tới root |

## Cách chúng kết hợp: `git commit`

Khi bạn chạy `git commit`, nhiều pattern phối hợp để tạo một snapshot bất biến và có thể xác minh:

<CompositionFlow variant="git-commit" />

Insight cốt lõi là copy-on-write + hash Merkle cho Git vừa hiệu quả không gian (object dùng chung) vừa xác minh được toàn vẹn (hash bất khả giả mạo) mà không phải đánh đổi cái này lấy cái kia.

## Đọc thêm

- [Source Git (GitHub)](https://github.com/git/git)
