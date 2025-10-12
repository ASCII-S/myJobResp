理想答案应该是：

cudaMalloc(void** **\*\*devPtr, size_t size)：在 GPU 全局内存上分配一块指定大小的内存空间，第一个参数是指向设备指针的地址，第二个是字节数。常见用法：

cpp
复制代码
float *d_A;
cudaMalloc((void**)&d_A, N * sizeof(float));
cudaFree(void* devPtr)：释放之前通过 cudaMalloc 分配的 GPU 内存，避免内存泄漏。

cudaMemcpy(void* dst, const void* src, size_t count, cudaMemcpyKind kind)：在 Host 和 Device 之间，或 Device 内部进行内存拷贝。常见方向：

cudaMemcpyHostToDevice

cudaMemcpyDeviceToHost

cudaMemcpyDeviceToDevice

示例：

cpp
复制代码
cudaMemcpy(d_A, h_A, N * sizeof(float), cudaMemcpyHostToDevice);