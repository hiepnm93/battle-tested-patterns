---
title: "Pattern: Registry / Tự đăng ký"
description: "Thành phần tự đăng ký vào bảng tra cứu toàn cục theo tên — consumer khám phá triển khai lúc runtime không có phụ thuộc hardcode."
difficulty: "beginner"
---

# Pattern: Registry / Tự đăng ký

<DifficultyBadge />

## Mô tả một câu

Thành phần tự đăng ký vào bảng tra cứu toàn cục theo tên — consumer khám phá triển khai lúc runtime không có phụ thuộc hardcode.

<DemoBadge />

## Tương tự thực tế

Quầy lễ tân khách sạn. Khách check in với tên, và ai cũng có thể hỏi quầy 'Alice ở phòng nào?' Quầy không quan tâm chuyện gì xảy ra trong phòng — chỉ ánh xạ tên sang vị trí.

## Ý tưởng cốt lõi

Registry là map trung tâm từ tên (chuỗi) sang triển khai (hàm, class, factory). Producer tự đăng ký lúc khởi động — thường qua decorator, macro hoặc hàm init. Consumer tra cứu triển khai theo tên lúc runtime, loại bỏ ghép lúc compile. Điều này cho phép kiến trúc plugin nơi chức năng mới có thể thêm mà không sửa code có sẵn.

```text
  Đăng ký (khởi động):

  ┌──────────┐    register("json")    ┌────────────────────┐
  │ JsonCodec│─────────────────────►  │     Registry       │
  └──────────┘                        │                    │
  ┌──────────┐    register("xml")     │  "json" → JsonCodec│
  │ XmlCodec │─────────────────────►  │  "xml"  → XmlCodec │
  └──────────┘                        │  "csv"  → CsvCodec │
  ┌──────────┐    register("csv")     │                    │
  │ CsvCodec │─────────────────────►  └────────────────────┘
  └──────────┘
                                             │
  Tra cứu (runtime):                         │
                                             ▼
  ┌──────────┐    get("json")         ┌────────────┐
  │ Consumer │─────────────────────►  │ JsonCodec  │
  └──────────┘                        └────────────┘
```

| Thuộc tính | Giá trị |
|----------|-------|
| Register | O(1) — chèn hash map |
| Lookup | O(1) — get hash map |
| Ghép | Không phụ thuộc lúc compile giữa producer và consumer |
| Khả năng mở rộng | Thêm triển khai mới không sửa code có sẵn |

**Thử ngay** — đăng ký handler theo tên và tra cứu lúc runtime:

<RegistryViz />

## Bằng chứng production

| Dự án | Nguồn | Cách dùng |
|---------|--------|-------|
| TensorFlow | [op.h#L258-L290](https://github.com/tensorflow/tensorflow/blob/b4c7e9a660badf8c8c81075fe9f781d23ed6f28a/tensorflow/core/framework/op.h#L258-L290) | Macro `REGISTER_OP` đăng ký operation mới vào `OpRegistry` toàn cục. Mỗi op định nghĩa tên, input, output và hàm shape. Runtime tra cứu op theo tên khi xây computation graph, nên op mới có thể thêm không động vào executor graph. |
| gRPC-Go | [server.go#L154-L170](https://github.com/grpc/grpc-go/blob/f1864955bbb48efa131f6652933fa8b2189d9305/server.go#L154-L170) | `RegisterService` thêm mô tả service (method, hàm handler) vào map service của server. Khi RPC đến, server tra method trong registry này để dispatch tới handler đúng. Service tự đăng ký khi init. |

## Triển khai

::: code-group

```typescript [TypeScript]
type Factory<T> = (...args: any[]) => T;

class Registry<T> {
  private entries = new Map<string, Factory<T>>();

  register(name: string, factory: Factory<T>): void {
    if (this.entries.has(name)) {
      throw new Error(`"${name}" is already registered`);
    }
    this.entries.set(name, factory);
  }

  get(name: string): Factory<T> {
    const factory = this.entries.get(name);
    if (!factory) {
      throw new Error(`"${name}" is not registered`);
    }
    return factory;
  }

  create(name: string, ...args: any[]): T {
    return this.get(name)(...args);
  }

  has(name: string): boolean {
    return this.entries.has(name);
  }

  list(): string[] {
    return [...this.entries.keys()];
  }
}
```

```rust [Rust]
use std::collections::HashMap;

pub struct Registry<T> {
    entries: HashMap<String, Box<dyn Fn() -> T>>,
}

impl<T> Registry<T> {
    pub fn new() -> Self {
        Registry { entries: HashMap::new() }
    }

    pub fn register<F: Fn() -> T + 'static>(
        &mut self, name: &str, factory: F,
    ) -> Result<(), String> {
        if self.entries.contains_key(name) {
            return Err(format!("\"{}\" is already registered", name));
        }
        self.entries.insert(name.to_string(), Box::new(factory));
        Ok(())
    }

    pub fn create(&self, name: &str) -> Result<T, String> {
        self.entries.get(name)
            .map(|f| f())
            .ok_or_else(|| format!("\"{}\" is not registered", name))
    }

    pub fn has(&self, name: &str) -> bool {
        self.entries.contains_key(name)
    }

    pub fn list(&self) -> Vec<&str> {
        self.entries.keys().map(|s| s.as_str()).collect()
    }
}
```

```go [Go]
type Factory func(args ...any) any

type Registry struct {
	mu      sync.RWMutex
	entries map[string]Factory
}

func NewRegistry() *Registry {
	return &Registry{entries: make(map[string]Factory)}
}

func (r *Registry) Register(name string, factory Factory) error {
	r.mu.Lock()
	defer r.mu.Unlock()
	if _, ok := r.entries[name]; ok {
		return fmt.Errorf("%q is already registered", name)
	}
	r.entries[name] = factory
	return nil
}

func (r *Registry) Get(name string) (Factory, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()
	factory, ok := r.entries[name]
	if !ok {
		return nil, fmt.Errorf("%q is not registered", name)
	}
	return factory, nil
}

func (r *Registry) Create(name string, args ...any) (any, error) {
	factory, err := r.Get(name)
	if err != nil {
		return nil, err
	}
	return factory(args...), nil
}

func (r *Registry) Has(name string) bool {
	r.mu.RLock()
	defer r.mu.RUnlock()
	_, ok := r.entries[name]
	return ok
}

func (r *Registry) List() []string {
	r.mu.RLock()
	defer r.mu.RUnlock()
	names := make([]string, 0, len(r.entries))
	for name := range r.entries {
		names = append(names, name)
	}
	return names
}
```

```python [Python]
from typing import Any, Callable

class Registry:
    def __init__(self):
        self._entries: dict[str, Callable[..., Any]] = {}

    def register(self, name: str, factory: Callable[..., Any]) -> None:
        if name in self._entries:
            raise ValueError(f'"{name}" is already registered')
        self._entries[name] = factory

    def get(self, name: str) -> Callable[..., Any]:
        if name not in self._entries:
            raise KeyError(f'"{name}" is not registered')
        return self._entries[name]

    def create(self, name: str, *args: Any, **kwargs: Any) -> Any:
        return self.get(name)(*args, **kwargs)

    def has(self, name: str) -> bool:
        return name in self._entries

    def list(self) -> list[str]:
        return list(self._entries.keys())

    def decorator(self, name: str):
        """Dùng @registry.decorator("name") để tự đăng ký."""
        def wrapper(cls):
            self.register(name, cls)
            return cls
        return wrapper
```

:::

## Bài tập

| Cấp độ | Bài tập | File |
|-------|----------|------|
| Cơ bản | Triển khai registry có kiểu với register/get/list | `exercises/typescript/registry/01-basic.test.ts` |
| Trung bình | Thêm tự đăng ký qua decorator và kiểm tra dependency | `exercises/typescript/registry/02-intermediate.test.ts` |

Chạy bài tập: `pnpm test:exercises` (TypeScript) · `cargo test` (Rust) · `go test ./...` (Go) · `pytest` (Python)

File bài tập: Rust `exercises/rust/src/registry/mod.rs` · Go `exercises/go/registry/registry_test.go` · Python `exercises/python/registry/test_registry.py`

## Khi nào nên dùng

- **Hệ plugin** — nạp và khám phá plugin theo tên không ghép lúc compile
- **Codec serialize** — đăng ký codec JSON, XML, Protobuf; tra theo content-type
- **Dispatch command/handler** — command CLI, method RPC, event handler tự đăng ký
- **Fixture test** — đăng ký factory test theo tên cho test tham số
- **Op framework ML** — TensorFlow, PyTorch đăng ký operator có thể ghép vào graph

## Khi nào KHÔNG nên dùng

- **Ít triển khai cố định** — nếu chỉ 2-3 triển khai biết trước, switch/match đơn giản hơn
- **An toàn kiểu then chốt** — tra cứu dựa trên chuỗi mất kiểm tra kiểu lúc compile; dùng dependency injection hoặc generic
- **Thứ tự quan trọng** — registry thường không có thứ tự; nếu thứ tự init quan trọng, dùng tuần tự rõ ràng

## Thêm các ứng dụng production

- [Terraform](https://github.com/hashicorp/terraform) — registry provider: mỗi cloud provider đăng ký kiểu resource và nguồn dữ liệu
- [Babel](https://github.com/babel/babel) — registry plugin: transform tự đăng ký theo tên pattern visitor
- [pytest](https://github.com/pytest-dev/pytest) — registry fixture: `@pytest.fixture` đăng ký hàm khám phá được theo tên tham số
- [Docker](https://github.com/moby/moby) — registry driver: driver storage, network và logging đăng ký khi daemon khởi động

## Pattern liên quan

| Pattern | Quan hệ |
|---------|-------------|
| [Middleware](/patterns/middleware-chain/) | Handler middleware thường tự đăng ký vào registry |
| [Dependency Graph](/patterns/dependency-graph/) | Registry có thể theo dõi dependency giữa các thành phần đã đăng ký |
| [Consistent Hashing](/patterns/consistent-hashing/) | Service registry cung cấp danh sách node có sẵn cho consistent hashing |
| [Trie (Prefix Tree)](/patterns/trie/) | Trie có thể làm cấu trúc tra cứu bên dưới cho truy vấn registry dựa trên prefix |

## Câu hỏi thử thách

::: details Câu 1: Hai plugin cùng cố đăng ký tên "json". Nên xảy ra gì?
**Trả lời:** Fail nhanh với lỗi lúc đăng ký.

Ghi đè âm thầm che bug — handler plugin đầu biến mất không cảnh báo, gây lỗi runtime tinh tế. Chính sách "writer cuối thắng" hoạt động cho config nhưng nguy hiểm cho dispatch code.

Cách đúng: ném/trả lỗi khi đăng ký trùng. Nếu cần thay thế có chủ ý, cung cấp method tường minh `override()` hoặc `replace()` báo hiệu ý định.
:::

::: details Câu 2: Registry của bạn dùng key chuỗi. Làm sao chặn typo như "josn" thay "json" gây lỗi runtime?
**Trả lời:** Nhiều chiến lược:

1. **Hằng**: Định nghĩa key là hằng export (`const JSON = "json"`) để compiler bắt typo.
2. **Enum**: Dùng kiểu enum thay vì chuỗi thô — giới hạn không gian key lúc compile.
3. **Kiểm tra đăng ký**: Khi khởi động, xác minh mọi key kỳ vọng đã đăng ký trước khi nhận traffic.
4. **Match mờ**: Khi tra cứu thất bại, gợi ý tên đã đăng ký tương tự (khoảng cách Levenshtein).

Cách tốt nhất tuỳ registry mở (plugin thêm key) hay đóng (key biết lúc compile). Registry đóng nên dùng enum; registry mở nên kiểm tra khi khởi động.
:::

::: details Câu 3: REGISTER_OP của TensorFlow dùng macro C++ để đăng ký op lúc init tĩnh. Rủi ro là gì?
**Trả lời:** Thảm hoạ thứ tự init tĩnh.

Trong C++, thứ tự init tĩnh qua các translation unit không xác định. Nếu đăng ký op A phụ thuộc op B đăng ký trước, và chúng ở các file .cc khác nhau, chương trình có thể crash hoặc fail âm thầm.

TensorFlow giảm nhẹ bằng cách làm thứ tự đăng ký độc lập — mỗi op tự đăng ký không phụ thuộc op khác. Singleton `OpRegistry` được tạo khi dùng lần đầu (Meyers' singleton), tránh "thảm hoạ thứ tự init tĩnh" cho chính registry.
:::

::: details Câu 4: Registry khác dependency injection (DI) thế nào?
**Trả lời:** Hướng dòng điều khiển.

- **Registry**: Consumer chủ động kéo triển khai theo tên. Consumer biết tên và gọi `registry.get("json")`.
- **DI**: Framework đẩy dependency vào consumer. Consumer khai báo cần gì (qua tham số constructor hoặc annotation), và container DI nối.

Registry đơn giản hơn nhưng ghép consumer với API registry và tên chuỗi. DI tách rời thêm nhưng thêm phức tạp framework. Thực tế, container DI thường dùng registry nội bộ.
:::
