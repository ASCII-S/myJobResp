
**移动语义（Move Semantics）**
是 C++11 引入的一种语言机制和设计理念，它的核心目的是：

* 允许对象在赋值或初始化时“窃取”另一个对象的资源（比如堆内存、文件句柄），而不是做昂贵的拷贝。
* 移动语义通过**移动构造函数**和**移动赋值运算符**来实现。
* 举例：

  ```cpp
  class MyVec {
      int* data;
      size_t size;
  public:
      MyVec(size_t n) : data(new int[n]), size(n) {}
      // 移动构造函数
      MyVec(MyVec&& other) noexcept : data(other.data), size(other.size) {
          other.data = nullptr;  // 资源转移
          other.size = 0;
      }
  };
  ```

  这就是语言层面支持的“移动语义”。

---

**`std::move`**

* 它不是移动操作，而是一个**类型转换工具**，把一个左值显式地转换成右值引用。
* 语法上就是一个 `static_cast<T&&>` 的包装。
* 只有当类实现了移动构造/赋值时，`std::move` 才会真正触发“移动”；否则它依然会退化到拷贝。
* 举例：

  ```cpp
  std::vector<int> v1 = {1,2,3};
  std::vector<int> v2 = std::move(v1);  // std::move 把 v1 转为右值引用
  ```

---

**关键区别总结**：

* 移动语义：C++11 的语言特性，本质是“如何高效转移资源”的一套机制，通过特殊构造函数/赋值运算符来实现。
* `std::move`：一个标准库工具函数，作用只是**把对象标记为右值引用**，以便编译器调用移动构造/赋值。它本身不做移动。

---

如果面试官追问，你可以加一句：

> 移动语义是能力，`std::move` 是触发器。
