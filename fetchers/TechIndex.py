import requests, json, time, re
from datetime import datetime
from mongo import MongoConn, MONGODB_CONFIG
from sender import send_message
from fetcher import create_new_fetcher, ExitSignal
from filter import create_new_filter
from bs4 import BeautifulSoup
from utils import GMT_to_local

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36',
    'Accept': '*/*',
}
ALL_BELOW_21_1 = ['railway-signal-communication-ltd', 'china-national-nuclear-power-co-ltd', 'zijin-mining',
                  'nari-tech', 'huaneng-lancang-river-a', 'jinfeng-invest', 'southern-air', 'hedy-holding-a',
                  'new-hope-liuhe-a', 'orient-securities-co-ltd', 'sh-electric-ss', 'china-molybden',
                  'bank-of-jiangsu-co-ltd', 'china-east-air-ss', 'great-wall-mot', 'cn-power-const', 'baotou-steel',
                  'rongsheng-a', 'cn-coal-energy', 'huajing', 'bank-of-nanjin', 'aluminium-corp', 'china-oilfield-ss',
                  'tongwei', 'metallurgical', 'hongta-securities-co-ltd', 'china-cosco', 'sinotex-invest', 'lujiazui',
                  'chinese-town-a', 'xj-goldwind-a', 'jpmf-guangdong-a', 'founder-securi', 'zheneng-elec-p',
                  'zhejiang-century-huatong', 'shanghai-pharm', 'yanzhou-coal', 'gemdale', 'ningbo-port',
                  'datang-power', 'jiangsu-exp', 'jiangxi-copper-ss', 'everbright', 'dahua-tech-a',
                  'merchant-express-a', 'china-great-wall', 'gd-power', 'avic-aircraft-a', 'longsheng',
                  'jiangxi-zhengbang-technology-co-ltd']
ALL_BELOW_21_2 = ['cgn-power', 'boe-technology-a', 'east-money-information', 'great-wall-com-a', 'agri-bank-of-c',
                  'jpmf-guangdong-a', 'cn-shipbuildin', 'icbc-ss', 'shuang-ta-food-a', 'baotou-steel', 'eagle-mining',
                  'zijin-mining', 'dakang-farming-a', 'wintime-energy', 'tcl-corp-a', 'hongta-securities-co-ltd',
                  'ping-an-bank-a', 'green-hitech-a', 'huakong-seg-a', 'hyron-software-a', 'red-arrow-a',
                  'hedy-holding-a', 'longsheng', 'lifan-industry', 'shenzhen-h-t-a', 'js-kingfield-a',
                  'wuhu-token-sciences', 'zheguangsha', 'xcmg-machinery-a', 'jiangxi-zhengbang-technology-co-ltd',
                  'beijing-vrv-software-corp-ltd', 'chunxing-pre-mec-a', 'aerospace-elec', 'n.-china-pharm',
                  'shenzhen-kaifa-a', 'o-film-tech-a', 'huatian-tech-a', 'dabeinong-tech-a', 'united-network',
                  'goertek-a', 'freetrade-tech', 'haitong-sec-ss', 'hebang-corp', 'cssc-steel', 'shenzhen-seg-a',
                  'first-capital-securities-a', 'huachang-chem-a', 'zhenjiang-dongfang-electric-heat', 'heungkong-hold',
                  'cs-zoomlion-a']
ALL_BELOW_21_3 = ['navinfo-a', 'anhui-shengyun-environment-protect', 's-goldleaf-jewel-a', 'huatai-securit',
                  's-beiya-ind', 'anxin-trust', 'sealand-securiti-a', 'petrochina-ss', 'sz-ch-bicycle-a',
                  'changjiang-ele', 'beijing-jetsen-tech-co', 'jilong-gold', 'bank-of-comm', 'luxin-packing-a',
                  'huaneng-lancang-river-a', 'shaanxi-trust-a', 'sanan-optoelec', 'gezhouba', 'sichuan-gaojin-a',
                  'realcan-pharm-a', 'twin-tower-a', 'zh-semicon-a', 'sz-capstone-a', 'shenzhen-sdg-information-co-ltd',
                  'foxconn', 'suning-commerce-a', 'aerospace-comm', 'pangda-automob', 'weichai-power-a',
                  'citic-heavy-in', 'shandong-iron', 'jiangsu-hoperun-software', 'industrial-sec', 'raas-blood-a',
                  'kangqiang-elect-a', 'china-harzone-industry', 'shanghai-const', 'railway-signal-communication-ltd',
                  'metallurgical', 'start-group', 'ningbo-tech-a', 'china-publishing-media', 'tontec-tech',
                  'guangdong-bobaolon-co-ltd', 'changlin', 'linzhou-mach-a', 'zhongnan-cons-a', 'bank-of-suzhou',
                  'sunbird-yacht', 'hongxing-steel']
ALL_BELOW_21_4 = ['guangdong-huasheng-electrical-a', 'chongqing-lummy-pharmaceutical', 'beijing-bank', 'zhongjin-gold',
                  'jihua-group', 'changchun-dep', 'zhongtian-tech', 'join-cheer-soft-a', 'dahua-tech-a',
                  'huahai-pharma', 'tongyu-heavy-industry', 'taigang-a', 'jingxin-pharm-a', 'jinjian-cereal', 'yinge',
                  'china-great-wall', 'shunrong-auto-a', 'victoryprecision-a', 'jiangxi-huawu-brake', 'jingui-silver-a',
                  'tongwei', 'guangzhou-ship', 'cpt-tech-group-a', 'lecron-energy-saving-materials',
                  'holitech-technology-co-ltd', 'shenghua-biok', 'gold-seed-wine', 'dunhuang-seed', 'gf-securities-a',
                  'baoan-real-estate-a', 'dhc-software-a', 'huayi-brothers-media-corp', 'beijing-enlight-media',
                  'beifang-chuang', 'shenzhen-riland-industry-co', 'rare-earth', 'sunwoda-electronic',
                  'caitong-securities', 'baiyin-nonferrous-group-co-ltd', 'guangtai-equip-a', 'sungrow-power-supply',
                  'rongtai', 'bohai-leasing-a', 'meidu', 'xuzhou-wuyang-technology', 'ningbo-huaxiang-a',
                  'shanghai-kingstar-winning-software', 'sh-belling', 'chengdu-santai-holding-group-co-ltd',
                  'cn-coal-energy']
ALL_BELOW_21_5 = ['jiangsu-sanyou-group-co-ltd', 'hainan-airline', 'xinjiang-machinery-research-inst',
                  'zhejiang-dehong-automotive-electric', 'zhongzhu-holdi', 'nanjing-securities-co', 'western-mining-co',
                  'air-china-ss', 'gd-power', 'haige-communicat-a', 'shenzhen-sunwin-intelligent',
                  'shenwan-hongyuan-group-co-ltd', 'anhui-shenjian-new-materials-co-ltd', 'sunnada-comm-a',
                  'yonghui-stores', 'ming-yang-smart-energy-group', 'softto-a', 'jiangsu-nata-opto-electr-material',
                  'xinchao-indust', 'china-galaxy-securities-co-ltd', 'huaxi-securities-a', 'ht-opticelectr',
                  'aluminium-corp', 'greattown', 'jiangsu-dagang-a', 'north-navigati', 'jinhua-chemical-a',
                  'zhejiang-runtu-a', 'shanxi-zhendong-pharmaceutical', 'huadian-power', 'aerospace-h-tech-a',
                  'xinan-chemical', 'wuhan-ps-information-tech', 'citic-guoan-a', 'kaile', 'yuguang',
                  'humon-smelting-a', 'dongguan-kingsun-optoelectron-a', 'zhiguang-elec-a', 'hongdu-avia',
                  'jinling-mining-a', 'soochow-securi', 'yunnan-tin-a', 'cn-railway-grp', 'bank-of-nanjin',
                  'huadong-tech-a', 'pci-suntek-tec', 'guangshen-rail-ss', 'chenzhou-mining-a', 'yunnan-alumin-a']
ALL_BELOW_21_6 = ['foton-motor', 'renhe-pharm-a', 'zhongchangmari', 'sailun', 'southern-air', 'shenzhen-mys-a',
                  'beijing-shouhang-resou-saving-a', 'broad-ocean-a', 'risen-energy', 'sz-coship-elect-a',
                  'xj-goldwind-a', 'chengxing-chem', 'avic-heavy', 'anhui-great-wall-military-industry',
                  'shenzhen-everwin-precision-tech', 'daqin-railway', 'guizhou-tyre-a', 'haite-high-tech-a',
                  'netposa-technologies-ltd', 'liaoning-hongyang', 'zixin-pharm-a', 'net263-a', 'taier-heavy-ind-a',
                  'yango-a', 'sz-sunlord-elec-a', 'gosuncn-a', 'xibei-bearing-a', 'beijing-etrol-tech', 'qingdao-haier',
                  'zz-mining-mach', 'gcl-system-integration-technology', 'western-region-gold-co-ltd',
                  'hand-enterprise-solutions-co', 'shaanxi-jr-fire-protection', 'csr-corp', 'shandong-mining-a',
                  'sw-securities', 'goworld-a', 'zhejiang-sanhua-co-ltd', 'kingenta-eco-a',
                  'guotai-junan-securities-co-ltd', 'yanjing-brewery-a', 'shaanxi-coal', 'sh-intl-port', 'conba',
                  'dali-technology-a', 'hebei-steel-a', 'pgvt-a', 'zhejiang-jinke-peroxides-co-ltd', 'fengle-seed-a']
ALL_BELOW_21_7 = ['titan-wind-energy-suzhou', 'taiji-indust', 'new-century-a', 'guanlu-a', 'shaanxi-heimao',
                  'cn-first-heavy', 'huaren-pharma', 'hongda-xingye-a', 'aerospace-auto', 'kingteller-tech-a',
                  'sh-jiabao', 'keybridge-com-a', 'bluedon-info-security-tech', 'bbmg-corp', 'shenzhen-mtc-a',
                  'huaxin-cement', 'chinese-town-a', 'china-east-air-ss', 'shengda-mining-a', 'shenzhen-infogem',
                  'yangtze-power', 'shenzhen-liantronics', 'lanzhou-ls-heavy-equipment-co', 'wonders-information',
                  'tianyuan-tech-a', 'jiangsu-jin-tong-ling-fluid-mach', 'huafang', 'changhong-elec',
                  'fujian-superpipe', 'jiangsu-dewei-materials', 'yili-energy', 'donghua', 'das-intellitech-a',
                  'microelect', 'huajing', 'beijing-philisense-tech', 'sz-airport-a', 'shenzhen-refond-optoelectronics',
                  'avit', 'science-city-a', 'suzhou-tianma-specialty-chem', 'strong-year', 'fangda', 'yn-germanium-a',
                  's-tianjin-mari', 'lens-technology-co-ltd', 'hangzhou-century', 'tengda-constr', 'hisoar-pharm-a',
                  'sumavision-technologies']

ALL_BELOW_21_8 = ['erfangji', 'zhongjin-a', 'anshan-senyuan-road-bridge', 'new-sea-union-a', 'techo-telecom-a',
                  'konka-a', 'taiya-shoes-co-ltd', 'crystal-optech-a', 'harbin-hi-tech', 'jinfeng-invest', 'surekam-a',
                  'zhengtong-elec-a', 'baoshan-steel', 'fenghuo-elec-a', 'harbin-hatou', 'beijing-sinnet-tech',
                  'ningbo-yak-tech-a', 'victor-on-text-a', 'valin-steel-a', 'akcome-solar-a', 'heihua', 'ronghua-ind',
                  'nanjing-panda', 'xiamen-anne-corp-ltd', 'ygsoft-a', 'shenzhen-dvision-video-communica', 'ourpalm',
                  'chengdu-techcent-environment', 'sz-topband-a', 'ningbo-port', 'china-shipping',
                  'yantai-zhenghai-magnetic-mat', 'beijing-jiaxun-feihong-electrical', 'jian-feng-chem-a',
                  'kunming-longjin-pharma', 'py-refractories-a', 'meihua-holding', 'brilliance-tech', 'xinhu-zhongbao',
                  'zheneng-elec-p', 'sinosun-tech', 'eternal-asia-a', 'b-soft-co-ltd', 'guangdong-hongda-blasting-a',
                  'aero-engine-ctrl-a', 'swan-fiber-co-ltd', 'yin-he-elec-a', 'hongtu-hi-tech',
                  'shanxi-baiyuan-trousers-chain-a', 'cnnc-hua-yuan-a']

ALL_BELOW_21_9 = ['feilo-acoustic', 'yunsheng', 'huilong-agri-pro-a', 'grinm-material', 'pudong-dev', 'northeast-sec-a',
                  'citic-helicop-a', 'rongxin-power-electronic-co-ltd', 'zhejiang-huatie-construction-safety',
                  'tellhow', 'sichuan-troy-information-tech', 'orient-securities-co-ltd', 'eastcompeace-a',
                  'zhongtian-urban-a', 'junzheng-ene-c', 'kyland-tech', 'danfu-compressor-a', 'yatai-pharm-a',
                  'surfilter-network-tech', 'xishan-coal-a', 'fj-nanping-sun-a', 'aerosun-corp',
                  'elefirst-science-tech', 'zhonghang-electronic-measuring-inst', 'guangdong-hongteo-accurate-tech',
                  'nanfang-pump-industry', 'yangquan-coal', 'fujian-snowman-a', 'org-packaging-a', 'susino-umbrella-a',
                  'gold-jade', 'changyuan', 'v-v-food---bev', 'ba-yi-steel', 'luxi-a',
                  'shenzhen-yitoa-intelligent-control', 'golden-horse-a', 'advanced-a', 'linewell-software-co-ltd',
                  'tianma-microelec-a', 'beijing-baofeng-technology', 'shenyang-mach-a', 'souyute-fashion-a',
                  'tatwah-smartech-co-ltd', 'zhenhua-tech-a', 'dongfang-elec-ss', 'hi-target-navigation-tech-co',
                  'guoguang-elec-a', 'shenwu-environmental-tech', 'yq-sea-cucumber-a']
ALL_BELOW_21_10 = ['shanghai-kinetic-medical-co', 'chinalin-securities', 'sinotrans-a', 'chengfa-tech',
                   'cn-avic-avioni', 'hengkang-medical-a', 'hangzhou-shunwang-tech', 'insigma', 'tiancheng',
                   'wuhu-port', 'dayuan-chem', 'china-cosco', 'boyun-new-mat-a', 'joincare', 'huaan-securities-co-ltd',
                   'beijing-cisri-gaona-materials-tech', 'china-ship', 'gemdale', 'selen-sci-tech-a', 'tongfang',
                   'changjiang-sec-a', 'sz-woer-a', 'bi-of-oriental-nations', 'aerospace-cf',
                   'nantong-metalforming-equipment', 'yankon-group', 'china-shenhua', 'zhejiang-kan-a',
                   'kaiser-china-holding-co-ltd', 'huaying-agri-a', 'nanjing-steel', 'chengdu-xiling-power-a',
                   'xingfa-chem', 'roshow-technology-co-ltd', 'tianshan-wool-a', 'hisun-pharm',
                   'centre-testing-intl-shenzhen', 'guofeng-plast-a', 'nationz-technologies-inc', 'cn-chemical',
                   'hunan-er-kang-pharmaceutical', 'juli-sling-a', 'tangshan-port', 'hengshun-vineg',
                   'jinjia-printing-a', 'huachangda-intelligent', 'tianguang-fire-fighting-co-ltd',
                   'shenzhen-sunline-tech', 'talkweb-info-sys-a', 'everbright']
WINE_BELOW_21 = ['yanjing-brewery-a', 'yantai-changyu-pioneer-wine', 'anhui-yingjia-distillery-co-ltd',
                 'zhujiang-brewery-a', 'hs-laobaigan', 'shanghai-bairun-a', 'yilite', 'guyuelongshan',
                 'jinhui-liquor-co-ltd', 'qinghai-huzhu-barley-wine-a', 'gold-seed-wine', 'kuaijishan',
                 'wei-long-grape-wine-co-ltd', 'jinfeng-wine', 'citic-guoan-vi', 'gansu-mogao', 'tonghua-wine',
                 'huiquan-brew', 'lan-huanghe-a', 'tibet-galaxy-a']
SEMI_BELOW_21 = ['huatian-tech-a', 'circuit-tech-a', 'silan-microele', 'changjiang-ele', 'sanan-optoelec',
                 'zh-semicon-a', 'kangqiang-elect-a', 'sunbird-yacht', 'sh-belling', 'wuhan-ps-information-tech',
                 'risen-energy', 'gcl-system-integration-technology', 'goworld-a', 'taiji-indust', 'aerospace-auto',
                 'microelect', 'hangzhou-century', 'akcome-solar-a', 'grinm-material', 'tellhow',
                 'tatwah-smartech-co-ltd', 'nationz-technologies-inc', 'datang-telecom', 'bomin-electronics-co-ltd',
                 'zhuhai-orbita-control-eng', 'topraysolar-a', 'nt-microelectron-a', 'suzhou-good-ark-a',
                 'shenzhen-mason-technologies-a', 'chaohua-tech-a', 'shenzhen-jufei-optoelectronics',
                 'shenzhen-suntak-circuit', 'shenzhen-changfang-light-emitting', 'victory-giant-technology-huizhou-co',
                 'olympic-circuit-technology-co-ltd', 'hubei-dinglong-chemical', 'yangzhou-yangjie-electronic',
                 'zhejiang-xinneng-photovoltaic-tech', 'zongyi', 'ellington-elec', 'wuhan-tianyu-info-industry',
                 'jiangsu-jiejie-microelectronics', 'focus-lightings-tech', 'lianchuang',
                 'jiangsu-huasheng-tianlong-photo', 'jingyuntong-te', 'nationstar-a', 'dongguang-micro-a',
                 'zhejiang-sunflower-light-energy', 'mls-co-ltd']
ALL_BELOW_21_11 = ['dikang-pharm', 'sinoma-science-a', 'zongshen-power-a', 'jiangsu-changshu-rural-commercial-b',
                   'datang-telecom', 'sh-dazhong', 'tj-tianbao-a', 'jiangxi-sanchuan-water-meter', 'shanying-paper',
                   'bomin-electronics-co-ltd', 'shangfeng-cement-a', 'sgis-a', 'tianan-coal', 'misho-ecology-landscape',
                   'hainan-zhenghe', 'beijing-ultrapower-software', 'focused-photonics-hangzhou-inc', 'tecon-animal-a',
                   'xingyuan-environment-tech', 'guangdong-eastone-century', 'qilianshan', 'neusoft-corp',
                   'faw-xiali-a', 'guangzheng-steel-a', 'luan-env-ener', 'beijing-jingxi-culture-a',
                   'jiangsu-welle-environmental', 'ctv-media', 'hs-laobaigan', 'kingsignal-tech',
                   'leyard-optoelectronic', 'shenzhen-terca-a', 'dalian-rubber', 'brother-enterpri-a', 'fudan-forward',
                   'eastern-investment-a', 'chengdu-corpro-technology-co-ltd', 'merchants-ship', 'guanfu-co-ltd-a',
                   'shenzhen-gongjin-electronics', 'ccoop-group', 'senyuan-electric-a', 'shenglu-telecom-a',
                   'zhongken-agri', 'cts-logistics', 'hytera-communica-a', 'faw-car-a', 'zhuhai-orbita-control-eng',
                   'invengo-a', 'huifeng-agrochem-a']
ALL_BELOW_21_12 = ['southwest-phar', 'jiangsu-zijin-rural-commercial-bank', 'shen-huo-a', 'gd-advertising-a',
                   'changshu-tianyin-electromechan', 'broadcast---tv', 'new-wellful', 'orient-group',
                   'grg-banking-equipment-co-ltd',
                   'china-baoan-group-co-ltd', 'topraysolar-a', 'huaye', 'jiangsu-shagang-a', 'eastern-comms',
                   'dr.-peng',
                   'jidong-cement-a', 'huizhou-speed-wireless', 'jinxinnong-feed-a', 'risesun-real-est-a',
                   'kunming-pharm', 'baoshuo',
                   'dalian-daxian', 'norinco-a', 'dongguan-eontec', 'shenzhen-ysstech-info-tech',
                   'shenzhen-huapengfei-logistics',
                   'xinyu-iron', 'harbin-gloria-pharmaceuticals', 'zheshang-securities',
                   'dalian-huarui-heavy-industry-a',
                   'meiyan-jixiang', 'yunnan-xiyi-ind-a', 'beijing-andawell-a', 'huaneng-power', 'wuhan-fingu-a',
                   'chongqing-stee',
                   'central-china-securities-co-ltd', 'shenzhen-fenda-technology-a', 'liuguo-chem', 'soyea-a',
                   'bank-of-shanghai-co-ltd',
                   'binjiang-re-a', 'tibet-summit', 'mengdian', 'shanghai-pharm', 'int-industry-a', 'yantai-tayho-a',
                   'aerospace-pwr',
                   'founder-securi', 'china-national-nuclear-power-co-ltd']
ALL_BELOW_21_13 = ['rastar-group', 'tdg-holding', 'sinovel-wind-g', 'tongling-jingd', 'denghai-seeds-a', 'capital-dev',
                   'dongfang-precisn-a', 'cn-metal-eng-a', 'tronly-new-electron-materials', 'baichuan-chem-a',
                   'sino-platinum',
                   'lanhua-sci-tec', 'zhejiang-firstar-panel-tech', 'sinotex-invest', 'yunnan-copper-a',
                   'hualing-xingma',
                   'janus-dongguan-precision', 'beijing-sojo-electric-co-ltd', 'zhongsheng-pharm-a',
                   'shenzhen-tianyuan-dic-info-tech',
                   'wuzhou-comm', 'dmegc-magnetics-a', 'bj-capital', 'henan-kedi-dairy-industry-co-ltd',
                   'cn-commu-cons', 'dongbao-pharm',
                   'zhongda-group', 'xuzhou-combustion-control-tech', 'gi-technologies-beijing',
                   'duzhe-publishing---media-co-ltd',
                   'sinolink-sec', 'tianshan-cemen-a', 'changshu-ruite-electric', 'cyts-tours', 'guanghui-energ',
                   'maanshan-iron-ss',
                   'jinling', 'wanxiang-donee', 'china-oilfield-ss', 'jianglong-shipbuilding', 'jinyu-group',
                   'hz-hangyang-a', 'haibo',
                   'greatoo-a', 'hualu-hs-chem', 'nt-microelectron-a', 'tiandi-tech', 'shenzhen-xinguodu-tech',
                   'suzhou-jinfu-new-material-co', 'suzhou-good-ark-a']
ALL_BELOW_21_14 = ['shenzhen-mason-technologies-a', 'hongda-mining', 'tangel-publishing', 'zhejiang-med',
                   'suplet-power', 'dongxing-securities', 'veken-elite', 'sz-textile-a', 'ganfeng-lithium-a',
                   'xinmin-textile-a', 'cn-citic-bank', 'xinmao-sci-tech-a', 'guosen-securities-co-ltd', 'gem-year-ind',
                   'yuanxing-energy-a', 'bank-of-jiangsu-co-ltd', 'qiming-info-tech-a', 'gpro-titanium-a',
                   'gohigh-data-a', 'neptunus-bioen-a', 'sh-electric-ss', 'shanxi-coal', 'jinduicheng',
                   'orient-landscape-a', 'maling', 'zj-dilong-a', 'unilumin', 'canny-elevator-a',
                   'western-securities-a', 'china-merchant', 'tang-sanyou', 'beijing-miteno-communication',
                   'qingdao-rural', 'china-tianying-inc', 'beyondsoft-a', 'beijing-chinese-digital-publis',
                   'tianjin-pengling-rubber-hose', 'shenzhen-jiawei-lighting', 'huaxicun-a', 's-yizheng-chem',
                   'nanjing-dept', 'sz-zero-seven-a', 'shenzhen-tatfook-tech', 'changan-auto-a',
                   'lander-real-estate-co-ltd', 'jiangxi-cement-a', 'boomsense-tech', 'sichuan-road', 'jiuzhitang-a',
                   'hubei-biocause-pharmaceutical']
ALL_BELOW_21_15 = ['yifan-xinfu-a', 'cashway-tech', 'huajin-chemical-a', 'shanxi-security-a',
                   'beijing-sanju-environmental', 'ju-hua', 'yongda-group-a', 'quanchai-eng', 'chaohua-tech-a',
                   'oriental-yuhong-a', 'fangsheng-phara', 'shenzhen-jufei-optoelectronics',
                   'shanghai-runda-medical-technology-c', 'sansteel-mg-a', 'china-hi-tech', 'avcon-information-tech',
                   'zhangjiagang-furui-special-equip', 'beijing-wkw-automotive-parts-a', 'hwa-create-corp-ltd',
                   'fuchun-tech', 'yunnan-chihong', 'universal-scie', 'befar-group', 'corun-new-ener', 'xinri-hengli',
                   'huawei-culture', 'zhejiang-jingu-a', 'sh-morn-elec-a', 'well-lead-medical-co-ltd',
                   'yunhai-metals-a', 'hubei-kailong-chemical', 'wanwei-hi-tech', 'dima-industry', 'keda-group',
                   'clou-elect-a', 'yihua-real-est-a', 'zhongtai-chem-a', 'shandong-longda-meat-foodstuff-a',
                   'zhejiang-century-huatong', 'ruize-material-a', 'sun-paper-a', 'suzhou-anjie-technology-a',
                   'joyson-electro', 'beijing-originwater-technology', 'dfd-chemical-a', 'wanda-cinema-line-corp',
                   'honyu-wear-resistant-new-materials', 'lianyungang-po', 'beijing-highlander-digital-technolo',
                   'enjoyor']

GUOFANG_BELOW_21 = ['avic-electro-a', 'avic-aircraft-a', 'north-navigati', 'hongdu-avia', 'aero-engine-ctrl-a',
                    'chengfa-tech', 'cn-avic-avioni', 'boyun-new-mat-a', 'beijing-cisri-gaona-materials-tech',
                    'beijing-andawell-a', 'ligeance-mineral-a', 'electro-optic', 'up-optotech-a']
SHARE_URL_LIST = ALL_BELOW_21_15 + ALL_BELOW_21_14 + ALL_BELOW_21_13 + ALL_BELOW_21_12 + ALL_BELOW_21_11 + \
                  ALL_BELOW_21_10 + ALL_BELOW_21_9 + ALL_BELOW_21_8 + ALL_BELOW_21_7 + ALL_BELOW_21_6 + ALL_BELOW_21_5 + ALL_BELOW_21_4 + \
                  ALL_BELOW_21_3 + ALL_BELOW_21_2 + ALL_BELOW_21_1
SHARE_URL_LIST2 = ALL_BELOW_21_14
URL = "https://cn.investing.com/equities/"
TICK = 1
PLACE = {"上海": "sh", "深圳": "sz"}


def strategy_multi_MA(self, code, name, MA5, MA10, MA20, MA50):
    """
    使用移动MA5,10,20,50依次按顺序排列，表示多头并进，视为买入信号
    :return:
    """

    if MA5 > MA10 and MA10 > MA20 and MA20 > MA50:
        print("-->检查策略MA", code, name, MA5, MA10, MA20, MA50, "符合")
        self.add({"code": code, "name": name})
    else:
        pass


def Share_prepare(self):
    self.conn = MongoConn(config=MONGODB_CONFIG)
    self.coll = self.conn.get_coll("share_tech_coll")
    self.cur_share_idx = 0
    self.cur_share = SHARE_URL_LIST[self.cur_share_idx]
    self.c = 0

    self.pool = []

    self.f = create_new_filter("MA", strategy_multi_MA)()


def Share_work(self):
    # print("Make a request Share", URL + self.cur_share + "-technical")
    r = requests.get(url=URL + self.cur_share + "-technical", headers=HEADERS, timeout=5)

    if r.status_code != 200:
        raise Exception
    else:
        self.c = 0
    soup = BeautifulSoup(r.text, 'html.parser')

    tech_list = soup.select("#curr_table")[1].tbody.find_all("tr", )[0:-1]
    _info = {}
    buy_c, sell_c, is_chaomai = 0, 0, False
    for i in tech_list:
        __index = i.find_all('td')[0].string
        __value = i.find_all('td')[1].string
        __signal = i.span.string.strip()
        _info[__index] = {"value": __value, "signal": __signal}
        if __signal == "购买":
            buy_c += 1
        elif __signal == "出售":
            sell_c += 1
        elif __signal == "超买":
            is_chaomai = True
    MA_list = soup.select("#curr_table")[2].tbody.find_all("tr", )[0:-1]
    for i in MA_list:
        __index = i.find_all('td')[0].string
        __1 = i.find_all('td')[1]
        __2 = i.find_all('td')[2]
        __signal_std = __1.span.string.strip()
        __signal_move = __2.span.string.strip()
        _info[__index + "标准"] = {"value": __1.text.strip().split("\n")[0], "signal": __signal_std}
        _info[__index + "移动"] = {"value": __2.text.strip().split("\n")[0], "signal": __signal_move}

        if __signal_std == "购买":
            buy_c += 1
        elif __signal_std == "出售":
            sell_c += 1
        elif __signal_std == "超买":
            is_chaomai = True
        if __signal_move == "购买":
            buy_c += 1
        elif __signal_move == "出售":
            sell_c += 1
        elif __signal_move == "超买":
            is_chaomai = True

    _info["summary"] = {"buy": buy_c, "sell": sell_c}
    _date = soup.find_all("span", class_="h3TitleDate")[0].string
    _place = soup.find_all("i", class_="btnTextDropDwn arial_12 bold")[0].string
    _title = re.search(r"\d{6}", soup.find_all("h1", class_="float_lang_base_1 relativeAttr")[0].string, ).group()
    _name = soup.find_all("i", class_="btnTextDropDwn arial_12 bold")[0].string + "_" + \
            soup.find_all("h1", class_="float_lang_base_1 relativeAttr")[0].string
    _code = PLACE[_place] + _title
    print(_name, _code)
    if buy_c > 21:
        print("-->", GMT_to_local(_date), _name, _code, buy_c)
        self.pool.append(_code)
    self.coll.update({"name": _name}, {'$set': {"date": _date, "info": _info}}, upsert=True)

    # strategy_multi_MA
    MA_value_list = [float(i.find_all('td')[2].text.strip().split("\n")[0]) for i in MA_list]
    MA5, MA10, MA20, MA50 = MA_value_list[0:4]
    self.f.work(name=_name, code=_code, MA5=MA5, MA10=MA10, MA20=MA20, MA50=MA50)

    if self.cur_share_idx == len(SHARE_URL_LIST) - 1:
        self.f.result()
        # 求交集
        MA_result = self.f.codes()
        Index_result = self.pool
        result = list(set(MA_result) & set(Index_result))
        self.result = result
        """
        print("######Result:")
        for s in result:
            print(s)
        """
        raise ExitSignal

    self.cur_share_idx = self.cur_share_idx + 1 if self.cur_share_idx < len(SHARE_URL_LIST) - 1 else 0
    self.cur_share = SHARE_URL_LIST[self.cur_share_idx]
    time.sleep(TICK)


def Share_exception(self):
    self.c += 1
    if self.c > 3:
        print("Fail request too many times")
        time.sleep(5 * TICK)
    else:
        print("Fail request")
        pass


def test_meta():
    newFetcher = create_new_fetcher("ShareFetcher", Share_prepare, Share_work, Share_exception)
    n = newFetcher()
    print(n.name, n.uuid)
    n.run()
    exit(1)


def scan():
    newFetcher = create_new_fetcher("ShareFetcher", Share_prepare, Share_work, Share_exception)
    n = newFetcher()
    print(n.name, n.uuid, "Start to fetch")
    res = n.run()
    print(n.name, n.uuid, "Finish fetching:", res)
    return res


if __name__ == "__main__":
    # test_meta()
    print(scan())
