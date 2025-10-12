# unique_ptr、shared_ptr、weak_ptr的使用场景

## 面试标准回答（精炼版）

> C++ 智能指针分三类：`unique_ptr` 独占所有权、只可移动；`shared_ptr` 共享所有权、通过原子引用计数在最后一个持有者释放资源；`weak_ptr` 不拥有对象、用于观察与打破循环引用。
>
> 实战上：函数需要接管资源就按值接收 `unique_ptr` 并 `std::move`；只读传参用引用/裸指针；共享跨组件/线程用 `shared_ptr`，但注意原子计数开销和循环引用，用 `weak_ptr` 做回指；在成员函数里要生成自身的 `shared_ptr` 时，应继承 `enable_shared_from_this`。优先使用 `make_unique`/`make_shared` 获得异常安全与更少分配；需要自定义清理其他句柄时用自定义删除器。数组有专门形式：`unique_ptr<T[]>` / `shared_ptr<T[]>`。
>
> 切记**配对与混用**：`new`/`delete` 由智能指针托管；不要把 `this` 直接包进新的 `shared_ptr`；别把 `shared_ptr` 长久转成 raw 指针持有而忘记生命周期。

如果你想再进阶一格，可以继续聊：**make\_shared 的“内嵌对象”带来的生存期耦合取舍、别名构造的典型用法、以及在高频路径用 `unique_ptr` + 明确所有权替代 `shared_ptr` 的性能权衡**。

---

### `std::unique_ptr`（独占）

**定位**：独占所有权，**只能移动，不能拷贝**。
**典型用法**：

* 工厂函数返回所有权：`std::unique_ptr<Foo> makeFoo();`
* 在容器里装多态对象：`std::vector<std::unique_ptr<Base>> v;`
* 自定义删除器管理非 `new` 资源：`unique_ptr<FILE, int(*)(FILE*)> fp(fopen(...), fclose);`
* 数组：`std::unique_ptr<T[]> p(new T[n]);`
  **首选构造**：`std::make_unique<T>(args...)`（异常安全、少写 `new`）。
  **传参策略**：
* 只读不接管：`const T&` 或 `T const*`；
* 需要接管：按值接收 `std::unique_ptr<T>`，调用方 `std::move` 进来。
  **坑点**：
* 别从 `unique_ptr` 偷生 raw 指针长期保存；
* 自定义删除器会进类型，影响对象大小（但不影响性能）。

---

### `std::shared_ptr`（共享）

**定位**：共享所有权，**引用计数（原子）**，最后一个持有者释放资源。
**控制块**：保存计数、删除器、（可选）自定义分配器。
**常用构造**：`std::make_shared<T>(args...)`（对象与控制块一次分配，缓存友好；但对象“内嵌”于控制块，定制分配或超长生命周期弱化时需权衡）。
**跨线程**：引用计数原子更新，可跨线程传递。
**配合**：多态 + 容器 + 异步任务（回调里延长对象寿命）。
**高级**：

* `enable_shared_from_this<T>`：成员函数里安全拿到 `shared_ptr<T>`（避免 `shared_ptr(this)` 的*二次控制块/双删*灾难）。
* **别名构造**：`shared_ptr<U> sp(sp_t, alias_ptr)` 用同一控制块管理不同指针（如指向子成员），常用于返回子对象但共享同一生命周期。
  **坑点**：
* **循环引用**：A 持有 B 的 `shared_ptr`，B 也持有 A 的 `shared_ptr` ⇒ 永不为 0 ⇒ 泄漏。**解法**：把“回指”改成 `std::weak_ptr`。
* 成本：计数是原子的，有开销；频繁增减引用要留心热点路径。
* 数组：优先用 `shared_ptr<T[]>` 或自定义删除器（否则删除器只删第一个元素）。

---

### `std::weak_ptr`（观察者）

**定位**：**不参与**引用计数，观察 `shared_ptr` 管理的对象，打破环。
**用法**：

* 从 `shared_ptr` 派生：`std::weak_ptr<Foo> w = sp;`
* 在用前锁：`if (auto s = w.lock()) { /* 安全使用 */ }`
  **典型场景**：
* 解决**双向关系**的环：A 持 B 的 `shared_ptr`，B 回指 A 用 `weak_ptr`。
* 观察/缓存：订阅者保存 `weak_ptr`，发布者短生命周期不被意外延长。
  **坑点**：`weak_ptr` 不能解引用，必须 `lock()`；并发下要在同一临界区检查 `lock()` 结果并使用。

---
