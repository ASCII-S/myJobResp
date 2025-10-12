
CUDA kernel 的启动配置用 <<<gridDim, blockDim, sharedMem, stream>>> 语法，其中：

gridDim：定义网格规模，即有多少个线程块。可以是一维、二维或三维（dim3 类型）。

blockDim：定义单个线程块中的线程数，也可以是一维、二维或三维。

sharedMem（可选）：为每个线程块动态分配的共享内存大小（字节数），默认是 0。

stream（可选）：指定 kernel 属于哪个 CUDA 流，没写时默认是 0 号流。