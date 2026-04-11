import sys
sys.path.append("../../") # 测试环境,把上2层加入path,即可以 查找到 opentdx 包
sys.path.append("/data0/htdocs/ak_fastapi/pytdx2")
from opentdx import doc 

doc.main()  # 启动完整的交互式菜单