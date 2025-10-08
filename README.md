![dmd](./assets/dmd.png)



<h1 align="center">DMD - Disk Memory Detector</h1>



`dmd` 是一个用于 **检测磁盘文件大小、分析文件夹变化趋势、自动清理旧日志文件** 的 Python 命令行工具。  
支持递归扫描文件夹、比较两次状态变化、找出空间增长最快的目录。未来将支持图形界面版本。



# 开始使用



## 安装



```powershell
git clone https://github.com/banxianxian/disk-memory-detect.git
```





## 运行

进入工作目录`disk-memory-detect`

```cmd
cd disk-memory-detect
dmd run [dir_path] [options]
```



| 参数        | 说明                                           |
| ----------- | ---------------------------------------------- |
| `dir_path`  | 位置参数，需要扫描的磁盘，使用 `/`，比如`C:/`  |
| `--topn`    | 可选参数，显示变化最大的前 N 个目录            |
| `--minsize` | 可选参数，忽略小于指定大小（单位：字节）的变化 |





