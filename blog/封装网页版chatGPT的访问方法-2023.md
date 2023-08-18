| [Blog](/homepage/blog/blog.html) | [News](/homepage/) | [CV](/homepage/CV.html) | [Professional Services](/homepage/services.html) | [Publications](/homepage/publications.html) | [Projects](/homepage/projects.html) | [Patents](/homepage/patents.html) | [Teaching](/homepage/teaching.html) |

## <font color=#6EB1EC>简介</font>  

以开源项目[潘多拉 (Pandora)](https://github.com/pengzhile/pandora)为例，介绍如何封装网页版chatGPT的方法。该程序实现了网页版 ChatGPT 的主要操作。后端优化，绕过 Cloudflare，速度喜人。

## <font color=#6EB1EC>安装流程</font>
* 1.在Windows操作系统上，可以使用'CMD'命令调用命令行工具，但更建议使用开源跨平台的新式命令行外壳程序和脚本环境PowerShell，[下载地址](https://github.com/PowerShell/PowerShell/releases)。
* 2.需要在电脑上配置好[python](https://www.python.org/downloads/)环境（2023/8/18号，最新版本为3.12）。
  * 使用以下命令一键安装Python程序（[参考网址](https://juejin.cn/s/install%20python3%20via%20powershell)）：'Invoke-WebRequest -Uri https://www.python.org/ftp/python/3.9.9/python-3.9.9-amd64.exe -OutFile python-3.9.9-amd64.exe'
  * 运行以下命令以开始安装程序：'.\python-3.9.9-amd64.exe'
  * 其中，上述命令中的 Python 3 版本号'python-3.9.9-amd64.exe'，是当前最新版本的 Python 3，如果您想安装其他版本的 Python 3，请在下载 URL 中更改版本号。
  * 在安装过程完成后，您可以使用以下命令检查 Python 3 是否已成功安装：'python --version'，如果输出了 Python 3 版本号，则说明已经成功安装 Python 3。
  * 备注：在最新版本的Windows 10操作系统下，在命令行中直接运行'Python'命令，会弹出Windows应用商店，很恶心。造成这一点的主要原因在于新版本Windows写入'C:\Users\Administrator\AppData\Local\Microsoft'类似的路径，里面包含了'Python.exe'的文件，导致每次运行'Python'命令会索引到微软商店下的Python程序。网上有一些解决方案，主要是修改系统变量的PATH路径，通过修改修改Python路径'C:\Users\Administrator\AppData\Local\Programs\Python\Python39\'的优先级或者删除上述'C:\Users\Administrator\AppData\Local\Microsoft'类似路径的方法解决。但奇怪的是，在我的电脑上均不奏效，无论如何修改环境变量，依旧会弹出微软商店。我猜测微软有一个隐藏的环境变量索引。最终的解决方法是，删除（改名亦可）Microsoft目录下的'Python.exe'文件即可（见下方命令，来源参考[stack overflow](https://stackoverflow.com/questions/58754860/cmd-opens-windows-store-when-i-type-python/64754371#64754371)）。
  * This is a PowerShell script that does the magic：Remove-Item $env:USERPROFILE\AppData\Local\Microsoft\WindowsApps\python*.exe
* 3.下载Github上的开源项目[Pandora最新Release](https://github.com/pengzhile/pandora/releases)，并完成解压。
* 4.安装Pandora程序：
  * 命令行中利用'cd'命令索引到目录内
  * 执行'python setup.py build'
  * 之后执行'python setup.py install'进行安装，需要等待一段时间
* 5.使用Pandora程序，参见[使用教程](https://github.com/pengzhile/pandora/blob/master/doc/wiki.md)：
  * 命令行中运行'pandora'或者'pandora --api'（使用gpt-3.5-turboAPI请求，可能需要向OpenAI支付费用）
  * 注：api可以登陆[Openai官网](https://platform.openai.com/)，在右上角的个人账户处点击'View API keys'即可生成api
  * 鉴于我本人的Openai账号是第三方登陆账号（Google账号登陆），可以使用'Access Token'方式登录，实现无代理直连
  * [这个服务](https://ai-20230626.fakeopen.com/auth)可以帮你安全有效拿到'Access Token'，无论是否第三方登录
  * 其中，'accessToken'字段的那一长串内容即是'Access Token'，其有效期目前为14天
* 注：更为简单的使用方法，可以使用网页版[FakeGPT](https://chat.zhile.io/)进行体验（目前提供共享账号，以及'Access Token'登陆两种方式）

