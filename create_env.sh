#!/bin/bash

# 检查imre环境是否存在
env_exists=$(conda env list | grep 'srte')

if [[ -z $env_exists ]]; then
    # 如果环境不存在，创建环境并指定Python版本为3.9
    echo "srte环境不存在，正在创建环境，并指定Python版本为3.9..."
    conda create -n srte python=3.9 -y
    echo "环境创建成功。"
fi

# 激活srte环境
echo "正在激活srte环境..."
conda activate srte

# 安装requirements.txt中的依赖
echo "正在安装/更新依赖..."
pip install -r requirements.txt

echo "依赖安装/更新完成。"