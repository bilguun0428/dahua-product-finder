#!/bin/bash
echo "Dahua Product Finder - Эхлүүлж байна..."
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Python3 олдсонгүй! Python суулгана уу."
    exit 1
fi

# Install dependencies
echo "Шаардлагатай сангуудыг суулгаж байна..."
pip3 install -r requirements.txt -q

echo ""
echo "Сервер эхэлж байна..."
python3 server.py
