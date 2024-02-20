import uiautomator2 as u2
from time import sleep

dv = u2.connect_usb('10KDBX0U7200000')
boss = 'com.hpbr.bosszhipin'
zhi_lian = 'com.zhaopin.social'

dv.app_start(boss)
# 从boss最新的第一个开始
sleep(2)
# 点击最新
dv.xpath(
    '//*[@resource-id="com.hpbr.bosszhipin:id/ly_left"]/android.widget.FrameLayout[3]').click()
# 点击第一个
dv.xpath(
    '//*[@resource-id="com.hpbr.bosszhipin:id/refresh_layout"]/androidx.recyclerview.widget.RecyclerView[1]/android.widget.LinearLayout[2]/android.view.ViewGroup[1]/android.widget.FrameLayout[1]').click()
tou_num = 0
for i in range(10):
    # 获取职位信息，去除无用招聘
    zhi_wei = dv.xpath('//*[@resource-id="com.hpbr.bosszhipin:id/tv_job_name"]').get_text()

    if ('测试' in zhi_wei) or ('车载' in zhi_wei) or ('python' in zhi_wei):
        sleep(1)
        dv(text='立即沟通').click()
        # 点击常用语
        dv.xpath(
            '//*[@resource-id="com.hpbr.bosszhipin:id/chat_functions"]/android.widget.LinearLayout[1]/android.widget.LinearLayout[1]'
        ).click()
        # 点击常用语第一个
        dv.xpath('//*[@resource-id="com.hpbr.bosszhipin:id/mContentText"]').click()
        # 点击发送
        dv.xpath(
            '//*[@resource-id="com.hpbr.bosszhipin:id/chat_functions"]/android.widget.LinearLayout[1]/android.widget.ImageView[1]').click()
        print(f'已经投递{zhi_wei}')
        # 点击返回
        dv.xpath('//*[@resource-id="com.hpbr.bosszhipin:id/iv_back"]').click()
        tou_num += 1
    # 左滑切到下一个
    sleep(1)
    dv.swipe(601, 743, 46, 954)
    sleep(1)
print(f'共投递{tou_num}份')