/**
 * @Author: BNDou
 * @Date: 2024-09-02 23:46:21
 * @LastEditTime: 2024-09-03 04:12:31
 * @FilePath: \ToolsBox\DingClockIn\DingClockIn.js
 * @Description: 
 * 借鉴自：https://github.com/georgehuan1994/DingDing-Automatic-Clock-in
 */
// pushplus推送token
const PUSHPLUS_TOKEN = "";
// pushplus邮箱推送，需在公众号配置邮箱: true-邮箱推送 false-公众号推送(建议)
const PUSHPLUS_MAIL = true;


// 公司的钉钉CorpId, 获取方法：https://www.dingtalk.com?corpId=$CORPID$
const CORP_ID = "";
// 钉钉包名
const PACKAGE_NAME = "com.alibaba.android.rimet"
const APP_NAME = "钉钉";
// PackageId白名单
const PACKAGE_ID_WHITE_LIST = [PACKAGE_NAME];
// 监听音量+键, 开启后无法通过音量+键调整音量, 按下音量+键：结束所有子线程
const OBSERVE_VOLUME_KEY = true;
const WEEK_DAY = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday",];



// ========== ↓↓↓ 主线程：监听通知 ↓↓↓ ==========

var currentDate = new Date();

// 运行日志路径
var globalLogFilePath = "/sdcard/脚本/DingClockInLog/" + getCurrentDate() + "-log.txt";

// 检查无障碍权限
auto.waitFor("normal");

// 创建运行日志
console.setGlobalLogConfig({
    file: "/sdcard/脚本/DingClockInLog/" + getCurrentDate() + "-log.txt"
});

// 唤醒设备
brightScreen();

// 显示控制台
// console.clear();
console.setTitle('钉钉打卡');
console.setPosition(0, 0);
console.setSize(0.5, 700);
console.show(true);
console.setLogSize(10);

// 监听通知
try {
    log("监听打卡通知中...");
    events.observeNotification();
    events.onNotification(function (n) {
        printNotification(n);
    });
} catch (e) {
    console.error("❌ 监听通知失败");
    exit(e);
}

events.setKeyInterceptionEnabled("volume_up", OBSERVE_VOLUME_KEY);

if (OBSERVE_VOLUME_KEY) {
    events.observeKey();
}

// 监听音量+键
events.onKeyDown("volume_up", function (event) {
    threads.shutDownAll();
    device.setBrightnessMode(1);
    device.cancelKeepingAwake();
    toast("已中断所有子线程!");

    // 可以在此调试各个方法
    // clockIn();
    // sendEmail("测试文本");
});

// 打卡
clockIn();

toastLog("监听中, 请在日志中查看记录的通知及其内容");

// ========== ↑↑↑ 主线程：监听通知 ↑↑↑ ==========



// 处理通知
function printNotification(n) {
    var packageName = n.getPackageName(); // 获取通知包名
    var abstract = n.tickerText; // 获取通知摘要
    var text = n.getText(); // 获取通知文本

    // 过滤 PackageId 白名单之外的应用所发出的通知
    if (!filterNotification(packageName, abstract, text)) {
        return;
    }

    log("\n🔔 应用包名: " + packageName + "\n🔔 通知文本: " + text);

    if (n.getText().indexOf("打卡·成功")) {

        // 推送内容
        var msg = "🎉 【打卡·成功】" + getCurrentDate() + " " + getCurrentTime();
        console.info(msg);

        // 推送
        sendPushPlus(msg);

        // 关闭应用
        killApp();

        // 关闭屏幕
        lockScreen();

        // 结束脚本运行
        exit();
    }
}

// 打卡流程
function clockIn() {
    currentDate = new Date();
    console.log("本地时间: " + getCurrentDate() + " " + getCurrentTime());
    console.log("开始打卡流程!");

    // 打开钉钉
    try {
        log("... 正在启动 " + APP_NAME);
        setVolume(0); // 设备静音
        attendKaoqin(); // 进入考勤页
        toast("🔔 如果有确定打开的弹窗\n🔔 请点击确定");
        // sleep(1000);
        // var button = className('Button').textMatches(/(.*确.*|.*定.*|.*允.*|.*许.*)/).findOne();
        // log(button);
        // if (button) {
        //     button.click();
        // }
    } catch (e) {
        console.error("启动钉钉失败" + e);
    }
}

// 推送
function sendPushPlus(msg) {
    const url = "http://www.pushplus.plus/send";
    const data = {
        "token": PUSHPLUS_TOKEN,
        "title": "钉钉自动打卡",
        "content": "# " + msg,
        "template": "markdown"
    };
    if (PUSHPLUS_MAIL) {
        data["channel"] = "mail";
        data["webhook"] = "qq";
    }
    var res = http.post(url, data);
    if (res.body.json()["code"] == 200) {
        console.log("✅ 推送成功");
    }
}

// 唤醒设备
function brightScreen() {
    console.log("唤醒设备");
    device.wakeUpIfNeeded(); // 唤醒设备
    device.keepScreenOn(); // 保持亮屏
    device.setBrightnessMode(0); // 手动亮度模式
    device.setBrightness(0); // 设置亮度为0
    sleep(500); // 等待屏幕亮起

    if (!device.isScreenOn()) {
        console.warn("❌ 设备未唤醒, 重试");
        device.wakeUpIfNeeded();
        brightScreen();
    }
    else {
        console.info("✅ 设备已唤醒");
    }
}

// 使用 URL Scheme 进入考勤界面
function attendKaoqin() {
    var url_scheme = "dingtalk://dingtalkclient/page/link?url=https://attend.dingtalk.com/attend/index.html";
    if (CORP_ID != "") {
        url_scheme = url_scheme + "?corpId=" + CORP_ID;
    } else {
        console.error("❌ 未设置 CORP_ID，无法跳转到考勤界面，尝试打开应用");
        launch(PACKAGE_NAME);
        return;
    }

    var a = app.intent({
        action: "VIEW",
        data: url_scheme
    });
    app.startActivity(a);
    console.log("正在进入考勤界面...");

    text("打卡").waitFor();
    text("统计").waitFor();
    text("设置").waitFor();
    console.info("✅ 已进入考勤界面");
}

// 锁屏
function lockScreen() {
    console.log("关闭屏幕");

    // 锁屏方案1：Root
    // Power()

    // 锁屏方案2：No Root
    // press(Math.floor(device.width / 2), Math.floor(device.height * 0.973), 1000) // 小米的快捷手势：长按Home键锁屏

    //    device.setBrightnessMode(1) // 自动亮度模式
    device.cancelKeepingAwake(); // 取消设备常亮

    if (isDeviceLocked()) {
        console.info("✅ 屏幕已关闭");
    }
    else {
        console.error("❌ 屏幕未关闭, 请尝试其他锁屏方案, 或等待屏幕自动关闭");
    }
}

// 停止APP
function killApp() {
    app.openAppSetting(PACKAGE_NAME);
    //通过包名获取已安装的应用名称，判断是否已经跳转至该app的应用设置界面
    text(APP_NAME).waitFor();
    sleep(1000);
    //稍微休息一下，不然看不到运行过程，自己用时可以删除这行
    let is_sure = textMatches(/(.*强.*|.*停.*|.*结.*)/).findOne();
    // log(is_sure.text());
    //在app的应用设置界面找寻包含“强”，“停”，“结”的控件
    if (is_sure.enabled()) { //判断控件是否已启用（想要关闭的app是否运行）
        is_sure.parent().click(); //结束应用的控件如果无法点击，需要在布局中找寻它的父控件，如果还无法点击，再上一级控件，本案例就是控件无法点击
        textMatches(/(.*确.*|.*定.*|.*允.*|.*许.*)/).findOne().click();
        log(APP_NAME + "-应用已被关闭");
        sleep(1000);
        back();
    } else {
        log(APP_NAME + "-应用不能被正常关闭或不在后台运行");
        back();
    }
}



// ===================== ↓↓↓ 功能函数 ↓↓↓ =======================

function dateDigitToString(num) {
    return num < 10 ? '0' + num : num;
}

function getCurrentTime() {
    var currentDate = new Date();
    var hours = dateDigitToString(currentDate.getHours());
    var minute = dateDigitToString(currentDate.getMinutes());
    var second = dateDigitToString(currentDate.getSeconds());
    var formattedTimeString = hours + ':' + minute + ':' + second;
    return formattedTimeString;
}

function getCurrentDate() {
    var currentDate = new Date();
    var year = dateDigitToString(currentDate.getFullYear());
    var month = dateDigitToString(currentDate.getMonth() + 1);
    var date = dateDigitToString(currentDate.getDate());
    var week = currentDate.getDay();
    var formattedDateString = year + '-' + month + '-' + date + '-' + WEEK_DAY[week];
    return formattedDateString;
}

// 通知过滤器
function filterNotification(bundleId, abstract, text) {
    var check = PACKAGE_ID_WHITE_LIST.some(function (item) { return bundleId == item });
    if (check) {
        console.verbose(bundleId);
        console.verbose(abstract);
        console.verbose(text);
        console.verbose("----------");
        return true;
    }
    else {
        return false;
    }
}

// 屏幕是否为锁定状态
function isDeviceLocked() {
    importClass(android.app.KeyguardManager);
    importClass(android.content.Context);
    var km = context.getSystemService(Context.KEYGUARD_SERVICE);
    return km.isKeyguardLocked();
}

// 设置媒体和通知音量
function setVolume(volume) {
    device.setMusicVolume(volume);
    device.setNotificationVolume(volume);
    console.verbose("媒体音量:" + device.getMusicVolume());
    console.verbose("通知音量:" + device.getNotificationVolume());
}
