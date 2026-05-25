#!/bin/bash
# Script de build pour Render.com
# 1. Installe les deps Python
# 2. Compile le frontend React
# 3. Les fichiers statiques vont dans backend/static/

echo "=== Installation des dependances Python ==="
cd backend
pip install -r requirements.txt

echo "=== Installation des dependances Node.js ==="
cd ../frontend
npm install

echo "=== Build du frontend React ==="
npm run build

echo "=== Build termine ! ==="
echo "Les fichiers statiques sont dans backend/static/"
ls -la ../backend/static/
