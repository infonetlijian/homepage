| [Blog](/homepage/blog/blog.html) | [News](/homepage/) | [CV](/homepage/CV.html) | [Professional Activities](/homepage/activities.html) | [Publications](/homepage/publications.html) | [Projects](/homepage/projects.html) | [Funding](/homepage/funding.html) | [Patents](/homepage/patents.html) | [Teaching](/homepage/teaching.html) |   

## <font color=#6EB1EC>简介</font>  

**问题描述**：之前在Windows平台上用CTeX撰写论文时，时常发现有些package无法被识别，需要单独下载更新。由于CTeX套装长久不更新，套装中的MiKTeX版本太旧，导致无法进行在线更新。本文介绍一种自主更新CTeX工具集的方法。

**2024.5.20更新**：目前CTeX套装已更新至3.1.218版本([官方网站](https://ctex.org/ctex/download/))，包含如下软件
        MiKTeX 24.1
        WinEdt 11.1 (64-bit) / 10.3 (32-bit)
        GSview 6.0
        Ghostscript 10.02.1
        

## <font color=#6EB1EC>更新流程</font>
* 1.下载最新版相关软件：
  * CTeX套装：前往[**Tsinghua Open Source Mirror**](https://mirrors.tuna.tsinghua.edu.cn/ctex/legacy/2.9/)下载CTeX_2.9.2.164_Full.exe，(选择完整版安装)；
  * MiKTeX：前往[**MiKTeX**](https://miktex.org/download)官方网站下载；  
  * WinEdt：前往[**WinEdt**](http://www.winedt.com/download.html)官方网站下载；  
  * SumatraPDF：前往[**SumatraPDF**](https://www.sumatrapdfreader.org/download-free-pdf-viewer.html)官方网站下载：
* 2.首先安装CTEX套件：选择语言，中文简体->ok->下一步->接受许可协议，在选择安装组件时注意要把MiKTeX的选项勾选掉，并同时保留住其他四项，尤其是WinEdt一定要保留。继续，下一步，选择默认安装路径为 C:\CTEX，完成CTeX套装的安装。

* 3.安装最新版MiKTeX：在C:\CTEX路径下新建一个空文件夹并命名为“MiKTeX”，双击basic-miktex-2.9.6753-x64.exe，启动安装程序。在安装过程中，选择安装路径为：C:\CTEX\MiKTeX, 然后一路选择默认选项，继续完成安装。

* 4.替换最新版 WinEdt：注意，不要手动删除C:\CTEX中的任何旧版WinEdt文件，直接将winedt103-64.exe拷贝到C:\CTEX\WinEdt文件夹，双击exe文件开始覆盖安装，完成。此时WinEdt仍是31天试用版本，支持正版。如有非盈利的工作需要，常用破解方法有两种：
  * 1).注册码破解，源自于某位不认识大神的贡献，亲测有效，非常感谢。

  * Name:Cracker TeCHiScy
  * Code:1130140925535334280

  * [**引用网址1**](http://blog.csdn.net/sdujava2011/article/details/57409399)

  * [**引用网址2**](https://www.52pojie.cn/thread-595351-1-1.html)
  * 2）.无限延长试用期的方法，这也是应用最多的方法，通过修改WinEdt里的exit文件，使得每次退出都会清除当前的试用时间，具体方法这里不再赘述，附上一个网址：[**按照步骤来就行**](https://jingyan.baidu.com/article/d2b1d102913bbd5c7e37d4e4.html)
  * 注意：将需要添加语句  RegDeleteValue('HKEY_CURRENT_USER', 'Software\WinEdt 8', 'Inst'); 的版本号改为自己的版本号，比如上面是8，如果用的是10.2的话，改为10就行。
* 5.替换最新版 Sumatra PDF：直接双击SumatraPDF-3.1.2-64-install.exe文件，按照默认选项完成安装。然后，打开WinEdt10.3，选择：Options->Execution Modes->PDF Viewer, 并将首个PDF Viewer Executable路径设置为安装过后的Sumatra PDF.exe路径即可。
* 6.最后，更新MiKTeX组件和宏包：在windows的所有程序中找到MiKTeX 2.9文件夹下的 MiKTeX Console 应用程序亦可在搜索栏中直接查找，并启动 MiKTeX Console ）。
* 第一次运行时最好进入Updates选项中进行在线更新。如果需要更换镜像源，在Install from 选项中点击“change”,选择一个比较稳定的镜像源即可，自动完成更新。

[**相关参考网站1**](https://zhuanlan.zhihu.com/p/47420690)
[**相关参考网站2**](https://www.cnblogs.com/xiachongkun/p/8176390.html)

