if [ -e './spider.zip' ];then
  rm ./spider.zip
  echo '删除旧的压缩包'
fi
echo '开始压缩'
if [ -e '/var/www/html/spider.zip'  ];then
  rm /var/www/html/spider.zip
  echo '删除旧的nginx文件'
fi
echo '压缩完成, 开始复制文件到nginx'
zip -r -q spider.zip ./spider_data
cp ./spider.zip /var/www/html
echo '复制完成, 可以开始下载'