# Automatic-minesweeping
A script for automatic minesweeping

这是一个可以自动扫雷的脚本

# 步骤

扫雷时请使用该网页：http://www.minesweeper.cn/

扫雷前，先根据每个雷块的大小对main.py中的gridwidth，gridheight进行修改。然后截取棋盘左上角、右下角、笑脸等图片以供棋盘的识别，用你截取的图片覆盖pictures文件夹下的对应图片（注意名字要正确）。

然后执行main.py程序后打开网页即可执行扫雷：

执行main.py的方法参考：win+R打开cmd，进入Automatic-minesweeping文件夹下，输入命令:

>python main.py


# 问题

如果缺少运行环境，请根据缺少的部分按照requirements.txt中的版本进行安装：

根据提示信息，找到对应包名，然后在cmd中执行：

>pip install 包名

如果遇到扫雷出错，请稍微增加main.py中delay变量的值
