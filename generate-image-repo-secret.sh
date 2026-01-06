#!/bin/bash    

echo "=========================================="
echo "Docker Registry Secret Generator"
echo "=========================================="
echo ""

# 交互式获取用户名
read -p "请输入 Docker Registry 用户名: " USERNAME
if [ -z "$USERNAME" ]; then
    echo "错误: 用户名不能为空"
    exit 1
fi

# 交互式获取密码（隐藏输入）
read -sp "请输入 Docker Registry 密码: " PASSWORD
echo ""
if [ -z "$PASSWORD" ]; then
    echo "错误: 密码不能为空"
    exit 1
fi

# 交互式获取 Kubernetes 命名空间
read -p "请输入 Kubernetes 命名空间 [default]: " NAMESPACE
NAMESPACE="${NAMESPACE:-default}"

# 交互式获取 Registry 地址（带默认值）
read -p "请输入 Docker Registry 地址 [https://index.docker.io/v1/]: " REGISTRY
REGISTRY="${REGISTRY:-https://index.docker.io/v1/}"

OUTPUT_FILE="./config.json"

echo ""
echo "正在生成 Docker config.json 文件..."

AUTH=$(echo -n "$USERNAME:$PASSWORD" | base64 | tr -d '\n')

cat > "$OUTPUT_FILE" <<EOF
{
"auths": {
    "$REGISTRY": {
    "auth": "$AUTH"
    }
}
}
EOF

echo "Docker config.json 已生成: $OUTPUT_FILE"
echo ""
echo "正在创建 Kubernetes Secret..."
kubectl -n $NAMESPACE create secret generic image-repo-secret --from-file=.dockerconfigjson=$OUTPUT_FILE --from-file=config.json=$OUTPUT_FILE --type=kubernetes.io/dockerconfigjson

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Secret 'image-repo-secret' 已在命名空间 '$NAMESPACE' 中成功创建！"
else
    echo ""
    echo "✗ 创建 Secret 失败，请检查错误信息"
    rm "$OUTPUT_FILE"
    exit 1
fi

rm "$OUTPUT_FILE"
echo "临时文件已清理"