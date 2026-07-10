#!/bin/bash
cd "$(dirname "$0")"
echo "==================================="
echo "正在启动你的本地预览服务器..."
echo "如需停止，请关闭此终端窗口或按 Ctrl+C"
echo "==================================="
sleep 1 && open "http://localhost:8000" &
python3 -m http.server 8000
