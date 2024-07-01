#!/bin/bash -e

# Создание необходимых каталогов
mkdir -p src/{lambda_bot,layer/python/lib/python3.12/site-packages}

# Копирование файлов бота в соответствующий каталог
cp lambda_bot config.py functions.py routes.py src/lambda_bot/
touch src/lambda_bot/__init__.py

# Упаковка всех файлов в src в lambda.zip
cd src
zip -r ../lambda.zip .
cd ..

# Установка зависимостей в правильную структуру каталогов для слоя
pip install -r requirements.txt --platform manylinux2014_x86_64 --target src/layer/python/lib/python3.12/site-packages --only-binary=:all:

# Создание архива layer.zip
cd src/layer
zip -r ../../layer.zip python
cd ../../

# Очистка временных файлов
rm -rf src
