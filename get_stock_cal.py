#!/usr/bin/python3
# -*- coding: utf-8 -*-

# 這是一個爬蟲程式，用來從富邦證券網站上抓取産業分類表。
# 從「富邦證券」-> 「國內股票」->「產業景氣循環圖」->「產業分類」裡，取出所有產業的名稱，並印出來。
# https://fubon-ebrokerdj.fbs.com.tw/z/zh/zha/zha.djhtm
#
# 加進 MySQL 資料表時有可能會遇上的問題：
# 等待時間過長，可能會被伺服器拒絕
# 改成每次只取一個產業，這樣就不會有這個問題了。
# 
# 發現股票名稱印出及填入 mysql 有可能會變成亂碼！！


import requests
from bs4 import BeautifulSoup
import re
import time
import mysql.connector


# 這是一個爬蟲程式，用來從富邦證券網站上抓取産業分類表。
# URL 是採用 base_url + page_url 的方式組合而成。
# 這個函數會返回一個 list, list 中包含了股票的代號和名稱。
def get_stock_names(page_url: str) -> list:
    base_url = "https://fubon-ebrokerdj.fbs.com.tw/z/zh/zhc/zhc.djhtm"
    url = f"{base_url}?a={page_url}"
    print(f"正在訪問網頁：{url}")

    headers = { 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0' }
    # 發送 GET 請求到指定的 URL
    response = requests.get(url, headers=headers, timeout=10)
    
    # 確保請求成功
    if response.status_code != 200:
        print(f"無法訪問網頁，狀態碼：{response.status_code}")
        return []

    # 使用 BeautifulSoup 解析 HTML 內容
    soup = BeautifulSoup(response.text, 'html.parser')

    #print(soup.prettify())
    
    # 使用正確的選擇器來找到股票名稱元素
    #<td class="t3t1" id="oAddCheckbox">

    #<script language="javascript">
    #<!-- GenLink2stk('AS1101','台泥'); -->
    #</script>
    # 取出元素列表
    stock_elements = soup.select('script')

    # print(stock_elements)
    
    ## 提取並返回股票名稱
    stock_names = []
    for element in stock_elements:
        # 提取文本並去除可能的前後空白

        #print (element.text)

        stock_name = element.text.strip()

        # 分離股票代碼和名稱

        # <!--
	    #        GenLink2stk('AS1101','台泥');
        # //-->

        # 使用正則表達式提取股票代碼和名稱
        pattern = re.compile(r"GenLink2stk\('(\w+)','(.+?)'\);")
        match = pattern.search(stock_name)
        if not match:
            continue

        code, name = match.groups()
        # 移除前飾字 AS
        code = code[2:] 
        stock_names.append((code, name))

        #print (stock_name)

    return stock_names


# 組合出正確的 URL, 並抓取網頁內容。寫入 data table 中。
def get_stock_url(table_name = str, page=None):

    # 幾次實驗後發現，富邦證券的網站會在一段時間後取不到資料，所以每次只取幾個產業。避免被伺服器拒絕。
    # 從富邦抄出來的表, 第一組 key 是大類，第二組後的 key 是開啟的網址參數，修改成 list。
    # list 中的第一個元素是”産業“，第二個元素是 dict，keys 是開啟的網址參數，value 是”細產業“。
    NewkindIDNameStr = [
      [ '水泥類', { 'C011010' : '水泥', 'C011011' : '水泥製品', 'C025012' : '預拌混凝土', 'C099192' : '高爐水泥' } ],
      [ '食品飲料類', { 'C012011' : '方便麵', 'C012014' : '乳製品', 'C012015' : '調味品', 'C012016' : '食品加工', 'C012017' : '罐頭', 'C012024' : '肉品加工', 'C012029' : '農產品加工', 'C012030' : '麵製品相關', 'C012031' : '水產品加工', 'C012032' : '糖果製品', 'C012033' : '保健食品', 'C012034' : '可可製品', 'C012035' : '穀類烘焙製品', 'C012036' : '磨粉製品', 'C012038' : '調理食品', 'C012039' : '茶葉與咖啡相關', 'C012040' : '寵物食品', 'C012043' : '餅乾製品', 'C012044' : '食品添加劑', 'C012012' : '製糖', 'C012020' : '大宗物資', 'C012021' : '面粉', 'C012022' : '油脂', 'C017240' : '製鹽', 'C012013' : '非酒精飲料', 'C012019' : '釀酒', 'C012026' : '啤酒', 'C012027' : '紅酒', 'C012028' : '白酒', 'C012041' : '飲料相關', 'C012042' : '蒸餾酒' } ],
      [ '石化類', { 'C013010' : 'PVC', 'C013030' : 'PE', 'C013040' : 'DOP', 'C013050' : '芳香烴', 'C013060' : 'SM', 'C013070' : 'ABS', 'C013080' : 'PS', 'C013090' : '塑膠皮布', 'C013110' : 'PP', 'C013130' : '烯烴', 'C013180' : '塑膠加工', 'C013190' : 'PA', 'C013192' : '瀝青', 'C013990' : '石化業', 'C017083' : 'EVA' } ],

     # [ '紡織類', { 'C013120' : 'AN', 'C014010' : '聚酯纖維', 'C014011' : '聚酯絲', 'C014012' : '聚酯加工絲', 'C014013' : '聚酯棉', 'C014014' : '紡織用聚酯粒', 'C014015' : '瓶用聚酯粒', 'C014016' : '寶特瓶', 'C014031' : '尼龍粒', 'C014032' : '尼龍加工絲', 'C014033' : '尼龍絲', 'C014050' : '亞克力棉', 'C014051' : '亞克力紗', 'C014060' : '化纖原料', 'C014061' : 'EG', 'C014062' : 'PTA', 'C014063' : 'CPL', 'C014064' : '粘膠', 'C014065' : '氨綸', 'C014066' : '芳綸', 'C014067' : '丙綸', 'C014068' : '再生纖維', 'C014069' : '半合成纖維', 'C014180' : '成衣', 'C014181' : '成衣製造', 'C014182' : '成衣銷售／零售', 'C014183' : '內衣褲、襪', 'C014030' : '尼龍製品', 'C014140' : '羊毛', 'C014150' : '加工絲', 'C014170' : '毛紡', 'C014171' : '麻紡', 'C014172' : '絲織品', 'C014173' : '混紡紗', 'C014190' : '染整', 'C014200' : '織布', 'C014201' : '無紡布', 'C014202' : '棉紡', 'C014203' : '魚網', 'C014204' : '聚酯紗', 'C014205' : '純棉紗', 'C014206' : '尼龍塔夫塔', 'C014207' : '粘扣帶', 'C014208' : '羽絨加工', 'C014210' : '工業用布', 'C014990' : '紡織中游' } ],
     # [ '電機機械類', { 'C015080' : '工具機', 'C015081' : '龍門機', 'C015090' : '壓縮機', 'C015100' : '木工機械', 'C015101' : '紡織機械', 'C015104' : '手持工具', 'C015107' : '幫浦', 'C015108' : '空調製冷', 'C015110' : '其他產業機械', 'C015111' : '塑膠機械', 'C015112' : '橡膠機械', 'C015113' : '包裝機械', 'C015115' : '通用機械', 'C015116' : '動力機械', 'C015120' : '工程機械', 'C015130' : '農用機械', 'C015140' : '機械零組件', 'C015141' : '磨料磨具', 'C015150' : '造船', 'C015151' : '飛機零件／製造', 'C015152' : '工業電機', 'C015153' : '家用縫紉機', 'C015154' : '模具', 'C015155' : '軌道運輸設備', 'C015156' : '工業用縫紉機', 'C015160' : '自動化設備', 'C015170' : '柴油機', 'C015180' : '機器人', 'C015201' : '單車零件', 'C015202' : '儀表', 'C015204' : '污染控制設備', 'C015205' : '裝載機', 'C015206' : '醫療保健設備／裝置', 'C015207' : '海洋工程設備', 'C015208' : '工業閥門', 'C015209' : '焊接設備', 'C015210' : '叉車／輸送設備', 'C015211' : '軸承／滑軌', 'C015770' : '機械', 'C026070' : '貨櫃製造', 'C015020' : '電機', 'C015021' : '重型電氣設備', 'C015022' : '電氣零件與設備', 'C015023' : '鍋爐', 'C015024' : '變電設備', 'C015025' : '輸配電設備', 'C015026' : '電氣開關設備', 'C015027' : '電氣自控設備', 'C015028' : '車用充電相關', 'C015102' : '配電工程', 'C015103' : '工業用電池', 'C015106' : '配電盤', 'C015109' : '變頻器', 'C015990' : '電力設備' } ],

     # [ '電器電纜類', { 'C015010' : '小家電', 'C015012' : '電雪櫃', 'C015013' : '洗衣機', 'C015014' : '冷氣機', 'C015015' : '音響/視聽組合', 'C015016' : '電器銷售', 'C015060' : '照明', 'C015061' : '家電零組件', 'C015880' : '家電', 'C023234' : '液晶電視', 'C016010' : '電線電纜', 'C016011' : '同軸電纜', 'C016012' : '電子線', 'C016013' : '漆包線', 'C016014' : '裸銅線', 'C016016' : '電纜連接件及附件', 'C016017' : '電力電纜' } ],
     # [ '化學工業類', { 'C017490' : '電池材料相關', 'C017495' : '正極材料', 'C017496' : '負極材料', 'C017497' : '電解液', 'C017498' : '電池隔離膜', 'C013150' : '溶劑', 'C013160' : '烷基苯', 'C013170' : '正烷屬烴', 'C013171' : '石蠟', 'C013173' : '工業氣體', 'C017030' : '衛生清潔用品', 'C017040' : '染料，顏料', 'C017050' : '農藥', 'C017051' : '草甘膦', 'C017055' : '肥料', 'C017060' : '膠帶', 'C017080' : '合成樹脂', 'C017081' : 'PU樹脂', 'C017120' : '鹼業', 'C017130' : '保險粉', 'C017140' : '硝化棉', 'C017160' : '熱熔膠', 'C017170' : '碳酸鋇', 'C017180' : '石墨', 'C017190' : '磷化工', 'C017200' : '炸藥', 'C017210' : '尿素', 'C017220' : '硝酸銀', 'C017230' : '拋光蠟', 'C017250' : '鈦白粉', 'C017260' : '氟化物', 'C017270' : '煤化工', 'C017280' : '丁二醇', 'C017290' : '二甲基甲醯胺(DMF)', 'C017300' : '磷酸二銨(DAP)', 'C017310' : '磷酸一銨(MAP)', 'C017320' : 'MDI', 'C017330' : 'TDI', 'C017340' : '有機硅', 'C017350' : '雙酚A', 'C017360' : '硫磺', 'C017370' : '黃磷', 'C017380' : '環氧丙烷', 'C017390' : '醋酸', 'C017391' : '酚', 'C017491' : '氣凝膠', 'C017492' : '石油支撐劑', 'C017493' : '化學產品通路', 'C017494' : '強酸產品', 'C017499' : '草酸', 'C017880' : '化學工業', 'C017990' : '其它化工產品', 'C018011' : '涂料', 'C021010' : '輪胎', 'C021050' : '橡膠製品', 'C021060' : '碳煙', 'C021070' : '合成橡膠', 'C021080' : '油封', 'C021090' : '天然橡膠', 'C021100' : '熱可塑橡膠', 'C021110' : '乳膠相關', 'C021990' : '橡膠工業' } ],
     # [ '建材居家用品類',{ 'C015030' : '電梯', 'C018010' : '建材', 'C018012' : '輕鋼架', 'C018013' : '複合板', 'C018014' : '金屬建材', 'C018020' : '玻璃', 'C018040' : '釉料', 'C018070' : '岩棉', 'C018990' : '陶瓷', 'C014209' : '地毯', 'C018030' : '家居用品', 'C018031' : '辦公傢俱', 'C018050' : '衛浴設備', 'C018060' : '廚具', 'C099130' : '家具', 'C099132' : '窗帘', 'C099133' : '水龍頭', 'C099180' : '鎖', 'C099193' : '寢具' } ],

     # [ '造紙類', { 'C019010' : '紙漿', 'C019020' : '工業用紙', 'C019030' : '文化用紙', 'C019040' : '家庭用紙', 'C019050' : '包裝用紙', 'C019060' : '特殊用紙', 'C019990' : '造紙業' } ],
     # [ '鋼鐵金屬類', { 'C020021' : '螺絲、螺帽', 'C020030' : '線材、盤元', 'C020040' : '鋼筋', 'C020050' : '條鋼', 'C020060' : '型鋼', 'C020070' : '鋼架構', 'C020080' : '鋼管', 'C020150' : '棒鋼', 'C020110' : '不鏽鋼', 'C020114' : '冷軋不鏽鋼', 'C020115' : '熱軋不鏽鋼', 'C020116' : '不鏽鋼品', 'C020117' : '不鏽鋼剪裁加工', 'C020118' : '不鏽鋼管', 'C020119' : '不鏽鋼緊固件', 'C020121' : '不鏽鋼線材', 'C020111' : '合金鋼', 'C020112' : '特殊鋼', 'C020113' : '工具鋼', 'C020130' : '非鐵金屬', 'C020131' : '銅', 'C020132' : '鋁', 'C020133' : '鎳', 'C020135' : '鉭', 'C020137' : '鎢', 'C020138' : '鋅', 'C020139' : '鈦', 'C020140' : '鋯', 'C020141' : '錫', 'C020142' : '鍶', 'C020143' : '鋁擠型', 'C020145' : '鈾', 'C020147' : '鉬', 'C020148' : '鎂合金', 'C020149' : '稀土', 'C020191' : '釩', 'C020192' : '鈷', 'C099080' : '製鉛業', 'C020134' : '黃金', 'C020136' : '鉑', 'C020144' : '銀', 'C020146' : '鈀', 'C020170' : '貴金屬', 'C020011' : '鋼胚', 'C020012' : '鐵礦砂', 'C020020' : '熱軋鋼卷', 'C020090' : '冷軋鋼卷', 'C020100' : '鍍鋅鋼卷', 'C020120' : '烤漆鋼卷', 'C020160' : '鋼剪裁加工', 'C020180' : '鋼板', 'C020190' : '塗鍍鋼捲', 'C020990' : '板鋼', 'C099352' : '金屬礦采選' } ],
     # [ '車輛相關類', { 'C015105' : '車燈', 'C022011' : '汽車保險杠', 'C022040' : '汽機車零部件', 'C022045' : '木床／車架', 'C022046' : '汽車鈑金', 'C022048' : '引擎相關', 'C022051' : '傳動系統', 'C022053' : '輪轂', 'C022054' : '活塞', 'C022062' : '轉向系統', 'C022063' : '剎車系統', 'C022064' : '懸吊系統', 'C022065' : '車用冷卻系統', 'C022080' : '車用電池', 'C022083' : '車用防盜系統', 'C022084' : '車用軸承', 'C022085' : '機車零部件', 'C022086' : '車用排氣系統', 'C022043' : '汽車空調', 'C022047' : '儀表盤', 'C022049' : '車用玻璃', 'C022050' : '汽車音響', 'C022055' : '汽車內飾', 'C022056' : '安全氣囊', 'C022061' : '汽車座椅', 'C022041' : '車用鑄件', 'C022042' : '車用鍛件', 'C022070' : '車用金屬成型', 'C022081' : '車用沖壓件', 'C022082' : '車用粉末冶金件', 'C022005' : '汽車製造', 'C022006' : '電動車', 'C022007' : '電動機車', 'C022010' : '汽車銷售', 'C022012' : '汽車融資', 'C022020' : '機車', 'C022030' : '沙灘車', 'C022031' : '汽車服務相關', 'C022032' : '自動駕駛車', 'C022910' : '車輛整車', 'C022911' : '特種車輛相關', 'C022912' : '客貨車輛相關', 'C099050' : '自行車' } ],

     # [ '電子類', { 'C022052' : '車用電子', 'C022057' : '胎壓監測系統', 'C022058' : '倒車雷達', 'C022059' : '車載影音系統', 'C022067' : '行車紀錄器', 'C022068' : '倒車影像系統', 'C022069' : '抬頭顯示器(HUD)', 'C023015' : '面板業', 'C023020' : '中小尺寸面板', 'C023025' : 'TFT-LCD', 'C023026' : 'TN／STNLCD', 'C023031' : 'LCM', 'C023036' : '電子紙', 'C023037' : 'OLED', 'C023158' : '觸摸屏', 'C023016' : '面板零組件', 'C023027' : '背光源', 'C023029' : '偏光板', 'C023032' : '液晶', 'C023033' : '導電玻璃', 'C023034' : '玻璃基板', 'C023035' : '光學膜', 'C023038' : '玻璃基板加工', 'C023380' : '彩色濾光片', 'C023040' : 'LED', 'C023041' : 'LED晶粒', 'C023042' : 'LED封裝', 'C023043' : 'LED磊晶', 'C023045' : '紅外線傳輸模塊', 'C023046' : 'LED照明產品', 'C023047' : 'LED散熱基板', 'C023048' : '藍寶石基板', 'C023060' : '被動元器件', 'C023061' : 'MLCC', 'C023062' : '貼片電阻', 'C023063' : '電容', 'C023064' : '電阻', 'C023066' : '電感', 'C023067' : '石英組件', 'C023068' : '鋁質電解電容', 'C023069' : '被動元器件上游', 'C023071' : '鉭質電解電容', 'C023072' : '塑膠膜電容器', 'C023073' : '熱敏電阻', 'C023074' : '濾波器', 'C023075' : '振盪器', 'C023076' : '壓敏電阻', 'C023080' : '電子其它', 'C023375' : '無塵室工程', 'C023377' : '事務機器', 'C023379' : '辦公用品設備', 'C023725' : '智能卡相關', 'C015040' : 'UPS', 'C023050' : '電源供應器', 'C023051' : '變壓器', 'C023053' : '機殼表面處理', 'C023054' : '磁性材料', 'C023055' : '無線充電', 'C023070' : '機箱', 'C023120' : '連接器', 'C023130' : '其它零件', 'C023132' : '消費類電池', 'C023134' : '模具沖壓', 'C023135' : '散熱風扇電機', 'C023137' : '樞紐', 'C023139' : '電子零件組件', 'C023153' : '散熱模塊', 'C023154' : '鎂鋁合金外殼', 'C023155' : '熱導管', 'C023391' : 'DRAM模塊', 'C023393' : 'Flash模塊', 'C023530' : '連接線材', 'C023590' : '音響設備及零件', 'C023610' : '撥碼開關', 'C023156' : 'DRAM內存IC', 'C023157' : 'SRAM內存IC', 'C023159' : 'FLASH內存IC', 'C023162' : 'DSL芯片組', 'C023164' : '網卡IC', 'C023165' : '集線器IC', 'C023166' : '無線網絡IC', 'C023168' : '衛星導航芯片組', 'C023171' : '智能卡IC', 'C023172' : 'STBIC', 'C023173' : '圖形卡IC', 'C023174' : '調制解調器芯片組', 'C023176' : 'CPU', 'C023177' : 'DSP', 'C023178' : '馬達IC', 'C023179' : '電池保護IC', 'C023183' : '模擬IC', 'C023184' : 'IO控制IC', 'C023185' : '其他IC', 'C023189' : 'IC設計軟體', 'C023190' : 'IC設計', 'C023191' : '芯片組', 'C023192' : '網絡通訊IC', 'C023193' : 'LCD驅動IC', 'C023195' : '消費性IC', 'C023196' : '光驅驅動IC', 'C023197' : 'LCD控制IC', 'C023198' : 'PC外圍IC', 'C023199' : 'MCU', 'C023206' : '設計IP', 'C023207' : '影音IC', 'C023209' : 'ASIC', 'C023221' : '記憶卡IC', 'C023222' : 'CMOS芯片', 'C023223' : '嵌入式芯片', 'C023224' : '感測元件', 'C023225' : '生物識別芯片', 'C023226' : '高速傳輸芯片', 'C023227' : 'SSD主控芯片', 'C023228' : '電力線載波芯片', 'C023229' : '安防芯片', 'C023332' : 'LED驅動IC', 'C023333' : '數字電視IC', 'C023334' : '觸摸芯片', 'C023336' : 'MEMS', 'C023504' : '光通信芯片', 'C023200' : 'IC封裝', 'C023201' : 'IC測試', 'C023203' : 'IC封裝測試', 'C023204' : 'LCD驅動IC封裝', 'C023100' : '玻纖布', 'C023103' : '激光鑽孔機、鑽頭', 'C023105' : 'PCB原材料', 'C023152' : '撓性印製電路板', 'C023161' : '撓性覆銅板', 'C023210' : '印製電路板', 'C023211' : '覆銅板', 'C023212' : '銅箔', 'C023219' : '印製電路板相關', 'C023230' : '顯示器', 'C023231' : '投影機', 'C023232' : '投影機元件', 'C023235' : '顯示器元件', 'C023236' : '3D顯示相關', 'C023237' : 'LCD顯示器', 'C023238' : '數字看板', 'C023270' : '光盤', 'C023271' : '盤片預錄', 'C023273' : '網絡電話(VOIP)', 'C023274' : '無線網絡設備系統(WLAN)', 'C023280' : '通訊設備', 'C023283' : '電信設備', 'C023286' : '衛星通訊設備', 'C023287' : '資安設備', 'C023298' : '天線', 'C023310' : '接入設備', 'C023311' : '數據機', 'C023312' : '5G通訊設備', 'C023314' : '物聯網裝置', 'C023315' : '局域網絡', 'C023401' : '通訊設備零組件', 'C023402' : '衛星導航', 'C023403' : '小型衛星地面站', 'C023404' : '基站', 'C023405' : '網絡交換機', 'C023406' : '低噪聲降頻器', 'C023407' : '4G通訊設備', 'C023408' : 'RFID相關', 'C023409' : '近場通訊(NFC)', 'C023288' : '手機', 'C023293' : '手機製造', 'C023399' : '智能手機', 'C023285' : '電信/數據服務', 'C023290' : '通訊服務', 'C023502' : '移動通訊', 'C023350' : '計算機經銷商', 'C023351' : '通訊經銷商', 'C023352' : 'IC零組件經銷商', 'C023353' : '其它電子經銷商', 'C023357' : '3C通路商', 'C023358' : '半導體材料通路商', 'C023359' : '電子產品銷售管道', 'C023313' : '信息安全', 'C023340' : '系統集成', 'C023341' : '操作系統', 'C023342' : '電子支付', 'C023360' : '軟件', 'C023361' : '軟件包', 'C023363' : '數據庫', 'C023364' : '企業資源規劃', 'C023365' : '大數據', 'C023366' : '客戶關係管理', 'C023367' : '軟件銷售渠道', 'C023368' : '應用軟件', 'C023369' : '人工智能', 'C023371' : '虛擬現實', 'C023081' : '檢測驗證服務', 'C023104' : 'PCB其他設備', 'C023326' : '半導體設備', 'C023328' : 'IC檢測設備', 'C023370' : '設備儀器廠商', 'C023372' : 'LED設備', 'C023373' : '面板設備', 'C023374' : '觸摸屏設備', 'C023376' : '光伏設備', 'C023378' : '測量儀器', 'C023852' : '封測用設備', 'C023160' : '非易失性存儲器', 'C023170' : 'DRAM', 'C023180' : 'IC生產', 'C023181' : '晶圓代工', 'C023187' : '砷化鎵相關', 'C023319' : '光通信元件磊晶(光通信元件外延)', 'C023320' : '光罩', 'C023321' : '磊晶(外延)', 'C023322' : '硅晶圓', 'C023323' : '化合物晶圓', 'C023324' : '氧化物晶圓', 'C023329' : '藍寶石晶棒', 'C023390' : 'IC製造', 'C023394' : '分立器件', 'C023395' : '二極管', 'C023396' : '晶體管', 'C023400' : 'Internet應用與服務', 'C023411' : '搜索引擎', 'C023412' : '門戶網站', 'C023413' : '電商平台', 'C023416' : '社交網絡與媒體', 'C023417' : '流媒體', 'C023415' : '雲計算', 'C023418' : 'Internet技術與基礎設施', 'C023419' : '電商服務', 'C023030' : '圖像傳感器', 'C023420' : '數碼相機', 'C023421' : '數碼相機組裝', 'C023422' : '光學鏡片／頭', 'C023090' : '電話/傳真機', 'C023451' : '視頻轉換相關', 'C023457' : '平板電腦', 'C023458' : '語音助理', 'C023460' : '消費性電子產品', 'C023550' : '安全監控系統', 'C023722' : '視頻會議產品', 'C023723' : '電子書閱讀器', 'C023726' : '攝像設備', 'C023325' : '拋光液/墊', 'C023327' : '光刻膠', 'C023480' : '電子化工材料', 'C023220' : '掃瞄儀', 'C023240' : '鼠標', 'C023250' : '鍵盤', 'C023260' : '光驅／刻錄機', 'C023490' : '外圍產品', 'C023492' : '打印機', 'C023493' : '存儲卡', 'C023495' : '儲存設備', 'C023496' : '3D打印機', 'C023497' : '打印機耗材', 'C023580' : 'IC讀卡機', 'C023630' : '磁盤陣列控制單元', 'C023660' : '手寫板', 'C023680' : '硬盤相關', 'C023690' : '讀卡器', 'C016015' : '光纖光纜', 'C023500' : '光通信', 'C023505' : '光纖預製棒', 'C023996' : '光有源器件', 'C023997' : '光無源器件', 'C023998' : '光通信設備', 'C023999' : '光通信元件', 'C023727' : '穿戴式裝置', 'C023728' : '智能手錶', 'C023729' : '智能眼鏡', 'C023738' : '智能手環', 'C023730' : '光伏', 'C023731' : '光伏硅片', 'C023732' : '光伏電池', 'C023733' : '光伏電池模塊', 'C023734' : '光伏系統運用', 'C023735' : 'PVInverter', 'C023736' : '光伏導電漿料', 'C023737' : '光伏玻璃', 'C023739' : '光伏多晶硅', 'C023362' : 'PC遊戲', 'C023455' : '家用遊戲機', 'C023800' : '遊戲行業', 'C023801' : '博彩設備', 'C023803' : '移動遊戲/手機遊戲', 'C023136' : '手機震動電機', 'C023292' : '手機面板驅動IC', 'C023294' : '手機外殼', 'C023296' : '手機按鍵', 'C023335' : '手機芯片相關', 'C023423' : '手機相機模組', 'C023802' : '手機零組件', 'C023202' : '金、錫凸塊', 'C023208' : '探針、探針卡', 'C023330' : '引線框架', 'C023331' : 'IC基板', 'C023850' : '封測服務與材料', 'C023851' : '測試用板卡', 'C023297' : '受話器', 'C023880' : '電聲器件', 'C023881' : '耳機', 'C023882' : '微型揚聲器', 'C023885' : '麥克風', 'C023900' : '生物辨識相關', 'C023901' : '指紋辨識', 'C023902' : '人臉辨識', 'C023903' : '虹膜辨識', 'C023904' : '掌紋辨識', 'C023905' : '語音辨識', 'C023295' : '功率放大器', 'C023920' : '射頻前端芯片', 'C023921' : '低雜訊放大器', 'C023922' : '射頻開關', 'C023923' : '射頻前端模塊', 'C023140' : '台式機', 'C023145' : '服務器', 'C023150' : '筆記本電腦', 'C023151' : '筆記本電腦製造', 'C023300' : '主板', 'C023510' : '工控機', 'C023560' : '條碼掃描器', 'C023700' : '顯卡', 'C023702' : '准系統', 'C023721' : 'POS機', 'C023760' : '電子製造服務', 'C023990' : '計算機系統業', 'C023205' : 'USB', 'C023992' : '傳輸介面', 'C023993' : 'Thunderbolt', 'C023994' : 'Displayport', 'C023995' : 'HDMI' } ],
     # [ '建築地產類', { 'C025010' : '房地產開發', 'C025011' : '房屋中介', 'C025080' : '地產', 'C025092' : '物業投資發展', 'C025093' : '園區開發', 'C025095' : '物業管理服務', 'C025020' : '住宅建設', 'C025021' : '基礎建設', 'C025022' : '其他營造工程', 'C025023' : '幕牆工程', 'C025030' : '建築設計、修建裝潢', 'C025031' : '園林造景', 'C025032' : '水電消防工程', 'C025090' : '營造工程', 'C099160' : '工程顧問', 'C099191' : '環保工程' } ],
     # [ '運輸類', { 'C025900' : '基礎建設營運', 'C025910' : '公路', 'C025930' : '機場', 'C025940' : '港口', 'C026010' : '倉儲／貨柜場', 'C026020' : '貨柜航運', 'C026030' : '散裝航運', 'C026040' : '陸上運輸', 'C026050' : '空運', 'C026060' : '客運', 'C026061' : '水上運輸', 'C026062' : '油輪', 'C026063' : '鐵路運輸服務', 'C026990' : '運輸事業', 'C029030' : '物流業' } ],

     # [ '觀光休閒娛樂類', { 'C027010' : '旅館、餐飲', 'C027011' : '飯店', 'C027013' : '餐飲', 'C027014' : '渡假山莊', 'C027015' : '休閒食品零售', 'C027012' : '休閒娛樂', 'C027020' : '旅遊', 'C027021' : '主題樂園', 'C027022' : '博奕相關', 'C027024' : '電影院／劇院', 'C027025' : '俱樂部', 'C027026' : '陳列展覽相關', 'C027027' : '時尚產業', 'C027028' : '精品', 'C027029' : '美妝保養品', 'C027030' : '珠寶', 'C027040' : '美容', 'C099220' : '鐘表' } ],
     # [ '金融相關類', { 'C028010' : '銀行', 'C028020' : '壽險', 'C028030' : '產險', 'C028031' : '保險經紀', 'C028040' : '票據', 'C028050' : '証金公司', 'C028060' : '証券', 'C028070' : '信託投資公司', 'C028090' : '投資信托', 'C028091' : '房地產投資信託', 'C028100' : '金融控股', 'C028110' : '租賃', 'C028120' : '金融其它', 'C028121' : '資產管理', 'C028122' : '再保險', 'C028123' : '消費金融', 'C028990' : '金融業' } ],
     # [ '百貨通路類', { 'C027050' : '便利商店', 'C029001' : '流通業', 'C029010' : '百貨公司', 'C029020' : '貿易', 'C029021' : '書店', 'C029040' : '相片沖印', 'C029050' : '量販店、大賣場', 'C029060' : '藥品化妝品零售相關', 'C029070' : '連鎖超市', 'C029080' : '食品飲料相關通路', 'C029094' : '家居相關用品通路', 'C029095' : '免稅店', 'C029090' : '無店舖販售', 'C029091' : '郵購', 'C029092' : '直銷', 'C029093' : '電視購物' } ],

     # [ '公共建設類', { 'C015203' : '電力公共事業', 'C025920' : '水利', 'C025980' : '水資源', 'C025981' : '海水淡化', 'C025982' : '污水處理', 'C025983' : '水資源設備/耗材', 'C025960' : '駕駛培訓班', 'C099100' : '加油站', 'C099370' : '其他公用事業', 'C099371' : '停車場', 'C099372' : '交通標誌' } ],
     # [ '控股類', { 'C098020' : '控股公司' } ],
     # [ '生物醫藥類', { 'C017000' : '醫藥行業', 'C017011' : '化學藥', 'C017012' : '中藥', 'C017013' : '原料藥', 'C017014' : '新藥研發', 'C017015' : '植物新藥', 'C017016' : '生物製劑', 'C017017' : '維生素', 'C017023' : '醫藥研發外包服務', 'C017024' : '仿製藥', 'C017025' : '品牌藥', 'C017105' : '獸藥', 'C017116' : '醫藥流通', 'C017010' : '生物科技', 'C017018' : '生技特用化學品', 'C017019' : '農業生技', 'C017020' : '環保生技', 'C017021' : '生技服務', 'C017022' : '植物工廠', 'C017108' : '食品生技', 'C017100' : '醫療器械銷售管道', 'C017111' : '血糖儀', 'C017118' : '體外診斷產品', 'C017119' : '檢驗試劑／紙', 'C017121' : 'IVD檢驗儀器設備', 'C017106' : '生命科學工具', 'C017107' : '醫療信息技術', 'C017110' : '血壓計', 'C017112' : '體溫計', 'C017122' : '診斷與監測用醫材', 'C017123' : '生理監測裝置', 'C017124' : '生理檢測器材', 'C017125' : '醫學影像裝置', 'C017114' : '洗腎器具', 'C017126' : '手術與治療用醫材', 'C017127' : '物理治療器具', 'C017128' : '呼吸與麻醉用器具', 'C017129' : '放射治療設備', 'C017131' : '動力手術器具', 'C017132' : '其他手術器械', 'C017101' : '電動代步車', 'C017104' : '福祉輔助設備', 'C017113' : '隱形眼鏡', 'C017115' : '醫用植入材料', 'C017133' : '輔助與彌補用醫材', 'C017134' : '人造關節', 'C017135' : '牙科植入器材', 'C017136' : '骨科類器材', 'C017109' : '醫療耗材', 'C017137' : '其他醫療器械', 'C017138' : '個人保護用器材', 'C017139' : '醫用家具', 'C017103' : '醫療服務', 'C017141' : '醫療管理服務', 'C017142' : '醫療檢驗服務' } ],

     # [ '初級產業類', { 'C011020' : '農林漁牧', 'C011021' : '農產品種植', 'C011022' : '林業', 'C011023' : '漁業', 'C011024' : '食用菌種植', 'C011026' : '種子生產', 'C011028' : '水產養殖', 'C011029' : '畜牧業', 'C012018' : '家畜，家禽', 'C012023' : '飼料', 'C011027' : '礦石開採', 'C099355' : '礦產採掘服務' } ],
     # [ '航天軍工類', { 'C099340' : '航天軍工', 'C099341' : '衛星相關', 'C099342' : '航空器、飛機', 'C099343' : '太空飛行機械零組件', 'C099344' : '太空飛行通訊零組件', 'C099345' : '軍火工業' } ],
     # [ '能源類', { 'C013001' : '石油開採', 'C013002' : '煉油', 'C013003' : '頁岩油／氣', 'C013191' : '燃氣儲運／分銷', 'C013980' : '石油及天然氣', 'C099070' : '天然氣', 'C099110' : '油品儲運／分銷', 'C099351' : '油氣採掘設備與工程', 'C099354' : '油氣採掘服務', 'C099360' : '電力', 'C099361' : '火力發電', 'C099362' : '餘熱發電', 'C099363' : '地熱發電', 'C099364' : '水力發電', 'C099365' : '風力發電', 'C099366' : '核能發電', 'C099367' : '供熱', 'C099368' : '太陽能發電', 'C099369' : '發電設備與零組件', 'C099373' : '垃圾發電', 'C099410' : '煤', 'C099411' : '煤炭採選設備' } ],

     # [ '傳播出版類', { 'C099090' : '傳播事業', 'C099091' : '電視台', 'C099092' : '出版業', 'C099094' : '平面媒體', 'C099095' : '廣告', 'C099096' : '影音娛樂', 'C099097' : '有線電視', 'C099400' : '文化創意產業' } ],
     # [ '綜合類', { 'C098010' : '綜合' } ],
     # [ '傳統行業及其他行業類', { 'C018015' : '耐火建材', 'C099010' : '傳產其它', 'C099020' : '鞋業', 'C099021' : '鞋材', 'C099030' : '製罐', 'C099031' : '瓶蓋', 'C099093' : '印刷業', 'C099140' : '烤肉架', 'C099190' : '拉鍊', 'C099194' : '手提箱', 'C099200' : '玩具', 'C099210' : '底片', 'C099230' : '皮革製品', 'C099250' : '嬰童用品', 'C099260' : '眼鏡', 'C099270' : '眼鏡架', 'C099280' : '製帽', 'C099290' : '光學', 'C099300' : '文具', 'C099310' : '工藝品', 'C099320' : '金融機具', 'C099330' : '自動售貨機', 'C099331' : '寵物用品', 'C099332' : '樂器', 'C099333' : '複合材料', 'C099334' : '回收、焚化相關', 'C099335' : '煙草', 'C099336' : '木(竹)加工／製品', 'C099337' : '金屬加工／製品', 'C099338' : '工安產品', 'C099395' : '碳權相關', 'C099060' : '資產股', 'C017102' : '健身器材', 'C027023' : '運動競賽', 'C099150' : '高爾夫球杆頭', 'C099380' : '運動產業', 'C099381' : '運動服', 'C099382' : '運動鞋', 'C099383' : '運動用品', 'C099384' : '球具', 'C099385' : '球場', 'C099040' : '保安', 'C099390' : '服務業', 'C099391' : '消費者服務', 'C099392' : '商業服務／顧問', 'C099393' : '教育事業', 'C099394' : '人力資源', 'C099396' : '殯葬服務', 'C099397' : '婚宴顧問', 'C099398' : '清潔服務' } ],
    ]

    # 建立寫入資料表的資料
    sql_insert = []
    for list in NewkindIDNameStr:
        for key in list[1]:
            #print(key, list[1][key])
        
            stock_names = get_stock_names(key)      # 取得股票名稱和代碼

            # 有可能是空的，就換下一個"細產業".
            if not stock_names:
                time.sleep(1)
                continue

            # 打印結果。產業別、細產業的訊息是在 list[0] 和 list[1][key] 中
            for code, name in stock_names:
                print(f"股票代碼: {code}, 股票名稱: {name}, 産業: {list[0]}, 類別: {list[1][key]}")

                # 每筆都是 list
                sql_insert.append( [code, name, list[0], list[1][key]] )    # "序號"會自動增加，不用寫入

            time.sleep(5)

    # 將資料存入資料庫，"序號"會自動增加，不用寫入
    add_to_sql = f"insert into {table_name} ( `證券代號`, `證券名稱`, `産業別`, `細産業` ) values (%s, %s, %s, %s)"   

    conn = get_mysql_connection()
    cursor = conn.cursor()
    cursor.executemany(add_to_sql, sql_insert) 
    cursor.close()
    conn.commit()


# 建立 mysql 資料表，試著在欄位部份使用中文
def create_industrial_table(table_name: str): 
    sql = f"""CREATE TABLE `{table_name}`(
        序號 int NOT NULL AUTO_INCREMENT comment '序號',
        證券代號 varchar(10) NOT NULL comment '證券代號',
        證券名稱 varchar(255) NOT NULL comment '證券名稱',
        産業別 varchar(255) NOT NULL comment '産業別',
        細産業 varchar(255) NOT NULL comment '細産業',
        PRIMARY KEY (序號)
        );
    """

    result = search_table_exist(table_name)
    if result:
        print(f'{table_name} 已存在！')
        return

    conn = get_mysql_connection()
    cursor = conn.cursor()

    cursor.execute(sql)

    cursor.close()
    print(f'已新增 {table_name}！')
    conn.close()
    


# 尋找 table_name 是否存在
# 原來找到的語法可能因為模組實作的問題而無法使用，
# 所以 w3cschool 才會提供用 show tables 來找
def search_table_exist(table_name: str) -> bool:
    conn = get_mysql_connection()
    cursor = conn.cursor()
    sql = "SHOW TABLES;"
    # mysql workbench 可以執行的語法，但 pymysql 會有問題
    # sql = f"""SELECT EXISTS ( SELECT * FROM information_schema.tables WHERE table_schema = 'stocktrading' AND table_name = `{table_name}` );"""

    cursor.execute(sql)
    tables = cursor.fetchall()

    cursor.close()
    conn.close()

    # 在 tuple 找出 table_name
    find = [table for table in tables if table[0] == table_name]       # 沒找到是空的
    if len(find) == 0:
        print(f"{table_name} 不存在！")
        return False
    
    print(f"找到 {table_name}")
    return True



# Connect to the database
def get_mysql_connection():
    # 依照自己的設定修改
	return mysql.connector.connect(
		host="127.0.0.1",
		port=3306,
		user="twsetrading",
		password="YOUR_PASSWORD_記得修改",
        db="twse_stock",
		charset="utf8mb4"
	)


if __name__ == '__main__':
    # 結合 get_stock_names() 和 create_industrial_table()，將產業分類表格存入資料庫
    create_industrial_table( 'stock_classification' ) 

    get_stock_url( 'stock_classification' )

