/**
 * @Author: BNDou
 * @Date: 2024-09-02 23:46:21
 * @LastEditTime: 2024-12-29 16:26:10
 * @FilePath: \ToolsBox\DingClockIn\DingClockIn.js
 * @Description: 钉钉自动打卡脚本
 */

"ui";

// 配置常量
const CONFIG = {
    UA: "Mozilla/5.0 (Linux; Android 14; 24031PN0DC Build/UKQ1.231003.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/126.0.6478.188 Mobile Safari/537.36 XWEB/1260117 MMWEBSDK/20240501 MMWEBID/4963 MicroMessenger/8.0.50.2701(0x2800325A) WeChat/arm64 Weixin NetType/4G Language/zh_CN ABI/arm64",
    // 钉钉包名
    PACKAGE_NAME: "com.alibaba.android.rimet",
    APP_NAME: "钉钉",
    // PackageId白名单
    PACKAGE_ID_WHITE_LIST: ["net.dinglisch.android.taskerm", "com.alibaba.android.rimet"],
    // 随机等待时间避免检测
    WAIT_TIME: {
        MIN: 1, // 最小等待时间（秒）
        MAX: 10 // 最大等待时间（秒）
    }
};

// 版本信息
const VERSION = "2024.1229.1626";

// 运行日志路径
const LOG_PATH = "/sdcard/脚本/DingClockInLog/";
const Holiday_Path = "/sdcard/脚本/DingClockInLog/holiday.txt";
const Config_Path = "/sdcard/脚本/DingClockInLog/config.txt";
var file;
if (!files.exists(Config_Path)) {
    file = open(Config_Path, "w");
    file.write(`{"screen_lock_key": "","pushplus_token": "","send_type": 0}`);
    file.close();
}
file = open(Config_Path, "r");
//读取token内容
const data =  JSON.parse(file.read());
var screen_lock_key = data["screen_lock_key"];
var pushplus_token = data["pushplus_token"];
var send_type = data["send_type"];
file.close();
ui.layout(
    <vertical padding="16">
        <text textSize="40sp" gravity="center">钉钉自动打卡脚本</text>
        <text textStyle="italic" textColor="red" gravity="right">版本号：{VERSION}</text>
        <text textStyle="italic" textColor="red" gravity="right">By BNDou</text>
        <text margin="8">Android是一种基于Linux的自由及开放源代码的操作系统，主要使用于移动设备，如智能手机和平板电脑，由Google公司和开放手机联盟领导及开发。尚未有统一中文名称，中国大陆地区较多人使用“安卓”或“安致”。Android操作系统最初由Andy Rubin开发，主要支持手机。2005年8月由Google收购注资。2007年11月，Google与84家硬件制造商、软件开发商及电信营运商组建开放手机联盟共同研发改良Android系统。</text>
        <text autoLink="all" gravity="center">主页：https://github.com/BNDou</text>
        <text text="锁屏密码(没有锁屏，可为空)" textColor="black" textSize="16sp" marginTop="16"/>
        <input id="screen_lock_key" hint="请输入锁屏密码">{screen_lock_key}</input>
        <text text="PUSHPLUS推送token" textColor="black" textSize="16sp" marginTop="16"/>
        <input id="pushplus_token" hint="请输入PUSHPLUS_TOKEN">{pushplus_token}</input>
        <horizontal>
            <text textSize="16sp">选择推送方式(默认公众号)</text>
            <spinner id="send_type" entries="公众号|邮箱"/>
        </horizontal>
        <button id="ok" text="确定" w="auto" style="Widget.AppCompat.Button.Colored"/>
    </vertical>
);
ui.send_type.setSelection(send_type);
ui.ok.click(() => {
    screen_lock_key = ui.screen_lock_key.text();
    pushplus_token = ui.pushplus_token.text();
    send_type = ui.send_type.getSelectedItemPosition();
    if (pushplus_token.length == 0) {
        ui.pushplus_token.setError("输入不能为空");
        return;
    }
    if (pushplus_token.length < 20) {
        ui.pushplus_token.setError("token格式错误");
        return;
    }
    file = open(Config_Path, "w");
    file.write(`{"screen_lock_key": "${screen_lock_key}","pushplus_token": "${pushplus_token}", "send_type": ${send_type}}`);
    file.close();
});

// 工具函数
const Utils = {
    // 日期时间相关
    formatDateDigit: function(num) {
        return num < 10 ? "0" + num : num;
    },

    getCurrentTime: function() {
        var now = new Date();
        return this.formatDateDigit(now.getHours()) + ":" +
            this.formatDateDigit(now.getMinutes()) + ":" +
            this.formatDateDigit(now.getSeconds());
    },

    getCurrentDate: function() {
        var now = new Date();
        return now.getFullYear() + "-" +
            this.formatDateDigit(now.getMonth() + 1) + "-" +
            this.formatDateDigit(now.getDate());
    },

    // 随机等待时间
    randomWait: function(min, max) {
        var waitTime = Math.floor(Math.random() * (max - min + 1)) + min;
        console.log("⏰ 等待时间：" + waitTime + "秒");
        return waitTime;
    },

    // 设置媒体和通知音量
    setVolume: function(volume) {
        device.setMusicVolume(volume);
        device.setNotificationVolume(volume);
        device.setAlarmVolume(volume);
        console.verbose("媒体音量:" + device.getMusicVolume());
        console.verbose("通知音量:" + device.getNotificationVolume());
    },

    // 判断电量
    isBatteryLow: function() {
        var battery = device.getBattery();
        if (battery <= 15) {
            return "⚠️ 电量低";
        } else if (battery <= 30) {
            return "💡 电量适中";
        }
        return "✅ 电量充足";
    }
};

// 初始化配置
function initializeApp() {
    console.warn("版本号：" + VERSION);
    // 检查无障碍权限
    auto.waitFor("normal");

    // 创建运行日志
    console.setGlobalLogConfig({
        file: LOG_PATH + Utils.getCurrentDate() + "-DingLog.txt"
    });

    // 显示控制台
    console.setTitle('钉钉打卡');
    console.setPosition(0, 0);
    console.setSize(0.5, 700);
    console.show(true);
    console.setLogSize(10);
}

// 获取当前年份节假日
function getHolidayData() {
    var res = http.get("https://timor.tech/api/holiday/year/" + new Date().getFullYear(), {
        headers: {
            'User-Agent': CONFIG.UA
        }
    });
    if (res.statusCode != 200) {
        console.error("❌ 当前年份节假日获取失败");
        return true;
    } else {
        var json = res.body.json();
        if (json['code'] != 0) {
            console.error("❌ 当前年份节假日获取失败");
            return true;
        }
        if (json['holiday'] != null) {
            var file = open(Holiday_Path, "w");
            file.write(JSON.stringify(json['holiday']));
            file.close();
            console.info("✅ 节假日数据更新成功");
        }
    }
}

// 工作日判断
function isWorkingDay() {
    try {
        var currentYear = new Date().getFullYear();
        var file;
        if (!files.exists(Holiday_Path)) {
            file = open(Holiday_Path, "w");
            file.close();
        }
        //打开文件
        file = open(Holiday_Path, "r");
        //读取文件的所有内容
        var holidays = file.read();
        //关闭文件
        file.close();
        if (holidays.length == 0) {
            console.info("❌ 节假日数据不存在，前往获取");
            getHolidayData();
            file = open(Holiday_Path, "r");
            holidays = file.read();
            file.close();
        } else {
            for (var key in JSON.parse(holidays)) {
                const year = JSON.parse(holidays)[key].date.split('-')[0];
                if (year != currentYear) {
                    getHolidayData();
                } else {
                    console.info("✅ 节假日数据已存在，无需更新");
                }
                break;
            }
        }

        const today = new Date();
        const dateStr = `${today.getMonth() + 1}-${today.getDate()}`;
        //dateStr='10-12';
        //console.log(holidays[dateStr]);

        if (JSON.parse(holidays)[dateStr]) {
            return !JSON.parse(holidays)[dateStr].holiday;
        }

        const dayOfWeek = today.getDay();
        //dayOfWeek=0;
        //console.log(dayOfWeek);
        if (dayOfWeek === 0 || dayOfWeek === 6) {
            return false;
        }

        return true;
    } catch (error) {
        console.error("❌ 节假日API请求失败：" + error);
        return true; // 默认按工作日处理
    }
}

// 推送消息
function sendPushPlus(sendTitle, sendMsg) {
    try {
        var url = "http://www.pushplus.plus/send";
        var data = {
            token: pushplus_token,
            title: sendTitle,
            content: sendMsg,
            template: "markdown"
        };

        if (send_type) {
            data.channel = "mail";
            data.webhook = "qq";
        }

        var res = http.post(url, data);
        var result = res.body.json();

        if (result.code === 200) {
            console.info("✅ 推送成功");
            return true;
        }

        console.error("❌ 推送失败：" + result.msg);
        return false;
    } catch (error) {
        console.error("❌ 推送请求失败：" + error);
        return false;
    }
}

// 唤醒设备
function brightScreen() {
    console.verbose("唤醒设备");
    device.wakeUp();
    sleep(2000);
    swipe(500, 1500, 500, 10, 1000);
    sleep(1000);
    if (screen_lock_key.length > 0) {
        for (var i = 0; i < screen_lock_key.length; i++) {
        desc(screen_lock_key[i].toString()).findOne(3000).click();
        sleep(234);
        }
    }
    device.keepScreenDim();
    device.setBrightnessMode(1);
    // device.setBrightness(1);
    sleep(500);

    if (!device.isScreenOn()) {
        console.warn("❌ 设备未唤醒, 重试");
        device.wakeUp();
        brightScreen();
    } else {
        console.info("✅ 设备已唤醒");
    }
}

// 使用 URL Scheme 进入考勤界面
function attendKaoqin() {
    console.verbose("打开应用中 ...");
    launch(CONFIG.PACKAGE_NAME);
    toast("🔔 如果有确定打开的弹窗\n🔔 请点击确定");
    var button = className('Button').textMatches(/(.*确定.*|.*允许.*)/).findOne(1000);
    if (button) {
        button.click();
    }
    console.info("✅ " + CONFIG.APP_NAME + "-应用已打开");

    console.verbose("正在进入考勤界面 ...");
    var url_scheme = "dingtalk://dingtalkclient/page/calendarHome?channel=calendarwidget";
    var a = app.intent({
        packageName: CONFIG.PACKAGE_NAME,
        flags: ["activity_new_task"],
        action: "VIEW",
        data: url_scheme
    });
    app.startActivity(a);

    id("calendar_week_month_switcher").waitFor()
    console.info("✅ 已进入考勤界面");
    swipe(500, 1200, 500, 800, 1000);
    swipe(500, 1200, 500, 1600, 1000);
}

// 锁屏
function screen() {
    console.verbose("关闭屏幕");
    device.cancelKeepingAwake();
    lockScreen();

    sleep(1000);
    if (!device.isScreenOn()) {
        console.info("✅ 屏幕已关闭");
    } else {
        console.error("❌ 屏幕未关闭, 请尝试其他锁屏方案, 或等待屏幕自动关闭");
    }
}

// 停止APP
function killApp() {
    app.openAppSetting(CONFIG.PACKAGE_NAME);
    text(CONFIG.APP_NAME).waitFor();
    sleep(1000);

    var is_sure = textMatches(/(.*强.*|.*停.*|.*结.*)/).findOne();
    if (is_sure.enabled()) {
        switch (device.brand.toLowerCase()) {
            case 'xiaomi':
                is_sure.parent().click();
                sleep(1000);
                textMatches(/(.*确.*|.*定.*|.*允.*|.*许.*)/).findOne().click();
                break;
            case 'huawei':
            case 'honor':
                is_sure.click();
                sleep(1000);
                textMatches(/(.*强行停止.*|.*确.*|.*定.*|.*允.*|.*许.*)/).findOnce(1).click();
                break;
            default:
                console.error("❌ 找不到停止运行的按钮，可能未适配-" + device.brand.toLowerCase());
                launch("org.autojs.autoxjs.v6");
        }
        console.info("✅ 应用已被关闭");
    } else {
        console.error("❌ 应用不能被正常关闭或不在后台运行");
    }
    launch("org.autojs.autoxjs.v6");
}

// 打卡流程
function clockIn() {
    console.verbose("本地时间: " + Utils.getCurrentDate() + " " + Utils.getCurrentTime());
    console.verbose("开始打卡流程!");

    try {
        Utils.setVolume(0);
        attendKaoqin();
    } catch (e) {
        console.error("❌ 启动钉钉失败" + e);
    }
}

// 处理通知
function handleNotification(n) {
    var packageName = n.getPackageName();
    var title = n.getTitle();
    var text = n.getText();

    if (!CONFIG.PACKAGE_ID_WHITE_LIST.includes(packageName)) {
        return;
    }

    console.verbose("👇👇👇👇👇👇");
    console.verbose("🔔 " + packageName);
    console.verbose("🔔 " + title);
    console.verbose("🔔 " + text);
    console.verbose("👆👆👆👆👆👆");

    if (text.indexOf("打卡·成功") !== -1) {
        var battery = Utils.isBatteryLow() + " 剩余电量：" + device.getBattery() + "%";
        var msg = "🔔 " + title.slice(title.indexOf(':') + 1) +
            " " + Utils.getCurrentDate() + " " + Utils.getCurrentTime();

        console.info(battery);
        console.info(msg);
        msg = "## " + battery + "\n## " + msg;

        sendPushPlus("🎉 " + CONFIG.APP_NAME + " [打卡·成功]", msg);
        killApp();
        screen();
        ui.finish();
        // exit();
    }
}

// 主函数
function main() {
    try {
        // 初始化
        initializeApp();
        console.verbose("======分割线===================================================");

        // 唤醒设备
        brightScreen();

        // 随机等待避免检测
        var waitTime = Utils.randomWait(CONFIG.WAIT_TIME.MIN, CONFIG.WAIT_TIME.MAX);
        sleep(waitTime * 1000);

        // 检查是否为工作日
        console.verbose("工作日判定中 ...");
        if (!isWorkingDay()) {
            var battery = Utils.isBatteryLow() + " 剩余电量：" + device.getBattery() + "%";
            var msg = "🌴 今日休息日，不执行打卡";
            console.info(battery);
            console.info(msg);
            msg = "## " + battery + "\n## " + msg;
            sendPushPlus("🚧 钉钉打卡 今日休息", msg);
            screen();
            ui.finish();
            // exit();
        }

        // 监听通知
        console.verbose("监听打卡通知中 ...");
        events.observeNotification();
        events.onNotification(handleNotification);

        // 执行打卡
        clockIn();
    } catch (error) {
        console.error("❌ 程序执行出错：" + error);
        sendPushPlus("❌ 钉钉打卡异常", "执行出错：" + error);
        ui.finish();
        // exit(error);
    }
}

// 启动脚本
threads.start(function() {
    if (pushplus_token.length != 0) {
        main();
    }
});