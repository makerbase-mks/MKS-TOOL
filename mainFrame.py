#-*-coding:utf-8-*-
__copyright__ = "Copyright (C) 2013 l - Released under terms of the AGPLv3 License"

import wx
from PIL import Image, ImageDraw
import os
from struct import *
import threading
import sys
import shutil
import __builtin__
__builtin__.__dict__['_'] = wx.GetTranslation
# import gettext
# _ = gettext.gettext

class FileDropTarget(wx.FileDropTarget):
    def __init__(self, parent, callback=None, pos=0):
        wx.FileDropTarget.__init__(self)
        self.parent = parent
        self._callback = callback
        self._pos = pos

    def OnDropFiles(self, x, y, fileNames):
        txt = '%s' % fileNames[0]
        self._callback(txt, self._pos)
class mainwindow(wx.Frame):
    def __init__(self):
        super(mainwindow, self).__init__(None, title=u"MKSTOOL")
        self.icon = wx.Icon('mkstool.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.icon)
        locale = wx.Locale(wx.LANGUAGE_ENGLISH)
        locale.AddCatalogLookupPathPrefix('locale')
        self.languagename = self.getLanguage()
        ibRet = locale.AddCatalog(self.languagename)
        self._viewlist = [_(u'开机logo'),_(u'准备打印'),_(u'预热'),_(u'挤出'),_(u'移动'),_(u'回零'),_(u'调平'),_(u'设置'),_(u'风扇'),
                          _(u'换料'),_(u'文件系统'),_(u'更多'),_(u'选择文件'),_(u'正在打印'),_(u'操作'),_(u'暂停'),_(u'变速'),_(u'更多（打印中）'),_(u'语言'),_(u'WIFI')]
        self.selectedviewpos = 0
        self._typelist = ["MKS Robin-TFT24/28/32", "MKS Robin Nano-TFT24/28/32", "MKS Robin Nano-TFT35", "MKS Robin Nano-TFT35-DIY-IAR", "MKS Robin Mini-TFT24/28/32", "MKS Robin2-TFT35"]
        self._pixellist = [[320, 240,78, 104], [480, 320, 117, 140]]
        self.languagelist = [u'中文',u'English']
        self.imagelist = [[None,None,None],[None,None,None],[None,None,None],[None,None,None],[None,None,None],[None,None,None],[None,None,None],[None,None,None]]
        self.choosefileimagelist = [[None, None, None], [None, None, None], [None, None, None], [None, None, None], [None, None, None],[None, None, None], [None, None, None], [None, None, None], [None, None, None]]
        self.printingimagelist = [[None, None, None], [None, None, None], [None, None, None], [None, None, None]]
        self.allimglist32 = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
        self.allimglist35 = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
        self.allimglistdiy = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
        # 标题 选项 类型 导出名 提示 默认值 校验器
        # [_(u'主板类型'), [_(u'0:MKS NANO+TFT32'), _(u'1:MKS NANO+TFT35'), _(u'2:MKS Robin2')], 'choose', 'mode', _(u'主板类型'), '0', ''],
        self.configdt = [[_(u'屏幕首页显示模式'), [_(u'0:经典模式'),_(u'1:简约模式')], 'choose', '>cfg_screen_display_mode', _(u'屏幕首页显示模式'), 0, ''],
                         [_(u'语言切换方式'), [_(u'0:配置文件选项切换语言'),_(u'1:屏幕按钮切换语言')], 'choose', '>cfg_language_adjust_type', _(u'语言切换方式'), 1, ''],
                         [_(u'语言'), [_(u'1:简体中文'), _(u'2:繁体中文'), _(u'3:英文'), _(u'4:俄语'), _(u'5:西班牙语'), _(u'6:法语'), _(u'7:意大利语')], 'choose', '>cfg_language_type', _(u'语言'), 2, ''],
                         [_(u'机型设置'), [_(u'0:Cartesian'), _(u'1:DELTA'), _(u'2:COREXY')], 'choose', '>MACHINETPYE',_(u'机型设置'), 0, ''],
                         [_(u'热床'), [_(u'0:禁止'), _(u'1:开启')], 'choose', '>HAS_TEMP_BED', _(u'热床'), 1, ''],
                         [_(u'挤出头数量'), [1], 'edit', '>HAS_TEMP_BED', _(u'挤出头数量'), 1, ''],
                         [_(u'使能双Z功能'), [_(u'0:禁止'), _(u'1:开启')], 'choose', '>EXTRUDERS', '', 0, ''],
                         [_(u'使能Z轴双限位'), [_(u'0:禁止'), _(u'1:开启')], 'choose', '>Z2_ENDSTOPS', '', 0, ''],
                         [_(u'Z轴第二个限位接口'), [_(u'0:不使用'), _(u'1:Z_MAX'), _(u'2:Z_MIN')], 'choose', '>Z2_USE_ENDSTOP', '', 0, ''],
                         [_(u'X轴最小行程'), [1], 'edit', '>X_MIN_POS', _(u'X轴最小行程,范围为-999~99999'), 0, 'type1'],
                         [_(u'Y轴最小行程'), [1], 'edit', '>Y_MIN_POS', _(u'Y轴最小行程,范围为-999~99999'), 0, 'type1'],
                         [_(u'Z轴最小行程'), [1], 'edit', '>Z_MIN_POS', '', 0, 'type1'],
                         [_(u'X轴最大行程'), [1], 'edit', '>X_MAX_POS', '', 210, 'type1'],
                         [_(u'Y轴最大行程'), [1], 'edit', '>Y_MAX_POS', '', 210, 'type1'],
                         [_(u'Z轴最大行程'), [1], 'edit', '>Z_MAX_POS', '', 210, 'type1'],
                         [_(u'暂停时X轴的位置'), [1], 'edit', '>FILAMENT_CHANGE_X_POS', '', 5, 'type1'],
                         [_(u'暂停时Y轴的位置'), [1], 'edit', '>FILAMENT_CHANGE_Y_POS', '', 5, 'type1'],
                         [_(u'暂停时Z轴的位置'), [1], 'edit', '>FILAMENT_CHANGE_Z_ADD', '', 5, 'type1'],
                         [_(u'双头时X轴的偏移值'), [1], 'edit', '>HOTEND_OFFSET_X', '', 20, 'type1'],
                         [_(u'双头时Y轴的偏移值'), [1], 'edit', '>HOTEND_OFFSET_Y', '', 5, 'type1'],
                         [_(u'X轴的电机方向'), [_(u'0:反转'), _(u'1:正转')], 'choose', '>INVERT_X_DIR', '', 1, ''],
                         [_(u'Y轴的电机方向'), [_(u'0:反转'), _(u'1:正转')], 'choose', '>INVERT_Y_DIR', '', 1, ''],
                         [_(u'Z轴的电机方向'), [_(u'0:反转'), _(u'1:正转')], 'choose', '>INVERT_Z_DIR', '', 1, ''],
                         [_(u'E0轴的电机方向'), [_(u'0:反转'), _(u'1:正转')], 'choose', '>INVERT_E0_DIR', '', 1, ''],
                         [_(u'E1轴的电机方向'), [_(u'0:反转'), _(u'1:正转')], 'choose', '>INVERT_E1_DIR', '', 1, ''],
                         [_(u'X轴脉冲值（Steps/mm）'), [1], 'edit', '>DEFAULT_X_STEPS_PER_UNIT', '', 80, 'type2'],
                         [_(u'Y轴脉冲值（Steps/mm）'), [1], 'edit', '>DEFAULT_Y_STEPS_PER_UNIT', '', 80, 'type2'],
                         [_(u'Z轴脉冲值（Steps/mm）'), [1], 'edit', '>DEFAULT_Z_STEPS_PER_UNIT', '', 4000, 'type2'],
                         [_(u'E0轴脉冲值（Steps/mm）'), [1], 'edit', '>DEFAULT_E0_STEPS_PER_UNIT', '', 90, 'type2'],
                         [_(u'E1轴脉冲值（Steps/mm）'), [1], 'edit', '>DEFAULT_E1_STEPS_PER_UNIT', '', 90, 'type2'],
                         [_(u'X轴默认速度 (mm/s)'), [1], 'edit', '>DEFAULT_X_MAX_FEEDRATE', '', 200, 'type2'],
                         [_(u'Y轴默认速度 (mm/s)'), [1], 'edit', '>DEFAULT_Y_MAX_FEEDRATE', '', 200, 'type2'],
                         [_(u'Z轴默认速度 (mm/s)'), [1], 'edit', '>DEFAULT_Z_MAX_FEEDRATE', '', 40, 'type2'],
                         [_(u'E0轴默认速度 (mm/s)'), [1], 'edit', '>DEFAULT_E0_MAX_FEEDRATE', '', 70, 'type2'],
                         [_(u'E1轴默认速度 (mm/s)'), [1], 'edit', '>DEFAULT_E1_MAX_FEEDRATE', '', 70, 'type2'],
                         [_(u'X轴默认最大加速度 (mm/s)'), [1], 'edit', '>DEFAULT_X_MAX_ACCELERATION', '', 1000, 'type2'],
                         [_(u'Y轴默认最大加速度 (mm/s)'), [1], 'edit', '>DEFAULT_Y_MAX_ACCELERATION', '', 1000, 'type2'],
                         [_(u'Z轴默认最大加速度 (mm/s)'), [1], 'edit', '>DEFAULT_Z_MAX_ACCELERATION', '', 100, 'type2'],
                         [_(u'E0轴默认最大加速度 (mm/s)'), [1], 'edit', '>DEFAULT_E0_MAX_ACCELERATION', '', 1000, 'type2'],
                         [_(u'E1轴默认最大加速度 (mm/s)'), [1], 'edit', '>DEFAULT_E1_MAX_ACCELERATION', '', 1000, 'type2'],
                         [_(u'X,Y,Z,E 打印时的默认加速度'), [1], 'edit', '>DEFAULT_ACCELERATION', '', 1000, 'type2'],
                         [_(u'X,Y,Z,E 回抽默认加速度'), [1], 'edit', '>DEFAULT_RETRACT_ACCELERATION', '', 1000, 'type2'],
                         [_(u'X,Y,Z 非打印时的默认加速度'), [1], 'edit', '>DEFAULT_TRAVEL_ACCELERATION', '', 1000, 'type2'],
                         [_(u'默认最小速度'), [1], 'edit', '>DEFAULT_MINIMUMFEEDRATE', '', 0, 'type2'],
                         [_(u'>DEFAULT_MINSEGMENTTIME'), [1], 'edit', '>DEFAULT_MINSEGMENTTIME', '', 20000, 'type2'],
                         [_(u'>DEFAULT_MINTRAVELFEEDRATE'), [1], 'edit', '>DEFAULT_MINTRAVELFEEDRATE', '', 0, 'type2'],
                         [_(u'X轴 Jerk (mm/s)'), [1], 'edit', '>DEFAULT_XJERK', '', 20, 'type2'],
                         [_(u'Y轴 Jerk (mm/s)'), [1], 'edit', '>DEFAULT_YJERK', '', 20, 'type2'],
                         [_(u'Z轴 Jerk (mm/s)'), [1], 'edit', '>DEFAULT_ZJERK', '', 0.4, 'type2'],
                         [_(u'E轴 Jerk (mm/s)'), [1], 'edit', '>DEFAULT_EJERK', '', 5, 'type2'],
                         [_(u'X轴高低电平使能'), [_(u'0:低'), _(u'1:高')], 'choose', '>X_ENABLE_ON', '', 0, ''],
                         [_(u'Y轴高低电平使能'), [_(u'0:低'), _(u'1:高')], 'choose', '>Y_ENABLE_ON', '', 0, ''],
                         [_(u'Z轴高低电平使能'), [_(u'0:低'), _(u'1:高')], 'choose', '>Z_ENABLE_ON', '', 0, ''],
                         [_(u'E轴高低电平使能'), [_(u'0:低'), _(u'1:高')], 'choose', '>E_ENABLE_ON', '', 0, ''],
                         [_(u'挤出头热敏类型'), [_(u'1:100k热敏'), _(u'-3:MAX31855热电偶')], 'choose', '>TEMP_SENSOR_0', '', 1, ''],
                         [_(u'挤出机最低挤出温度'), [1], 'edit', '>EXTRUDE_MINTEMP', '', 170, 'type2'],
                         [_(u'挤出头1最低温度'), [1], 'edit', '>HEATER_0_MINTEMP', '', 5, 'type2'],
                         [_(u'挤出头1最大温度'), [1], 'edit', '>HEATER_0_MAXTEMP', '', 275, 'type2'],
                         [_(u'挤出头2最低温度'), [1], 'edit', '>HEATER_1_MINTEMP', '', 5, 'type2'],
                         [_(u'挤出头2最大温度'), [1], 'edit', '>HEATER_1_MAXTEMP', '', 275, 'type2'],
                         [_(u'热床最大温度'), [1], 'edit', '>BED_MAXTEMP', '', 150, 'type2'],
                         [_(u'>THERMAL_PROTECTION_PERIOD'), [1], 'edit', '>THERMAL_PROTECTION_PERIOD', '', 140, 'type2'],
                         [_(u'>THERMAL_PROTECTION_HYSTERESIS'), [1], 'edit', '>THERMAL_PROTECTION_HYSTERESIS', '', 4, 'type2'],
                         [_(u'>WATCH_TEMP_PERIOD'), [1], 'edit', '>WATCH_TEMP_PERIOD', '', 120, 'type2'],
                         [_(u'>WATCH_TEMP_INCREASE'), [1], 'edit', '>WATCH_TEMP_INCREASE', '', 2, 'type2'],
                         [_(u'>THERMAL_PROTECTION_BED_PERIOD'), [1], 'edit', '>THERMAL_PROTECTION_BED_PERIOD', '', 120, 'type2'],
                         [_(u'>THERMAL_PROTECTION_BED_HYSTERESIS'), [1], 'edit', '>THERMAL_PROTECTION_BED_HYSTERESIS', '', 2, 'type2'],
                         [_(u'>WATCH_BED_TEMP_PERIOD'), [1], 'edit', '>WATCH_BED_TEMP_PERIOD', '', 160, 'type2'],
                         [_(u'>WATCH_BED_TEMP_INCREASE'), [1], 'edit', '>WATCH_BED_TEMP_INCREASE', '', 2, 'type2'],
                         [_(u'挤出头温控模式选择'), [_(u'0:bang-bang'), _(u'1:PID')], 'choose', '>PIDTEMPE', '', 1, ''],
                         [_(u'挤出头温控P值设置'), [1], 'edit', '>DEFAULT_Kp', '', 22.2, 'type2'],
                         [_(u'挤出头温控I值设置'), [1], 'edit', '>DEFAULT_Ki', '', 1.08, 'type2'],
                         [_(u'挤出头温控D值设置'), [1], 'edit', '>DEFAULT_Kd', '', 114, 'type2'],
                         [_(u'热床温控P值设置'), [1], 'edit', '>DEFAULT_bedKp', '', 10.02, 'type2'],
                         [_(u'热床温控I值设置'), [1], 'edit', '>DEFAULT_bedKi', '', 0.023, 'type2'],
                         [_(u'热床温控D值设置'), [1], 'edit', '>DEFAULT_bedKd', '', 305.4, 'type2'],
                         [_(u'最小软限位'), [_(u'0:禁止'), _(u'1:开启')], 'choose', '>MIN_SOFTWARE_ENDSTOPS', '', 1, ''],
                         [_(u'最大软限位'), [_(u'0:禁止'), _(u'1:开启')], 'choose', '>MAX_SOFTWARE_ENDSTOPS', '', 1, ''],
                         [_(u'使能X轴最小值限位开关'), [_(u'0:禁止'), _(u'1:开启')], 'choose', '>USE_XMIN_PLUG', '', 1, ''],
                         [_(u'使能Y轴最小值限位开关'), [_(u'0:禁止'), _(u'1:开启')], 'choose', '>USE_YMIN_PLUG', '', 1, ''],
                         [_(u'使能Z轴最小值限位开关'), [_(u'0:禁止'), _(u'1:开启')], 'choose', '>USE_ZMIN_PLUG', '', 1, ''],
                         [_(u'使能X轴最大值限位开关'), [_(u'0:禁止'), _(u'1:开启')], 'choose', '>USE_XMAX_PLUG', '', 0, ''],
                         [_(u'使能Y轴最大值限位开关'), [_(u'0:禁止'), _(u'1:开启')], 'choose', '>USE_YMAX_PLUG', '', 0, ''],
                         [_(u'使能Z轴最大值限位开关'), [_(u'0:禁止'), _(u'1:开启')], 'choose', '>USE_ZMAX_PLUG', '', 0, ''],
                         [_(u'X轴最小限位开关类型'), [_(u'0:常开'), _(u'1:关闭')], 'choose', '>X_MIN_ENDSTOP_INVERTING', '', 0, ''],
                         [_(u'Y轴最小限位开关类型'), [_(u'0:常开'), _(u'1:关闭')], 'choose', '>Y_MIN_ENDSTOP_INVERTING', '', 0, ''],
                         [_(u'Z轴最小限位开关类型'), [_(u'0:常开'), _(u'1:关闭')], 'choose', '>Z_MIN_ENDSTOP_INVERTING', '', 0, ''],
                         [_(u'X轴最大限位开关类型'), [_(u'0:常开'), _(u'1:关闭')], 'choose', '>X_MAX_ENDSTOP_INVERTING', '', 1, ''],
                         [_(u'Y轴最大限位开关类型'), [_(u'0:常开'), _(u'1:关闭')], 'choose', '>Y_MAX_ENDSTOP_INVERTING', '', 1, ''],
                         [_(u'Z轴最大限位开关类型'), [_(u'0:常开'), _(u'1:关闭')], 'choose', '>Z_MAX_ENDSTOP_INVERTING', '', 1, ''],
                         [_(u'X轴回零方向'), [_(u'-1:最小值方向'), _(u'1:最大值方向')], 'choose', '>X_HOME_DIR', '', -1, ''],
                         [_(u'Y轴回零方向'), [_(u'-1:最小值方向'), _(u'1:最大值方向')], 'choose', '>Y_HOME_DIR', '', -1, ''],
                         [_(u'Z轴回零方向'), [_(u'-1:最小值方向'), _(u'1:最大值方向')], 'choose', '>Z_HOME_DIR', '', -1, ''],
                         [_(u'XY轴回零速度 (mm/m)'), [1], 'edit', '>HOMING_FEEDRATE_XY', '', 2400, 'type2'],
                         [_(u'Z轴回零速度 (mm/m)'), [1], 'edit', '>HOMING_FEEDRATE_Z', '', 2400, 'type2'],
                         [_(u'回零时xy轴的顺序'), [_(u'0:X先回零'), _(u'1:Y先回零')], 'choose', '>HOME_Y_BEFORE_X', '', 0, ''],
                         [_(u'打完关机'), [_(u'0:禁止'), _(u'1:开启')], 'choose', '>cfg_print_over_auto_close', '', 1, ''],
                         [_(u'是否接UPS电源'), [_(u'0:禁止'), _(u'1:开启')], 'choose', '>cfg_have_ups_device', '', 0, ''],
                         [_(u'配合UPS电源检测模块'), [_(u'0:mks pwc'), _(u'1:mks 220det')], 'choose', '>cfg_print_over_auto_close', '', 1, ''],
                         [_(u'挤出头1断料检测'), [_(u'0:低电平触发'), _(u'1:高电平触发')], 'choose', '>cfg_filament_det0_trigger_level', '', 0, ''],
                         [_(u'挤出头2断料检测'), [_(u'0:低电平触发'), _(u'1:高电平触发')], 'choose', '>cfg_filament_det1_trigger_level', '', 0, ''],
                         [_(u'换料进料的长度'), [1], 'edit', '>cfg_filament_load_length', '', 100, 'type2'],
                         [_(u'换料进料速度配置(mm/min)'), [1], 'edit', '>cfg_filament_load_speed', '', 800, 'type2'],
                         [_(u'换料进料最低限制温度配置'), [1], 'edit', '>cfg_filament_load_limit_temperature', '', 200, 'type2'],
                         [_(u'换料退料的长度'), [1], 'edit', '>cfg_filament_unload_length', '', 100, 'type2'],
                         [_(u'换料退料速度配置(mm/min)'), [1], 'edit', '>cfg_filament_unload_speed', '', 800, 'type2'],
                         [_(u'换料退料最低限制温度配置'), [1], 'edit', '>cfg_filament_unload_limit_temperature', '', 200, 'type2'],
                         [_(u'调平方式'), [_(u'0:手动调平'), _(u'1:自动调平')], 'choose', '>cfg_leveling_mode', '', 0, ''],
                         [_(u'手动调平的调平点数'), [_(u'3:3'), _(u'4:4'), _(u'5:5')], 'choose', '>cfg_point_number', '', 5, ''],
                         [_(u'调平点1（X,Y）'), [1], 'edit', '>cfg_point1:', '', '20,20', 'type2'],
                         [_(u'调平点2（X,Y）'), [1], 'edit', '>cfg_point2:', '', '200,20', 'type2'],
                         [_(u'调平点3（X,Y）'), [1], 'edit', '>cfg_point3:', '', '200,200', 'type2'],
                         [_(u'调平点4（X,Y）'), [1], 'edit', '>cfg_point4:', '', '20,200', 'type2'],
                         [_(u'调平点5（X,Y）'), [1], 'edit', '>cfg_point5:', '', '100,100', 'type2'],
                         [_(u'自动调平指令'), [1], 'edit', '>cfg_auto_leveling_cmd:', '', 'G28;G29;', 'type3'],
                         [_(u'自动调平方式'), [_(u'0:不使用调平'), _(u'3:多点自动调平'), _(u'5:手动网格调平')], 'choose', '>BED_LEVELING_METHOD', '', 0, ''],
                         [_(u'调平的探针'), [_(u'0:不使用'), _(u'1:接Z_MIN'), _(u'2:接ZMAX')], 'choose', '>Z_MIN_PROBE_PIN_MODE', '', 0, ''],
                         [_(u'探针X轴偏移量'), [1], 'edit', '>Z_PROBE_OFFSET_FROM_EXTRUDER', '', 0, 'type1'],
                         [_(u'探针Y轴偏移量'), [1], 'edit', '>X_PROBE_OFFSET_FROM_EXTRUDER', '', 0, 'type1'],
                         [_(u'探针Z轴偏移量'), [1], 'edit', '>Y_PROBE_OFFSET_FROM_EXTRUDER', '', 0, 'type1'],
                         [_(u'调平时探针XY轴移动速度(mm/m)'), [1], 'edit', '>XY_PROBE_SPEED', '', 4000, 'type2'],
                         [_(u'调平时探针下降第一段速度(mm/m)'), [1], 'edit', '>Z_PROBE_SPEED_FAST', '', 600, 'type2'],
                         [_(u'调平时探针下降第二段速度(mm/m)'), [1], 'edit', '>Z_PROBE_SPEED_SLOW', '', 300, 'type2'],
                         [_(u'自动调平X轴上点数'), [1], 'edit', '>GRID_MAX_POINTS_X', '', 3, 'type2'],
                         [_(u'自动调平Y轴上点数'), [1], 'edit', '>GRID_MAX_POINTS_Y', '', 3, 'type2'],
                         [_(u'Z轴抬起/放下的距离'), [1], 'edit', '>Z_CLEARANCE_DEPLOY_PROBE', '', 20, 'type2'],
                         [_(u'Z轴在两个调平点的的移动高度'), [1], 'edit', '>Z_CLEARANCE_BETWEEN_PROBES', '', 20, 'type2'],
                         [_(u'调平热床边界距离X1'), [1], 'edit', '>LEFT_PROBE_BED_POSITION', '', 30, 'type2'],
                         [_(u'调平热床边界距离X2'), [1], 'edit', '>RIGHT_PROBE_BED_POSITION', '', 200, 'type2'],
                         [_(u'调平热床边界距离Y1'), [1], 'edit', '>FRONT_PROBE_BED_POSITION', '', 30, 'type2'],
                         [_(u'调平热床边界距离Y2'), [1], 'edit', '>BACK_PROBE_BED_POSITION', '', 200, 'type2'],
                         [_(u'MESH_BED_LEVELING调平模式下边界距离范围'), [1], 'edit', '>MESH_INSET', '', 20, 'type2'],
                         [_(u'DELTA_SEGMENTS_PER_SECOND'), [1], 'edit', '>BACK_PROBE_BED_POSITION', '', 40, 'type2'],
                         [_(u'DELTA_DIAGONAL_ROD'), [1], 'edit', '>DELTA_DIAGONAL_ROD', '', 346, 'type2'],
                         [_(u'DELTA_SMOOTH_ROD_OFFSET'), [1], 'edit', '>DELTA_SMOOTH_ROD_OFFSET', '', 211, 'type2'],
                         [_(u'DELTA_EFFECTOR_OFFSET'), [1], 'edit', '>DELTA_EFFECTOR_OFFSET', '', 28, 'type2'],
                         [_(u'DELTA_CARRIAGE_OFFSET'), [1], 'edit', '>DELTA_CARRIAGE_OFFSET', '', 14.5, 'type2'],
                         [_(u'DELTA_RADIUS'), [1], 'edit', '>DELTA_RADIUS', '', 169, 'type2'],
                         [_(u'DELTA_HEIGHT'), [1], 'edit', '>DELTA_HEIGHT', '', 302, 'type2'],
                         [_(u'DELTA_PRINTABLE_RADIUS'), [1], 'edit', '>DELTA_PRINTABLE_RADIUS', '', 125, 'type2'],
                         [_(u'DELTA_CALIBRATION_RADIUS'), [1], 'edit', '>DELTA_CALIBRATION_RADIUS', '', 100, 'type2'],
                         [_(u'WIFI模式'), [_(u'0:STA'), _(u'1:AP')], 'choose', '>CFG_WIFI_MODE', '', 1, ''],
                         [_(u'WIFI名称'), [1], 'edit', '>CFG_WIFI_AP_NAME', '', 'WIFITEST', 'type3'],
                         [_(u'WIFI密码'), [1], 'edit', '>CFG_WIFI_KEY_CODE', '', 'makerbase', 'type3'],
                         [_(u'云服务使能'), [_(u'0:禁止'), _(u'1:使能')], 'choose', '>CFG_CLOUD_ENABLE', '', 1, ''],
                         [_(u'云服务链接'), [1], 'edit', '>CFG_WIFI_CLOUD_HOST', '', 'www.baizhongyun.cn', 'type3'],
                         [_(u'云服务端口'), [1], 'edit', '>CFG_CLOUD_PORT', '', '10086', 'type2'],
                         [_(u'更多界面自定义数量按钮'), [1], 'edit', '>moreitem_pic_cnt', '', '7', 'type2'],
                         [_(u'更多界面自定义按钮1'), [1], 'edit', '>moreitem_button1_cmd:', '', 'G28 X0;G28 Y0;G28 Z0;', 'type3'],
                         [_(u'更多界面自定义按钮2'), [1], 'edit', '>moreitem_button2_cmd:', '', 'G28 X0;G28 Y0;G28 Z0;', 'type3'],
                         [_(u'更多界面自定义按钮3'), [1], 'edit', '>moreitem_button3_cmd:', '', 'G28 X0;G28 Y0;G28 Z0;', 'type3'],
                         [_(u'更多界面自定义按钮4'), [1], 'edit', '>moreitem_button4_cmd:', '', 'G28 X0;G28 Y0;G28 Z0;', 'type3'],
                         [_(u'更多界面自定义按钮5'), [1], 'edit', '>moreitem_button5_cmd:', '', 'G28 X0;G28 Y0;G28 Z0;', 'type3'],
                         [_(u'更多界面自定义按钮6'), [1], 'edit', '>moreitem_button6_cmd:', '', 'G28 X0;G28 Y0;G28 Z0;', 'type3'],
                         [_(u'更多界面自定义按钮7'), [1], 'edit', '>moreitem_button7_cmd:', '', 'G28 X0;G28 Y0;G28 Z0;', 'type3'],
                         [_(u'打印中更多界面自定义数量按钮'), [1], 'edit', '>morefunc_cnt', '', '7', 'type2'],
                         [_(u'打印中更多界面自定义按钮1'), [1], 'edit', '>morefunc1_cmd:', '', 'G28 X0;G28 Y0;G28 Z0;', 'type3'],
                         [_(u'打印中更多界面自定义按钮2'), [1], 'edit', '>morefunc2_cmd:', '', 'G28 X0;G28 Y0;G28 Z0;', 'type3'],
                         [_(u'打印中更多界面自定义按钮3'), [1], 'edit', '>morefunc3_cmd:', '', 'G28 X0;G28 Y0;G28 Z0;', 'type3'],
                         [_(u'打印中更多界面自定义按钮4'), [1], 'edit', '>morefunc4_cmd:', '', 'G28 X0;G28 Y0;G28 Z0;', 'type3'],
                         [_(u'屏幕背景色'), [1], 'edit', '>cfg_background_color', '', '0x000000', 'type3'],
                         [_(u'标题文字'), [1], 'edit', '>cfg_title_color', '', '0xFFFFFF', 'type3'],
                         [_(u'状态栏背景色'), [1], 'edit', '>cfg_state_bkcolor', '', '0x000000', 'type3'],
                         [_(u'状态栏字体颜色'), [1], 'edit', '>cfg_state_textcolor', '', '0xFFFFFF', 'type3'],
                         [_(u'文件目录按钮背景色'), [1], 'edit', '>cfg_filename_bkcolor', '', '0x000000', 'type3'],
                         [_(u'文件目录按钮字体颜色'), [1], 'edit', '>cfg_filename_textcolor', '', '0xFFFFFF', 'type3'],
                         [_(u'通用按钮背景色'), [1], 'edit', '>cfg_btn_bkcolor', '', '0x000000', 'type3'],
                         [_(u'通用按钮文字颜色'), [1], 'edit', '>cfg_btn_textcolor', '', '0xFFFFFF', 'type3'],
                         [_(u'状态按钮背景色'), [1], 'edit', '>cfg_state_btn_bkcolor', '', '0x000000', 'type3'],
                         [_(u'状态按钮字体颜色'), [1], 'edit', '>cfg_state_btn_textcolor', '', '0xFFFFFF', 'type3'],
                         [_(u'"返回"键背景色'), [1], 'edit', '>cfg_back_btn_bkcolor', '', '0x000000', 'type3'],
                         [_(u'"返回"键字体颜色'), [1], 'edit', '>cfg_back_btn_textcolor', '', '0xFFFFFF', 'type3'],
                         [_(u'选定按钮背景色'), [1], 'edit', '>cfg_sel_btn_bkcolor', '', '0x000000', 'type3'],
                         [_(u'选定按钮字体颜色'), [1], 'edit', '>cfg_sel_btn_textcolor', '', '0xFFFFFF', 'type3'],
                         [_(u'对话框按钮背景色'), [1], 'edit', '>cfg_dialog_btn_bkcolor', '', '0x000000', 'type3'],
                         [_(u'对话框按钮字体颜色'), [1], 'edit', '>cfg_dialog_btn_textcolor', '', '0xFFFFFF', 'type3'],
                         [_(u'按钮字体偏移底边位置'), [1], 'edit', '>cfg_btn_text_offset', '', 23, 'type2']
                         ]
        self._textlist = []
        self.btnlist = []
        self.choosefilebtnlist = []
        self.printingbtnlist = []
        self.widgetlist = []
        self.selectedpath = ""
        self.outputpath = None
        self.viewimglist = None
        self.selectbtnpos = 0
        self.viewpos = 0
        self.underselectpos = 0
        self._picwidth = 78
        self._picheight = 104
        self.progressing = False
        self._mdialog = None
        self.initview()
        self.Update()
        # pathname = sys.path[0] + "\\mks_pic\\"
        # self.progressthread = threading.Thread(target=lambda pn=pathname: self.inprogress(pn))
        # self.progressthread.setDaemon(True)
        # self.progressthread.start()
        # self.inputexample()

    def initview(self):
        self.SetMinSize((650, 580))
        self.SetSize((650, 580))
        self._mainpanel = wx.Panel(self,-1)
        self.toppanel = wx.Panel(self._mainpanel,-1,size=(-1,23))

        #toppanelview
        self.viewcbcopy = wx.ComboBox(self.toppanel, -1, value=self._typelist[0], choices=self._typelist,style=wx.CB_READONLY)
        self.viewcbcopy.Enable(False)
        self.viewcb = wx.ComboBox(self.toppanel, -1, value=self._typelist[0], choices=self._typelist,style=wx.CB_READONLY)
        self.viewcb.Bind(wx.EVT_COMBOBOX,lambda evt,widget = self.viewcb:self.pixelchange(evt,widget))
        self.viewcb.Enable(False)
        self._dlgbutton = wx.Button(self.toppanel, -1, _(u'配置文件'))
        self._dlgbutton.Bind(wx.EVT_BUTTON, self.showConfigDialog)
        # self.wtext = wx.StaticText(self.toppanel,-1,_(u'宽：'),style=wx.ALIGN_CENTER | wx.ST_NO_AUTORESIZE)
        # self.wctr = wx.TextCtrl(self.toppanel, -1, value='78',size=(50,-1))
        # self.htext = wx.StaticText(self.toppanel, -1,_(u'高：'), style=wx.ALIGN_CENTER | wx.ST_NO_AUTORESIZE)
        # self.hctr = wx.TextCtrl(self.toppanel, -1, value='104', size=(50, -1))
        self.language = wx.ComboBox(self.toppanel, -1, value=self.languagelist[0],choices=self.languagelist,style=wx.CB_READONLY)
        self.language.Bind(wx.EVT_COMBOBOX, lambda evt, widget=self.language: self.changelanguage(evt, widget))
        if self.languagename == 'en':
            self.language.SetValue(self.languagelist[1])
        self.topsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.topsizer.Add(self.viewcbcopy,0,wx.LEFT|wx.RIGHT,border=10)
        self.topsizer.Add(self.viewcb, 0, wx.LEFT | wx.RIGHT, border=10)
        # self.topsizer.Add(self.wtext, 0, wx.TOP, border=5)
        # self.topsizer.Add(self.wctr, 0, wx.RIGHT, border=10)
        # self.topsizer.Add(self.htext, 0, wx.TOP, border=5)
        # self.topsizer.Add(self.hctr, 0, wx.RIGHT, border=10)
        self.topsizer.Add(self.language,0,wx.LEFT,border=10)
        self.topsizer.Add(self._dlgbutton, 0, wx.LEFT, border=10)
        self.toppanel.SetSizer(self.topsizer)
        self.viewcb.Hide()


        self.makeImage('bai.png','#ffffff',False)
        self.makeImage('hei.png', '#000000',False)
        self.normalbitmap = wx.Image(os.path.abspath("")+"\\bai.png", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.hnormalbitmap = wx.Image(os.path.abspath("") + "\\hei.png", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.bottompanel = wx.Panel(self._mainpanel,-1)
        self.bottompanel.SetMinSize((480, 320))
        self.bottompanel.SetBackgroundColour('#000000')

        #topsizer with four image
        self.btlogo = self.getStaticBmp(self._mainpanel, self.normalbitmap, lambda e, pos=0: self.ChangeBitmap(e, pos))
        self.btlogo.SetMinSize((480, 320))
        self.btlogo.SetBackgroundColour('#000000')
        self.btlogo.SetDropTarget(FileDropTarget(self, self.dropCallback, 0))
        self.btone = self.getStaticBmp(self.bottompanel,self.normalbitmap, lambda e, pos=0: self.ChangeBitmap(e, pos))
        self.bttwo = self.getStaticBmp(self.bottompanel,self.normalbitmap, lambda e, pos=1: self.ChangeBitmap(e, pos))
        self.btthree = self.getStaticBmp(self.bottompanel,self.normalbitmap, lambda e, pos=2: self.ChangeBitmap(e, pos))
        self.btfour = self.getStaticBmp(self.bottompanel,self.normalbitmap, lambda e, pos=3: self.ChangeBitmap(e, pos))
        self.btone.SetDropTarget(FileDropTarget(self, self.dropCallback, 0))
        self.bttwo.SetDropTarget(FileDropTarget(self, self.dropCallback, 1))
        self.btthree.SetDropTarget(FileDropTarget(self, self.dropCallback, 2))
        self.btfour.SetDropTarget(FileDropTarget(self, self.dropCallback, 3))

        self.bbone = self.getStaticBmp(self.bottompanel,self.normalbitmap, lambda e, pos=4: self.ChangeBitmap(e, pos))
        self.bbtwo = self.getStaticBmp(self.bottompanel,self.normalbitmap, lambda e, pos=5: self.ChangeBitmap(e, pos))
        self.bbthree = self.getStaticBmp(self.bottompanel,self.normalbitmap, lambda e, pos=6: self.ChangeBitmap(e, pos))
        self.bbfour = self.getStaticBmp(self.bottompanel,self.normalbitmap, lambda e, pos=7: self.ChangeBitmap(e, pos))
        self.bbone.SetDropTarget(FileDropTarget(self, self.dropCallback, 4))
        self.bbtwo.SetDropTarget(FileDropTarget(self, self.dropCallback, 5))
        self.bbthree.SetDropTarget(FileDropTarget(self, self.dropCallback, 6))
        self.bbfour.SetDropTarget(FileDropTarget(self, self.dropCallback, 7))

        self.btnlist[:] =[self.btone,self.bttwo,self.btthree,self.btfour,self.bbone,self.bbtwo,self.bbthree,self.bbfour]

        # self.btone.SetSize((320, 240))
        # for i in range(1, len(self.btnlist)):
            # self.btnlist[i].Hide()

        self.choosefilepanel = wx.Panel(self._mainpanel,-1)
        self.choosefilepanel.SetMinSize((480, 320))
        self.choosefilepanel.SetBackgroundColour('#000000')
        # 第一列
        self.cfone = self.getStaticBmp(self.choosefilepanel, self.normalbitmap, lambda e, pos=0: self.choosefileChangeBitmap(e, pos))
        self.cftwo = self.getStaticBmp(self.choosefilepanel, self.normalbitmap, lambda e, pos=1: self.choosefileChangeBitmap(e, pos))
        self.cfone.SetDropTarget(FileDropTarget(self, self.dropCallback, 0))
        self.cftwo.SetDropTarget(FileDropTarget(self, self.dropCallback, 1))
        # 第二列
        self.cfbone = self.getStaticBmp(self.choosefilepanel, self.normalbitmap, lambda e, pos=2: self.choosefileChangeBitmap(e, pos))
        self.cfbtwo = self.getStaticBmp(self.choosefilepanel, self.normalbitmap, lambda e, pos=3: self.choosefileChangeBitmap(e, pos))
        self.cfbone.SetDropTarget(FileDropTarget(self, self.dropCallback, 2))
        self.cfbtwo.SetDropTarget(FileDropTarget(self, self.dropCallback, 3))
        # 第三列
        self.cfdone = self.getStaticBmp(self.choosefilepanel, self.normalbitmap, lambda e, pos=4: self.choosefileChangeBitmap(e, pos))
        self.cfdtwo = self.getStaticBmp(self.choosefilepanel, self.normalbitmap, lambda e, pos=5: self.choosefileChangeBitmap(e, pos))
        self.cfdone.SetDropTarget(FileDropTarget(self, self.dropCallback, 4))
        self.cfdtwo.SetDropTarget(FileDropTarget(self, self.dropCallback, 5))
        # 竖列
        self.cfhone = self.getWHBmp(self.choosefilepanel, self.normalbitmap,117,92, lambda e, pos=6: self.choosefileChangeBitmap(e, pos))
        self.cfhtwo = self.getWHBmp(self.choosefilepanel, self.normalbitmap,117,92, lambda e, pos=7: self.choosefileChangeBitmap(e, pos))
        self.cfhthree = self.getWHBmp(self.choosefilepanel, self.normalbitmap,117,92, lambda e, pos=8: self.choosefileChangeBitmap(e, pos))
        self.cfhone.SetDropTarget(FileDropTarget(self, self.dropCallback, 6))
        self.cfhtwo.SetDropTarget(FileDropTarget(self, self.dropCallback, 7))
        self.cfhthree.SetDropTarget(FileDropTarget(self, self.dropCallback, 8))
        self.choosefilebtnlist[:] = [self.cfone, self.cftwo, self.cfbone, self.cfbtwo, self.cfdone, self.cfdtwo, self.cfhone, self.cfhtwo, self.cfhthree]
        self.cflefttopsizer = wx.BoxSizer(wx.VERTICAL)
        self.cflefttopsizer.Add(self.cfone, 0, wx.ALL|wx.ALIGN_CENTER|wx.ALIGN_RIGHT, border=1)
        self.cflefttopsizer.Add(self.cftwo, 0, wx.ALL|wx.ALIGN_CENTER|wx.ALIGN_RIGHT, border=1)
        self.cfleftbotsizer = wx.BoxSizer(wx.VERTICAL)
        self.cfleftbotsizer.Add(self.cfbone, 0, wx.ALL|wx.ALIGN_CENTER,border=1)
        self.cfleftbotsizer.Add(self.cfbtwo, 0, wx.ALL|wx.ALIGN_CENTER, border=1)
        self.cfleftsizer = wx.BoxSizer(wx.VERTICAL)
        self.cfleftsizer.Add(self.cfdone, 0, wx.ALL,border=1)
        self.cfleftsizer.Add(self.cfdtwo, 0, wx.ALL, border=1)
        self.cfrightsizer = wx.BoxSizer(wx.VERTICAL)
        self.cfrightsizer.Add(self.cfhone, 0, wx.ALL,border=1)
        self.cfrightsizer.Add(self.cfhtwo, 0,  wx.ALL, border=1)
        self.cfrightsizer.Add(self.cfhthree, 0,  wx.ALL, border=1)
        self.cfsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.cfsizer.Add(self.cflefttopsizer, 2, wx.ALIGN_CENTER|wx.ALIGN_RIGHT, border=1)
        self.cfsizer.Add(self.cfleftbotsizer, 1, wx.ALIGN_CENTER, border=1)
        self.cfsizer.Add(self.cfleftsizer, 1, wx.ALIGN_CENTER, border=1)
        self.cfsizer.Add(self.cfrightsizer, 2, wx.ALIGN_CENTER|wx.ALIGN_LEFT, border=1)
        self.choosefilepanel.SetSizer(self.cfsizer)

        self.printingpanel = wx.Panel(self._mainpanel, -1)
        self.printingpanel.SetMinSize((480, 320))
        self.printingpanel.SetBackgroundColour('#000000')
        self.ptone = self.getWHBmp(self.printingpanel, self.normalbitmap,200,200, lambda e, pos=0: self.printingChangeBitmap(e, pos))
        self.ptone.SetDropTarget(FileDropTarget(self, self.dropCallback, 0))
        self.pbone = self.getWHBmp(self.printingpanel, self.normalbitmap,150,80, lambda e, pos=1: self.printingChangeBitmap(e, pos))
        self.pbtwo = self.getWHBmp(self.printingpanel, self.normalbitmap,150,80, lambda e, pos=2: self.printingChangeBitmap(e, pos))
        self.pbthree = self.getWHBmp(self.printingpanel, self.normalbitmap,150,80, lambda e, pos=3: self.printingChangeBitmap(e, pos))
        self.pbone.SetDropTarget(FileDropTarget(self, self.dropCallback, 1))
        self.pbtwo.SetDropTarget(FileDropTarget(self, self.dropCallback, 2))
        self.pbthree.SetDropTarget(FileDropTarget(self, self.dropCallback, 3))
        self.printingbtnlist[:] = [self.ptone, self.pbone, self.pbtwo, self.pbthree]
        self.ptsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.ptsizer.Add(self.ptone, 0, wx.ALL | wx.ALIGN_BOTTOM, border=1)
        self.pbsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.pbsizer.Add(self.pbone, 0, wx.ALL,border=1)
        self.pbsizer.Add(self.pbtwo, 0, wx.TOP|wx.BOTTOM, border=1)
        self.pbsizer.Add(self.pbthree, 0, wx.ALL, border=1)
        self.printingsizer = wx.BoxSizer(wx.VERTICAL)
        self.printingsizer.Add(self.ptsizer, 1, wx.ALIGN_BOTTOM | wx.ALIGN_CENTER, border=0)
        self.printingsizer.Add(self.pbsizer, 1, wx.ALIGN_CENTER, border=0)
        self.printingpanel.SetSizer(self.printingsizer)
        #
        # # 操作与暂停
        # self.btone1 = self.getWHBmp(self.bottompanel,self.normalbitmap, lambda e, pos=0: self.ChangeBitmap(e, pos))
        # self.bttwo1 = self.getWHBmp(self.bottompanel,self.normalbitmap, lambda e, pos=1: self.ChangeBitmap(e, pos))
        # self.btthree1 = self.getWHBmp(self.bottompanel,self.normalbitmap, lambda e, pos=2: self.ChangeBitmap(e, pos))
        # self.btfour1 = self.getWHBmp(self.bottompanel,self.normalbitmap, lambda e, pos=3: self.ChangeBitmap(e, pos))
        # self.btone1.SetDropTarget(FileDropTarget(self, self.dropCallback, 0))
        # self.bttwo1.SetDropTarget(FileDropTarget(self, self.dropCallback, 1))
        # self.btthree1.SetDropTarget(FileDropTarget(self, self.dropCallback, 2))
        # self.btfour1.SetDropTarget(FileDropTarget(self, self.dropCallback, 3))
        # self.btnlist1[:] =[self.btone1,self.bttwo1,self.btthree1,self.btfour1,self.bbone,self.bbtwo,self.bbthree,self.bbfour]
        # self.btsizer1 = wx.BoxSizer(wx.HORIZONTAL)
        # self.btsizer1.Add(self.btone1, 0, wx.ALL | wx.ALIGN_BOTTOM, border=1)
        # self.btsizer1.Add(self.bttwo1, 0, wx.TOP | wx.BOTTOM | wx.ALIGN_BOTTOM, border=1)
        # self.btsizer1.Add(self.btthree1, 0, wx.LEFT | wx.TOP | wx.BOTTOM | wx.ALIGN_BOTTOM, border=1)
        # self.btsizer1.Add(self.btfour1, 0, wx.ALL | wx.ALIGN_BOTTOM, border=1)
        # # bottomsizer width four image
        # self.bbsizer = wx.BoxSizer(wx.HORIZONTAL)
        # self.bbsizer1.Add(self.bbone, 0, wx.ALL, border=1)
        # self.bbsizer1.Add(self.bbtwo, 0, wx.TOP | wx.BOTTOM, border=1)
        # self.bbsizer1.Add(self.bbthree, 0, wx.LEFT | wx.TOP | wx.BOTTOM, border=1)
        # self.bbsizer1.Add(self.bbfour, 0, wx.ALL, border=1)


        self.btsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.btsizer.Add(self.btone,0,wx.ALL|wx.ALIGN_BOTTOM,border=1)
        self.btsizer.Add(self.bttwo, 0, wx.TOP|wx.BOTTOM|wx.ALIGN_BOTTOM, border=1)
        self.btsizer.Add(self.btthree, 0, wx.LEFT|wx.TOP|wx.BOTTOM|wx.ALIGN_BOTTOM, border=1)
        self.btsizer.Add(self.btfour, 0, wx.ALL|wx.ALIGN_BOTTOM, border=1)
        #bottomsizer width four image
        self.bbsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.bbsizer.Add(self.bbone, 0, wx.ALL,border=1)
        self.bbsizer.Add(self.bbtwo, 0, wx.TOP|wx.BOTTOM, border=1)
        self.bbsizer.Add(self.bbthree, 0, wx.LEFT|wx.TOP|wx.BOTTOM, border=1)
        self.bbsizer.Add(self.bbfour, 0, wx.ALL, border=1)

        self.bottomsizer = wx.BoxSizer(wx.VERTICAL)
        self.bottomsizer.Add(self.btsizer,1,wx.ALIGN_BOTTOM|wx.ALIGN_CENTER,border=0)
        self.bottomsizer.Add(self.bbsizer, 1, wx.ALIGN_CENTER, border=0)
        self.bottompanel.SetSizer(self.bottomsizer)
        self.makeImage('zxc.png', '#000000',True)
        self.underbitmap = wx.Image(os.path.abspath("") + "\\zxc.png", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        # self.underbitmap = self.underbitmap.ConvertToBitmap()
        self.addview = wx.Panel(self._mainpanel,-1,size=(355,140),style=wx.SIMPLE_BORDER)
        # self.addview.SetMaxSize((355, 140))
        self.addview.SetMinSize((355, 140))
        self.addone = self.getStaticBmp(self.addview,self.underbitmap,lambda e, pos=0: self.addImage(e,pos),lambda e, pos=0:self.showpopupmenu(e,pos))
        self.addtwo = self.getStaticBmp(self.addview,self.underbitmap,lambda e, pos=1: self.addImage(e,pos),lambda e, pos=1:self.showpopupmenu(e,pos))
        self.addthree = self.getStaticBmp(self.addview,self.underbitmap,lambda e, pos=2: self.addImage(e,pos),lambda e, pos=2:self.showpopupmenu(e,pos))
        self.addone.SetDropTarget(FileDropTarget(self, self.dropOTTCallback, 0))
        self.addtwo.SetDropTarget(FileDropTarget(self, self.dropOTTCallback, 1))
        self.addthree.SetDropTarget(FileDropTarget(self, self.dropOTTCallback, 2))
        self.addsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.addsizer.Add(self.addone,0,wx.ALIGN_CENTER|wx.RIGHT|wx.LEFT,border=30)
        self.addsizer.Add(self.addtwo, 0, wx.ALIGN_CENTER, border=0)
        self.addsizer.Add(self.addthree, 0, wx.ALIGN_CENTER|wx.RIGHT|wx.LEFT, border=30)
        self.addview.SetSizer(self.addsizer)

        self.addone.Disable()
        self.addtwo.Disable()
        self.addthree.Disable()


        self.footbar = wx.Panel(self._mainpanel,-1,size=(-1,23))
        self.message = wx.StaticText(self.footbar,-1,_(u'准备..'),style=wx.ALIGN_LEFT | wx.ST_NO_AUTORESIZE)
        self.outputbutton = wx.Button(self.footbar, -1, _(u"导出文件"))
        self.inputbutton = wx.Button(self.footbar, -1, _(u'导入文件夹'))
        self.examplebutton = wx.Button(self.footbar, -1, _(u'导入模板'))
        self.outputbutton.Bind(wx.EVT_BUTTON,self.exportbin)
        self.inputbutton.Bind(wx.EVT_BUTTON, self.inputbin)
        self.examplebutton.Bind(wx.EVT_BUTTON, self.inputexample)
        self.footsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.footsizer.Add(self.message,1,wx.EXPAND|wx.TOP,border=5)
        self.footsizer.Add(self.inputbutton, 0, wx.EXPAND, border = 0)
        self.footsizer.Add(self.outputbutton,0,wx.EXPAND,border=0)
        self.footsizer.Add(self.examplebutton,0,wx.EXPAND,border=0)
        self.footbar.SetSizer(self.footsizer)


        self._mainsizer = wx.BoxSizer(wx.VERTICAL)
        self._mainsizer.Add(self.toppanel,0,wx.EXPAND,border=0)
        self._mainsizer.Add(self.btlogo, 0, wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM,border=5)
        self._mainsizer.Add(self.bottompanel,0,wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM,border=5)
        self._mainsizer.Add(self.choosefilepanel, 0, wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=5)
        self._mainsizer.Add(self.printingpanel, 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=5)
        self._mainsizer.Add(self.addview,0,wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM,border=5)
        self._mainsizer.Add(self.footbar,0,wx.EXPAND|wx.ALIGN_BOTTOM,border=0)

        self.bottompanel.Hide()
        self.choosefilepanel.Hide()
        self.printingpanel.Hide()

        self._listview = wx.ListBox(self._mainpanel, -1, choices=self._viewlist)
        self._listview.SetSelection(0)
        self._listview.Bind(wx.EVT_LISTBOX,lambda evt,widget = self._listview:self.comboboxsl(evt,widget))
        self._newmainsizer = wx.BoxSizer(wx.HORIZONTAL)
        self._newmainsizer.Add(self._listview, 0, wx.EXPAND)
        self._newmainsizer.Add(self._mainsizer, 1, wx.EXPAND)
        self.addview.Layout()
        self._mainpanel.SetSizer(self._newmainsizer)

    def inputexample(self,e):
        value = self.viewcb.GetSelection()
        if value == 1 :
            pathname = sys.path[0] + "\\mks_pic35\\"
            self.progressthread = threading.Thread(target=lambda pn=pathname: self.inprogress(pn))
            self.progressthread.setDaemon(True)
            self.progressthread.start()
        elif value == 2 :
            pathname = sys.path[0] + "\\mks_picdiy\\"
            self.progressthread = threading.Thread(target=lambda pn=pathname: self.inprogress(pn))
            self.progressthread.setDaemon(True)
            self.progressthread.start()
        else:
            pathname = sys.path[0] + "\\mks_pic32\\"
            self.progressthread = threading.Thread(target=lambda pn=pathname: self.inprogress(pn))
            self.progressthread.setDaemon(True)
            self.progressthread.start()

    def dropCallback(self, txt, pos):
        try:
            # Image.open(txt)
            size = Image.open(txt).size
            listvalue = self._listview.GetSelection()
            value = self.viewcb.GetSelection()
            if listvalue == 0:
                if value == 0:
                    if (size[0] != 320 or size[1] != 240):
                        self.message.SetLabel(u'请放入320x240像素的bmp格式文件')
                        return
                if value == 1:
                    if (size[0] != 480 or size[1] != 320):
                        self.message.SetLabel(u'请放入480x320像素的bmp格式文件')
                        return
            elif listvalue == 12 and (value == 1):
                if pos == 0:
                    if (size[0] != 100 or size[1] != 100):
                        self.message.SetLabel(u'请放入100x100像素的bmp格式文件')
                        return
                else:
                    if (size[0] != 117 or size[1] != 92):
                        self.message.SetLabel(u'请放入117x92像素的bmp格式文件')
                        return
            elif listvalue == 13 and (value == 1):
                if pos == 0:
                    if (size[0] != 200 or size[1] != 200):
                        self.message.SetLabel(u'请放入200x200像素的bmp格式文件')
                        return
                else:
                    if (size[0] != 150 or size[1] != 80):
                        self.message.SetLabel(u'请放入150x80像素的bmp格式文件')
                        return
            else:
                if value == 0:
                    if (size[0] != 78 or size[1] != 104):
                        self.message.SetLabel(u'请放入78x104像素的bmp格式文件')
                        return
                if value == 1:
                    if (size[0] != 117 or size[1] != 140):
                        self.message.SetLabel(u'请放入117x140像素的bmp格式文件')
                        return
            if self.viewimglist[pos][0] != '':
                if listvalue == 12 and (value == 1):
                    self.choosefileimagelist[pos][0] = txt
                    self.allimglist35[self.viewpos][:] = self.choosefileimagelist
                    self.choosefilebtnlist[pos].SetBitmap(self.getBitmap(txt, self.gettextlist()[pos]))
                elif listvalue == 13 and (value == 1):
                    self.printingimagelist[pos][0] = txt
                    self.allimglist35[self.viewpos][:] = self.printingimagelist
                    self.printingbtnlist[pos].SetBitmap(self.getBitmap(txt, self.gettextlist()[pos]))
                else:
                    self.imagelist[pos][0] = txt
                    if value == 1:
                        self.allimglist35[self.viewpos][:] = self.imagelist
                    else:
                        self.allimglist32[self.viewpos][:] = self.imagelist

                    self.btnlist[pos].SetBitmap(self.getBitmap(txt, self.gettextlist()[pos]))
                self.addone.SetBitmap(self.getBitmap(txt, ''))
                self.message.SetLabel(u'导入文件成功')
        except Exception as e:
            return

    def dropOTTCallback(self, txt, pos):
        try:
            # Image.open(txt)
            size = Image.open(txt).size
            listvalue = self._listview.GetSelection()
            value = self.viewcb.GetSelection()
            print(size[0], size[1], value)
            if listvalue == 0:
                if value == 0:
                    if (size[0] != 320 or size[1] != 240):
                        self.message.SetLabel(u'请放入320x240像素的bmp格式文件')
                        return
                if value == 1:
                    if (size[0] != 480 or size[1] != 320):
                        self.message.SetLabel(u'请放入480x320像素的bmp格式文件')
                        return
            elif listvalue == 12 and (value == 1):
                if pos == 0:
                    if (size[0] != 100 or size[1] != 100):
                        self.message.SetLabel(u'请放入100x100像素的bmp格式文件')
                        return
                else:
                    if (size[0] != 117 or size[1] != 92):
                        self.message.SetLabel(u'请放入117x92像素的bmp格式文件')
                        return
            elif listvalue == 13 and (value == 1):
                if pos == 0:
                    if (size[0] != 200 or size[1] != 200):
                        self.message.SetLabel(u'请放入200x200像素的bmp格式文件')
                        return
                else:
                    if (size[0] != 150 or size[1] != 80):
                        self.message.SetLabel(u'请放入150x80像素的bmp格式文件')
                        return
            else:
                if value == 0:
                    if (size[0] != 78 or size[1] != 104):
                        self.message.SetLabel(u'请放入78x104像素的bmp格式文件')
                        return
                if value == 1:
                    if (size[0] != 117 or size[1] != 140):
                        self.message.SetLabel(u'请放入117x140像素的bmp格式文件')
                        return
            if self.viewimglist[self.selectbtnpos][pos] != '':
                if listvalue == 12 and (value == 1):
                    self.choosefileimagelist[self.selectbtnpos][pos] = txt
                    self.allimglist35[self.viewpos][:] = self.choosefileimagelist
                    if pos == 0:
                        self.choosefilebtnlist[self.selectbtnpos].SetBitmap(self.getBitmap(txt, self.gettextlist()[self.selectbtnpos]))
                        self.addone.SetBitmap(self.getBitmap(txt, ''))
                    elif pos == 1:
                        self.addtwo.SetBitmap(self.getBitmap(txt, ''))
                    elif pos == 2:
                        self.addthree.SetBitmap(self.getBitmap(txt, ''))
                elif listvalue == 13 and (value == 1):
                    self.printingimagelist[self.selectbtnpos][pos] = txt
                    self.allimglist35[self.viewpos][:] = self.printingimagelist
                    if pos == 0:
                        self.printingbtnlist[self.selectbtnpos].SetBitmap(self.getBitmap(txt, self.gettextlist()[self.selectbtnpos]))
                        self.addone.SetBitmap(self.getBitmap(txt, ''))
                    elif pos == 1:
                        self.addtwo.SetBitmap(self.getBitmap(txt, ''))
                    elif pos == 2:
                        self.addthree.SetBitmap(self.getBitmap(txt, ''))
                else:
                    self.imagelist[self.selectbtnpos][pos] = txt
                    if value == 1:
                        self.allimglist35[self.viewpos][:] = self.imagelist
                    else:
                        self.allimglist32[self.viewpos][:] = self.imagelist

                    if pos == 0:
                        self.btnlist[self.selectbtnpos].SetBitmap(self.getBitmap(txt, self.gettextlist()[self.selectbtnpos]))
                        self.addone.SetBitmap(self.getBitmap(txt, ''))
                    elif pos == 1:
                        self.addtwo.SetBitmap(self.getBitmap(txt, ''))
                    elif pos == 2:
                        self.addthree.SetBitmap(self.getBitmap(txt, ''))
                self.message.SetLabel(u'导入文件成功')
        except Exception as e:
            return

    def RefreshBitmap(self):
        # self.SetSize((510, 410))

        if self.viewimglist is None:
            self.viewimglist = self.getbinname(self._viewlist[0])
        value = self.viewcb.GetSelection()
        if self.viewpos == 12 and (value == 1):
            list = self.choosefileimagelist
            self.viewimglist = self.getbinname(self._viewlist[12])
        elif self.viewpos == 13 and (value == 1):
            list = self.printingimagelist
        else:
            if value == 1:
                list = self.allimglist35[self.viewpos]
            else:
                list = self.allimglist32[self.viewpos]
        for i in range(0,len(self.viewimglist)):
            if self.viewpos == 0 and list[0][0] is not None:
                self.btlogo.SetBitmap(self.getBitmap(list[0][0], ''))
            elif self.viewimglist[i][0] == '':
                if self.viewpos == 12 and (value == 1):
                    self.choosefilebtnlist[i].SetBitmap(self.hnormalbitmap)
                elif self.viewpos == 13 and (value == 1):
                    if i < 4:
                        self.printingbtnlist[i].SetBitmap(self.hnormalbitmap)
                else:
                    self.btnlist[i].SetBitmap(self.hnormalbitmap)
            else:
                if i < len(list) and list[i][0] is not None:
                    if self.viewpos == 12 and (value == 1):
                        self.choosefilebtnlist[i].SetBitmap(self.getBitmap(list[i][0], self.gettextlist()[i]))
                        self.addone.SetBitmap(self.getBitmap(list[i][0], ''))
                    elif self.viewpos == 13 and (value == 1):
                        if i < 4:
                            self.printingbtnlist[i].SetBitmap(self.getBitmap(list[i][0], self.gettextlist()[i]))
                            self.addone.SetBitmap(self.getBitmap(list[i][0], ''))
                    elif (self.viewpos == 14 or self.viewpos == 15) and (value == 1):
                        if i == 0 or i == 3:
                            self.btnlist[i].SetSize(wx.Size(150, 80))
                            self.btnlist[i].SetBitmap(self.getBitmap(list[i][0], self.gettextlist()[i]))
                            self.addone.SetBitmap(self.getBitmap(list[i][0], ''))
                        elif i == 1 or i == 2:
                            self.btnlist[i].SetSize(wx.Size(50, 80))
                            self.makeWHImage('bai2.png','#FFFFFF',True,50,80)
                            sbitmap = wx.Image(os.path.abspath("") + "\\bai2.png", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
                            self.btnlist[i].SetBitmap(sbitmap)
                            self.addone.SetBitmap(self.getBitmap(list[i][0], ''))
                        else:
                            self.btnlist[i].SetBitmap(self.getBitmap(list[i][0], self.gettextlist()[i]))
                            self.addone.SetBitmap(self.getBitmap(list[i][0], ''))

                    else:
                        self.btnlist[i].SetBitmap(self.getBitmap(list[i][0], self.gettextlist()[i]))
                        self.addone.SetBitmap(self.getBitmap(list[i][0], ''))
                elif list[i][1] is not None:
                    self.addtwo.SetBitmap(self.getBitmap(list[i][1], ''))
                elif list[i][2] is not None:
                    self.addthree.SetBitmap(self.getBitmap(list[i][2], ''))
                else:
                    if self.viewpos == 12 and (value == 1):
                        self.choosefilebtnlist[i].SetBitmap(self.normalbitmap)
                    elif self.viewpos == 13 and (value == 1):
                        if i < 4:
                            self.printingbtnlist[i].SetBitmap(self.normalbitmap)
                    else:
                        self.btnlist[i].SetBitmap(self.normalbitmap)

    def getLanguage(self):
        result = 'en'
        if not os.path.exists(os.path.abspath('')+'\\l.l'):
            f = open(os.path.abspath('')+'\\l.l','w')
            f.write(result)
            f.close()
        else:
            f = open(os.path.abspath('')+'\\l.l','r')
            content = f.read()
            if content == 'zh_CN':
                result = content
            f.close()
        return result
    def changelanguage(self,e,widget):
        value = widget.GetValue()
        content = 'zh_CN'
        f = open(os.path.abspath('') + '\\l.l', 'w')
        if value == self.languagelist[0]:
            f.write(content)
        elif value == self.languagelist[1]:
            f.write('en')
        f.close()



    def addImage(self,e,pos):
        with wx.FileDialog(self, _(u"选择你的图标文件"),defaultDir=self.selectedpath, wildcard="img files (*.png;*.jpg;)|*.png;*.jpg;",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            pathname = fileDialog.GetPath()
            size = Image.open(pathname).size
            listvalue = self._listview.GetSelection()
            value = self.viewcb.GetSelection()
            if listvalue == 0:
                if value == 0:
                    if (size[0] != 320 or size[1] != 240):
                        self.message.SetLabel(u'请放入320x240像素的bmp格式文件')
                        return
                if value == 1:
                    if (size[0] != 480 or size[1] != 320):
                        self.message.SetLabel(u'请放入480x320像素的bmp格式文件')
                        return
            elif listvalue == 12 and value == 1:
                if self.selectbtnpos == 0:
                    if (size[0] != 100 or size[1] != 100):
                        self.message.SetLabel(u'请放入100x100像素的bmp格式文件')
                        return
                else:
                    if (size[0] != 117 or size[1] != 92):
                        self.message.SetLabel(u'请放入117x92像素的bmp格式文件')
                        return
            elif listvalue == 13 and value == 1:
                if self.selectbtnpos == 0:
                    if (size[0] != 200 or size[1] != 200):
                        self.message.SetLabel(u'请放入200x200像素的bmp格式文件')
                        return
                else:
                    if (size[0] != 150 or size[1] != 80):
                        self.message.SetLabel(u'请放入150x80像素的bmp格式文件')
                        return
            else:
                if value == 0:
                    if (size[0] != 78 or size[1] != 104):
                        self.message.SetLabel(u'请放入78x104像素的bmp格式文件')
                        return
                if value == 1:
                    if (size[0] != 117 or size[1] != 140):
                        self.message.SetLabel(u'请放入117x140像素的bmp格式文件')
                        return
            if listvalue == 12 and value == 1:
                self.choosefileimagelist[self.selectbtnpos][pos] = pathname
                self.allimglist35[self.viewpos][:] = self.choosefileimagelist
                self.choosefilebtnlist[self.selectbtnpos].SetBitmap()
            elif listvalue == 13 and value == 1:
                self.printingimagelist[self.selectbtnpos][pos] = pathname
                self.allimglist35[self.viewpos][:] = self.printingimagelist
                self.printingbtnlist[self.selectbtnpos].SetBitmap(self.getBitmap(pathname, self.gettextlist()[self.selectbtnpos]))
            else:
                self.imagelist[self.selectbtnpos][pos] = pathname
                if value == 1:
                    self.allimglist35[self.viewpos][:] = self.imagelist
                else:
                    self.allimglist32[self.viewpos][:] = self.imagelist
                self.btnlist[self.selectbtnpos].SetBitmap(self.getBitmap(pathname, self.gettextlist()[self.selectbtnpos]))
            if pos == 0:
                self.addone.SetBitmap(self.getBitmap(pathname, ''))
            elif pos == 1:
                self.addtwo.SetBitmap(self.getBitmap(pathname, ''))
            elif pos == 2:
                self.addthree.SetBitmap(self.getBitmap(pathname, ''))
            # i = 0
            # for a in self.allimglist:
            #     if len(a)>0:
            #         for b in a:
            #             for c in b:
            #                 if c is not None:
            #                     i+=1
            # self.message.SetLabel(_(u'已添加 ')+str(i)+_(u'张图片'))
            self.selectedpath = fileDialog.GetDirectory()
        e.Skip()

    def showImage(self,e):
        if self.underselectpos == 0 and self.imagelist[self.selectbtnpos][0] is not None:
            self.btnlist[self.selectbtnpos].SetBitmap(self.getBitmap(self.imagelist[self.selectbtnpos][0], ''))
        elif self.underselectpos == 1 and self.imagelist[self.selectbtnpos][1] is not None:
            self.btnlist[self.selectbtnpos].SetBitmap(self.getBitmap(self.imagelist[self.selectbtnpos][1], ''))
        elif self.underselectpos == 2 and self.imagelist[self.selectbtnpos][2] is not None:
            self.btnlist[self.selectbtnpos].SetBitmap(self.getBitmap(self.imagelist[self.selectbtnpos][2], ''))
        if e is not None:
            e.Skip()
    def deleteimg(self,e):
        value = self.viewcb.GetSelection()
        if self.underselectpos == 0:
            self.imagelist[self.selectbtnpos][0] = None
            if value == 1:
                self.allimglist35[self.viewpos][:] = self.imagelist
            else:
                self.allimglist32[self.viewpos][:] = self.imagelist
            self.addone.SetBitmap(self.underbitmap)
        elif self.underselectpos == 1:
            self.imagelist[self.selectbtnpos][1] = None
            if value == 1:
                self.allimglist35[self.viewpos][:] = self.imagelist
            else:
                self.allimglist32[self.viewpos][:] = self.imagelist
            self.addtwo.SetBitmap(self.underbitmap)
        elif self.underselectpos == 2:
            self.imagelist[self.selectbtnpos][2] = None
            if value == 1:
                self.allimglist35[self.viewpos][:] = self.imagelist
            else:
                self.allimglist32[self.viewpos][:] = self.imagelist
            self.addthree.SetBitmap(self.underbitmap)

    def showpopupmenu(self,e,pos):
        menu = wx.Menu()
        # addtt = wx.MenuItem(menu, wx.NewId(), _(u'添加到预览界面'))
        deltt = wx.MenuItem(menu, wx.NewId(), _(u'删除'))
        id = menu.Append(0,_(u'添加到预览界面'))

        self.underselectpos = pos
        # self.Bind(wx.EVT_MENU,self.showImage,addtt)
        # self.Bind(wx.EVT_MENU,self.deleteimg, deltt)
        self.Bind(wx.EVT_MENU,self.showImage,id)
        id = menu.Append(1, _(u'删除'))
        self.Bind(wx.EVT_MENU, self.deleteimg, id)
        self.PopupMenu(menu, self.ScreenToClient(wx.GetMousePosition()))
        menu.Destroy()
        e.Skip()

    def getBitmap(self,filepath, text):
        try:
            bmp = wx.Image(filepath, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
            if text is not '':
                dc = wx.MemoryDC()
                dc.SelectObject(bmp)
                # dc.Clear()
                dc.SetTextForeground((255, 255, 255))
                tw, th = dc.GetTextExtent(text)
                mh = 10
                if self.viewcb.GetSelection() == 1:
                    mh = 25
                dc.DrawText(text, (self._picwidth - tw) / 2, self._picheight - th - mh)
                dc.SelectObject(wx.NullBitmap)
            return bmp
        except Exception as e:
            return self.normalbitmap

    def sizeChange(self,e):
        # .Bind(wx.EVT_TEXT, lambda evt: self.checkisnum(evt, rightpart))
        width = self._picwidth
        height = self._picheight
        if width >= 78 and height>=104:
            # self.SetSize((510, 410))
            self.SetSize()
    def ChangeBitmap(self,e,pos):
        # self.addone.SetBitmap(self.normalbitmap)
        # self.addone.Disable()
        self.selectbtnpos = pos
        self.addone.Enable()
        self.addtwo.Enable()
        self.addthree.Enable()
        self.addone.SetBitmap(self.underbitmap)
        self.addtwo.SetBitmap(self.underbitmap)
        self.addthree.SetBitmap(self.underbitmap)
        if self.viewimglist is None:
            self.viewimglist = self.getbinname(self._viewlist[0])
        if self.viewimglist[pos][0] == '':
            self.addone.Disable()
        else:
            if self.imagelist[pos][0] is not None:
                self.addone.SetBitmap(self.getBitmap(self.imagelist[pos][0], ''))
        if self.viewimglist[pos][1] == '':
            self.addtwo.Disable()
        else:
            if self.imagelist[pos][1] is not None:
                self.addtwo.SetBitmap(self.getBitmap(self.imagelist[pos][1], ''))
        if self.viewimglist[pos][2] == '':
            self.addthree.Disable()
        else:
            if self.imagelist[pos][2] is not None:
                self.addthree.SetBitmap(self.getBitmap(self.imagelist[pos][2], ''))
        if e is not None:
            e.Skip()

    def choosefileChangeBitmap(self,e,pos):
        # self.addone.SetBitmap(self.normalbitmap)
        # self.addone.Disable()
        self.selectbtnpos = pos
        self.addone.Enable()
        self.addtwo.Enable()
        self.addthree.Enable()
        self.addone.SetBitmap(self.underbitmap)
        self.addtwo.SetBitmap(self.underbitmap)
        self.addthree.SetBitmap(self.underbitmap)
        if self.viewimglist is None:
            self.viewimglist = self.getbinname(self._viewlist[12])
        if self.viewimglist[pos][0] == '':
            self.addone.Disable()
        else:
            if self.choosefileimagelist[pos][0] is not None:
                self.addone.SetBitmap(self.getBitmap(self.choosefileimagelist[pos][0], ''))
        if self.viewimglist[pos][1] == '':
            self.addtwo.Disable()
        else:
            if self.choosefileimagelist[pos][1] is not None:
                self.addtwo.SetBitmap(self.getBitmap(self.choosefileimagelist[pos][1], ''))
        if self.viewimglist[pos][2] == '':
            self.addthree.Disable()
        else:
            if self.choosefileimagelist[pos][2] is not None:
                self.addthree.SetBitmap(self.getBitmap(self.choosefileimagelist[pos][2], ''))
        if e is not None:
            e.Skip()
    def printingChangeBitmap(self,e,pos):
        # self.addone.SetBitmap(self.normalbitmap)
        # self.addone.Disable()
        self.selectbtnpos = pos
        self.addone.Enable()
        self.addtwo.Enable()
        self.addthree.Enable()
        self.addone.SetBitmap(self.underbitmap)
        self.addtwo.SetBitmap(self.underbitmap)
        self.addthree.SetBitmap(self.underbitmap)
        if self.viewimglist is None:
            self.viewimglist = self.getbinname(self._viewlist[13])
        if self.viewimglist[pos][0] == '':
            self.addone.Disable()
        else:
            if self.printingimagelist[pos][0] is not None:
                self.addone.SetBitmap(self.getBitmap(self.printingimagelist[pos][0], ''))
        if self.viewimglist[pos][1] == '':
            self.addtwo.Disable()
        else:
            if self.printingimagelist[pos][1] is not None:
                self.addtwo.SetBitmap(self.getBitmap(self.printingimagelist[pos][1], ''))
        if self.viewimglist[pos][2] == '':
            self.addthree.Disable()
        else:
            if self.printingimagelist[pos][2] is not None:
                self.addthree.SetBitmap(self.getBitmap(self.printingimagelist[pos][2], ''))
        if e is not None:
            e.Skip()

    def getStaticBmp(self,parent,bmp,func=None,rfun=None):

        width = int(float(self._picwidth))
        height = int(float(self._picheight))
        staticbitmap = wx.BitmapButton(parent, -1, bitmap=bmp, size=(width, height))
        if func is not None:
            staticbitmap.Bind(wx.EVT_BUTTON, func)
        if rfun is not None:
            staticbitmap.Bind(wx.EVT_RIGHT_UP,rfun)
        return staticbitmap

    def getWHBmp(self,parent,bmp,w,h,func=None,rfun=None):
        staticbitmap = wx.BitmapButton(parent, -1, bitmap=bmp, size=(w, h))
        if func is not None:
            staticbitmap.Bind(wx.EVT_BUTTON, func)
        if rfun is not None:
            staticbitmap.Bind(wx.EVT_RIGHT_UP,rfun)
        return staticbitmap

    def makeImage(self,filename,color,hasX):
        width = int(float(self._picwidth))
        height = int(float(self._picheight))
        image = Image.new('RGB', (width,height ), color)
        if hasX:
            draw = ImageDraw.Draw(image)
            draw.line((10,image.size[1]/2,image.size[0]-10,image.size[1]/2), fill=(255,255,255,255),width=3)
            draw.line((image.size[0]/2, 20, image.size[0]/2, image.size[1]-20), fill=(255,255,255,255),width=3)
        image.save(os.path.abspath('')+'\\'+filename,'png')

    def makeWHImage(self,filename,color,hasX,W,H):
        width = int(float(W))
        height = int(float(H))
        image = Image.new('RGB', (width,height ), color)
        if hasX:
            draw = ImageDraw.Draw(image)
            draw.line((10,image.size[1]/2,image.size[0]-10,image.size[1]/2), fill=(255,255,255,255),width=3)
            draw.line((image.size[0]/2, 20, image.size[0]/2, image.size[1]-20), fill=(255,255,255,255),width=3)
        image.save(os.path.abspath('')+'\\'+filename,'png')

    def comboboxsl(self,evt,widget):
        value = self._listview.GetString(self._listview.GetSelection())
        if self._listview.GetSelection() == 0:
            self.btlogo.Show()
            self.bottompanel.Hide()
            self.choosefilepanel.Hide()
            self.printingpanel.Hide()
        elif self._listview.GetSelection() == 12 and (self.viewcb.GetSelection() == 1):
            self.btlogo.Hide()
            self.bottompanel.Hide()
            self.choosefilepanel.Show()
            self.printingpanel.Hide()
        elif self._listview.GetSelection() == 13 and (self.viewcb.GetSelection() == 1):
            self.btlogo.Hide()
            self.bottompanel.Hide()
            self.choosefilepanel.Hide()
            self.printingpanel.Show()
        else:
            self.btlogo.Hide()
            self.choosefilepanel.Hide()
            self.bottompanel.Show()
            self.printingpanel.Hide()
        self._mainsizer.Layout()
        self.addsizer.Layout()
        self.addview.Layout()
        self._newmainsizer.Layout()
        self.viewimglist = self.getbinname(value)
        self.RefreshBitmap()
        evt.Skip()

    def pixelchange(self, evt, widget):
        if self.progressing:
            return
        value = self.viewcb.GetSelection()
        if len(self._pixellist) > value:
            self._picwidth = self._pixellist[value][2]
            self._picheight = self._pixellist[value][3]
            self.btlogo.SetSize((self._pixellist[value][0], self._pixellist[value][1]))
            for i in range(len(self.btnlist)):
                self.btnlist[i].SetSize((self._picwidth, self._picheight))
                self.btnlist[i].SetMinSize((self._picwidth, self._picheight))
                self.btnlist[i].SetMaxSize((self._picwidth, self._picheight))
            for i in range(len(self.choosefilebtnlist)):
                if i > 5:
                    self.choosefilebtnlist[i].SetSize((117, 92))
                    self.choosefilebtnlist[i].SetMinSize((117, 92))
                    self.choosefilebtnlist[i].SetMaxSize((117, 92))
                else:
                    self.choosefilebtnlist[i].SetSize((self._picwidth, self._picheight))
                    self.choosefilebtnlist[i].SetMinSize((self._picwidth, self._picheight))
                    self.choosefilebtnlist[i].SetMaxSize((self._picwidth, self._picheight))
            self.makeImage('bai.png', '#ffffff', False)
            self.makeImage('hei.png', '#000000', False)
            self.normalbitmap = wx.Image(os.path.abspath("") + "\\bai.png", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
            self.hnormalbitmap = wx.Image(os.path.abspath("") + "\\hei.png", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.btsizer.Layout()
        self.bbsizer.Layout()
        self.cfleftbotsizer.Layout()
        self.cflefttopsizer.Layout()
        self.cfleftsizer.Layout()
        self.cfrightsizer.Layout()
        self.cfsizer.Layout()
        self._mainsizer.Layout()
        self.addsizer.Layout()
        self.addview.Layout()
        self._newmainsizer.Layout()
        self.RefreshBitmap()
        # evt.Skip()

    def showConfigDialog(self, e):
        locale = wx.Locale(wx.LANGUAGE_ENGLISH)
        locale.AddCatalogLookupPathPrefix('locale')
        self.languagename = self.getLanguage()
        ibRet = locale.AddCatalog(self.languagename)
        self.widgetlist[:] = []
        if self._mdialog:
            self._mdialog.Hide()
        self._mdialog = wx.Dialog(self, -1, _(u'配置文件'), style=wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        self.isMax = False
        # self._mdialog.Bind(wx.EVT_SPLITTER_DOUBLECLICKED, self.OnDoubleClick())
        panel = wx.ScrolledWindow(self._mdialog, -1)
        panelsizer = wx.BoxSizer(wx.VERTICAL)
        totalheight = 1
        count = -1
        for mlist in self.configdt:
            ## 0标题 1选项 2类型 3导出名 4提示 5默认值
            tv = wx.StaticText(panel, -1, mlist[0])
            eachsizer = wx.BoxSizer(wx.HORIZONTAL)
            eachsizer.Add(tv, 1, wx.EXPAND)
            count += 1
            if mlist[2] == 'choose':
                indexi = 0
                for i in range(len(mlist[1])):
                    if str(mlist[1][i][:mlist[1][i].find(':')]) == str(mlist[5]):
                        indexi = i
                        break
                mwidget = wx.ComboBox(panel, -1, value=mlist[1][indexi], choices=mlist[1], style=wx.CB_READONLY)
                mwidget.SetName(mlist[3])
                mwidget.Bind(wx.EVT_COMBOBOX,lambda evt,widget=mwidget:self.cbchange(evt,widget))
                mwidget.SetToolTipString(mlist[0])
                totalheight = totalheight+mwidget.GetSize()[1]+6
                eachsizer.Add(mwidget, 1, wx.EXPAND)
                # self.widgetlist.append(mwidget)
            elif mlist[2] == 'edit':
                # for defaultvalue in mlist[5]:
                valida = MyNumberValidator(mlist[6], self, count)
                mwidget = wx.TextCtrl(panel, -1, validator=valida)
                mwidget.SetName(mlist[3])
                mwidget.SetLabelText(str(mlist[5]))
                if mlist[6] == 'type1':
                    tips = u':范围为-999~99999'
                elif mlist[6] == 'type2':
                    tips = u':范围为0~99999'
                else:
                    tips = u''
                mwidget.SetToolTipString(mlist[0] + tips)
                mwidget.Bind(wx.EVT_TEXT,lambda evt,widget=mwidget,vali=valida:self.edchange(evt,widget,vali))
                totalheight = totalheight + mwidget.GetSize()[1] + 6
                eachsizer.Add(mwidget, 1, wx.EXPAND)
                # self.widgetlist.append(mwidget)
            panelsizer.AddSizer(eachsizer, 0, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=3)
        panel.SetScrollbars(15, 15, 1000, totalheight)
        panel.SetSizer(panelsizer)
        btnyes = wx.Button(self._mdialog, -1, _(u'导出配置文件'))
        btnyes.Bind(wx.EVT_BUTTON, self.outputConfig)
        btnimport = wx.Button(self._mdialog, -1, _(u'导入配置文件'))
        btnimport.Bind(wx.EVT_BUTTON,self.importConfig)
        btnsizer = wx.BoxSizer(wx.HORIZONTAL)
        btnsizer.Add(btnyes, 1, wx.ALIGN_CENTER)
        btnsizer.Add(btnimport, 1, wx.ALIGN_CENTER)
        mdsizer = wx.BoxSizer(wx.VERTICAL)
        mdsizer.Add(panel, 1, wx.EXPAND)
        mdsizer.AddSizer(btnsizer, 0, wx.EXPAND)
        self._mdialog.SetSizer(mdsizer)
        self._mdialog.SetMinSize((580, 600))
        self._mdialog.SetSize((580,600))
        self._mdialog.Show()

    def cbchange(self, e, widget):
        for i in range(len(self.configdt)):
            if widget.GetName() == self.configdt[i][3]:
                self.configdt[i][5] = widget.GetStringSelection()[:widget.GetStringSelection().find(':')]
                break

    def edchange(self, e, widget, vali):
        for i in range(len(self.configdt)):
            if widget.GetName() == self.configdt[i][3]:
                self.configdt[i][5] = widget.GetValue()
                vali.value = self.configdt[i][5]
                break
    def getValue(self,id):
        print 'getValue'
        print self.configdt[id][5]
        return self.configdt[id][5]

    def outputConfig(self, e):
        filename = ""
        values = self.viewcbcopy.GetSelection()
        if values == 0:
            filename = "robin_config.txt"
        elif values == 1:
            filename = "robin_nano_cfg.txt"
        elif values == 2:
            filename = "robin_nano35_cfg.txt"
        elif values == 3:
            filename = "robin_nano35_cfg.txt"
        elif values == 4:
            filename = "robin_mini_config.txt"
        elif values == 5:
            filename = "robin2_cfg.txt"
        with wx.FileDialog(self, _(u"选择你的配置文件"),defaultDir=self.selectedpath,defaultFile=filename, wildcard="txt file (*.*)|*.*",
                           style=wx.SAVE) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            pathname = fileDialog.GetPath()
            configfile = open(pathname, 'w')
            for i in range(len(self.configdt)):
                configfile.write(str(self.configdt[i][3])+' ' +str(self.configdt[i][5])+ '    #' + self.configdt[i][4].encode(sys.getfilesystemencoding())+'\r\n')
            # for mlist in self.configdt:
            #     configfile.write(str(mlist[3])+' ' +str(mlist[5])+ '    #' + mlist[4].encode(sys.getfilesystemencoding())+'\r\n')
            configfile.close()
        self._mdialog.Hide()

    def importConfig(self, e):
        with wx.FileDialog(self, _(u"选择你的配置文件"),defaultDir=self.selectedpath, wildcard="txt file (*.*)|*.*",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            pathname = fileDialog.GetPath()
            configfile = open(pathname, 'r')
            configline = configfile.readline()
            while configline:
                for i in range(len(self.configdt)):
                    if self.configdt[i][3] in configline:
                        endpos = len(configline)
                        if configline.rfind("#") != -1:
                            endpos = configline.rfind('#')
                        self.configdt[i][5] = configline[configline.find(self.configdt[i][3])+len(self.configdt[i][3]):endpos].replace('\t', '').replace(' ', '')
                        break
                configline = configfile.readline()
            configfile.close()
        self.showConfigDialog(None)


    def exportbin(self,e):
        with wx.DirDialog(self, _(u"选择保存的文件夹"),style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dirDialog:

            if dirDialog.ShowModal() == wx.ID_CANCEL:
                return
            pathname = dirDialog.GetPath()
            # self.message.SetLabel(_(u'正在导出bin文件，请不要关闭'))
            self.progressthread = threading.Thread(target=lambda pn=pathname: self.progress(pn))
            self.progressthread.setDaemon(True)
            self.progressthread.start()
        e.Skip()

    def inputbin(self, e):
        with wx.DirDialog(self, _(u"选择导入的文件夹"),style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dirDialog:

            if dirDialog.ShowModal() == wx.ID_CANCEL:
                return
            pathname = dirDialog.GetPath()
            self.progressthread = threading.Thread(target=lambda pn=pathname: self.inprogress(pn))
            self.progressthread.setDaemon(True)
            self.progressthread.start()
        e.Skip()

    def inprogress(self, pathname):
        value = self.viewcb.GetSelection()
        locale = wx.Locale(wx.LANGUAGE_ENGLISH)
        locale.AddCatalogLookupPathPrefix('locale')
        self.languagename = self.getLanguage()
        ibRet = locale.AddCatalog(self.languagename)
        self.progressing = True
        try:
            filelist = os.listdir(pathname)
            temppos = self.viewpos
            temppath = sys.path[0] + "\\tempimg32\\"
            if value == 1:
                temppath = sys.path[0] + "\\tempimg35\\"
            elif value == 2:
                temppath = sys.path[0] + "\\tempimgdiy\\"
            else:
                temppath = sys.path[0] + "\\tempimg32\\"

            if os.path.exists(temppath):
                shutil.rmtree(temppath)
            os.mkdir(temppath)
            self.message.SetLabel(_(u'正在导入bin文件夹'))
            fid = 0
            for f in filelist:
                self.bin2image(pathname + "\\" + f, f[:-4])
                self.message.SetLabel(_(u'已导入:') + str(fid) + "/" + str(len(filelist)))
                fid = fid + 1
            self.message.SetLabel(_(u'正在加载图片'))
            for v in range(len(self._viewlist)):
                result = self.rgetbinname(self._viewlist[v])
                if v == 12 and value == 1:
                    self.choosefileimagelist = [[None, None, None], [None, None, None], [None, None, None], [None, None, None],[None, None, None], [None, None, None], [None, None, None], [None, None, None], [None, None, None]]
                    for r in range(len(result)):
                        if result[r][0] is not '' and os.path.exists(temppath + result[r][0].replace('.bin', '.png')):
                            self.choosefileimagelist[r][0] = temppath + result[r][0].replace('.bin', '.png')
                        if result[r][1] is not '' and os.path.exists(temppath + result[r][1].replace('.bin', '.png')):
                            self.choosefileimagelist[r][1] = temppath + result[r][1].replace('.bin', '.png')
                        if result[r][2] is not '' and os.path.exists(temppath + result[r][2].replace('.bin', '.png')):
                            self.choosefileimagelist[r][2] = temppath + result[r][2].replace('.bin', '.png')
                    self.allimglist35[v][:] = self.choosefileimagelist
                    self.choosefileimagelist[:] = self.allimglist35[self.viewpos]
                elif v == 13 and value == 1:
                    self.printingimagelist = [[None, None, None], [None, None, None], [None, None, None],[None, None, None]]
                    for r in range(len(result)):
                        if r < 4:
                            if result[r][0] is not '' and os.path.exists(temppath + result[r][0].replace('.bin', '.png')):
                                self.printingimagelist[r][0] = temppath + result[r][0].replace('.bin', '.png')
                            if result[r][1] is not '' and os.path.exists(temppath + result[r][1].replace('.bin', '.png')):
                                self.printingimagelist[r][1] = temppath + result[r][1].replace('.bin', '.png')
                            if result[r][2] is not '' and os.path.exists(temppath + result[r][2].replace('.bin', '.png')):
                                self.printingimagelist[r][2] = temppath + result[r][2].replace('.bin', '.png')
                    self.allimglist35[v][:] = self.printingimagelist
                    self.printingimagelist[:] = self.allimglist35[self.viewpos]
                else:
                    self.imagelist = [[None, None, None], [None, None, None], [None, None, None], [None, None, None],
                              [None, None, None], [None, None, None], [None, None, None], [None, None, None]]
                    for r in range(len(result)):
                        if result[r][0] is not '' and os.path.exists(temppath + result[r][0].replace('.bin', '.png')):
                            self.imagelist[r][0] = temppath + result[r][0].replace('.bin', '.png')
                        if result[r][1] is not '' and os.path.exists(temppath + result[r][1].replace('.bin', '.png')):
                            self.imagelist[r][1] = temppath + result[r][1].replace('.bin', '.png')
                        if result[r][2] is not '' and os.path.exists(temppath + result[r][2].replace('.bin', '.png')):
                            self.imagelist[r][2] = temppath + result[r][2].replace('.bin', '.png')
                    if value == 1:
                        self.allimglist35[v][:] = self.imagelist
                        self.imagelist[:] = self.allimglist35[self.viewpos]
                    elif value == 2:
                        self.allimglistdiy[v][:] = self.imagelist
                        self.imagelist[:] = self.allimglistdiy[self.viewpos]
                    else:
                        self.allimglist32[v][:] = self.imagelist
                        self.imagelist[:] = self.allimglist32[self.viewpos]

            self.viewpos = temppos
            self.RefreshBitmap()
            self.message.SetLabel(_(u'已完成导入'))
            self.progressing = False
        except Exception as e:
            self.progressing = False
    def progress(self,pathname):
        q = 0
        value = self.viewcb.GetSelection()
        if value == 1:
            for i in range(0, len(self.allimglist35)):
                if len(self.allimglist35[i]) > 0:
                    namelist = self.getbinname(self._viewlist[i])
                    for j in range(0, len(self.allimglist35[i])):
                        for k in range(0, len(self.allimglist35[i][j])):
                            if self.allimglist35[i][j][k] is not None:
                                q += 1
                                self.image2bin(Image.open(self.allimglist35[i][j][k]), pathname + '\\' + namelist[j][k])
                                self.message.SetLabel(_(u'已导出') + str(q) + _(u'个bin文件'))
        else:
            for i in range(0, len(self.allimglist32)):
                if len(self.allimglist32[i]) > 0:
                    namelist = self.getbinname(self._viewlist[i])
                    for j in range(0, len(self.allimglist32[i])):
                        for k in range(0, len(self.allimglist32[i][j])):
                            if self.allimglist32[i][j][k] is not None:
                                q += 1
                                self.image2bin(Image.open(self.allimglist32[i][j][k]), pathname + '\\' + namelist[j][k])
                                self.message.SetLabel(_(u'已导出') + str(q) + _(u'个bin文件'))

        self.message.SetLabel(_(u'已完成导出，可以关闭'))

    def rgetbinname(self, value):
        result = []
        # 0_(u'准备打印'), 1_(u'预热'), 2_(u'挤出'), 3_(u'移动'), 4_(u'回零'), 5_(u'调平'), 6_(u'设置'), 7_(u'风扇'),
        # 8_(u'换料'),9 _(u'文件系统'), 10_(u'更多'), 11_(u'选择文件'), 12_(u'正在打印'), 13_(u'操作'), 14_(u'暂停'), 15_(u'变速'), 16_(u'更多（打印中）'),17_(u'语言')
        # 18_(u'WIFI')
        if value == self._viewlist[0]:
            self.viewpos = 0
            result = [['bmp_logo.bin', '', ''], ['', '', ''], ['', '', ''],
                      ['', '', '']
                , ['', '', ''], ['', '', ''],
                      ['', '', ''], ['', '', '']]
        elif value == self._viewlist[1]:
            self.viewpos = 1
            result = [['bmp_preHeat.bin', '', ''], ['bmp_mov.bin', '', ''], ['bmp_zero.bin', '', ''],
                      ['bmp_printing.bin', '', '']
                , ['bmp_extruct.bin', '', ''], ['bmp_leveling.bin', 'bmp_autoleveling.bin', ''],
                      ['bmp_set.bin', '', ''], ['bmp_more.bin', '', '']]
        elif value == self._viewlist[2]:
            self.viewpos = 2
            result = [['bmp_Add.bin', '', ''], ['', '', ''], ['', '', ''], ['bmp_Dec.bin', '', ''],
                      ['bmp_bed.bin', 'bmp_extru1.bin', 'bmp_extru2.bin']
                , ['bmp_step1_degree.bin', 'bmp_step5_degree.bin', 'bmp_step10_degree.bin'], ['bmp_speed0.bin', '', ''],
                      ['bmp_return.bin', '', '']]
        elif value == self._viewlist[3]:
            self.viewpos = 3
            result = [['bmp_in.bin', '', ''], ['', '', ''], ['', '', ''], ['bmp_out.bin', '', ''],
                      ['bmp_extru1.bin', 'bmp_extru2.bin', '']
                , ['bmp_step1_mm.bin', 'bmp_step5_mm.bin', 'bmp_step10_mm.bin'],
                      ['bmp_speed_slow.bin', 'bmp_speed_normal.bin', 'bmp_speed_high.bin'], ['bmp_return.bin', '', '']]
        elif value == self._viewlist[4]:
            self.viewpos = 4
            result = [['bmp_xAdd.bin', '', ''], ['bmp_yAdd.bin', '', ''], ['bmp_zAdd.bin', '', ''],
                      ['bmp_step_move0_1.bin', 'bmp_step_move1.bin', 'bmp_step_move10.bin'], ['bmp_xDec.bin', '', ''],
                      ['bmp_yDec.bin', '', ''], ['bmp_zDec.bin', '', ''], ['bmp_return.bin', '', '']]
        elif value == self._viewlist[5]:
            self.viewpos = 5
            result = [['bmp_zeroA.bin', '', ''], ['bmp_zeroX.bin', '', ''], ['bmp_zeroY.bin', '', ''],
                      ['bmp_zeroZ.bin', '', ''], ['', '', ''], ['', '', ''], ['', '', ''], ['bmp_return.bin', '', '']]
        elif value == self._viewlist[6]:
            self.viewpos = 6
            result = [['bmp_leveling1.bin', '', ''], ['bmp_leveling2.bin', '', ''], ['bmp_leveling3.bin', '', ''],
                      ['bmp_leveling4.bin', '', '']
                , ['bmp_leveling5.bin', '', ''], ['', '', ''], ['', '', ''], ['bmp_return.bin', '', '']]
        elif value == self._viewlist[7]:
            self.viewpos = 7
            result = [['bmp_wifi.bin ', '', ''], ['bmp_fan.bin', '', ''], ['bmp_about.bin  ', '', ''],
                      ['bmp_filamentchange.bin', '', '']
                , ['bmp_breakpoint.bin', '', ''], ['bmp_function1.bin', '', ''], ['bmp_language.bin', '', ''],
                      ['bmp_return.bin', '', '']]
        elif value == self._viewlist[8]:
            self.viewpos = 8
            result = [['bmp_Add.bin', '', ''], ['', '', ''], ['', '', ''], ['bmp_Dec.bin', '', ''],
                      ['bmp_speed255.bin', '', '']
                , ['bmp_speed127.bin', '', ''], ['bmp_speed0.bin', '', ''], ['bmp_return.bin', '', '']]
        elif value == self._viewlist[9]:
            self.viewpos = 9
            result = [['bmp_in.bin', '', ''], ['', '', ''], ['', '', ''], ['bmp_out.bin', '', ''],
                      ['bmp_extru1.bin', 'bmp_extru2.bin', '']
                , ['', '', ''],
                      ['', '', ''], ['bmp_return.bin', '', '']]
        elif value == self._viewlist[10]:
            self.viewpos = 10
            result = [['bmp_sd.bin', 'bmp_sd_sel.bin', ''], ['bmp_usb.bin', 'bmp_usb_sel.bin', ''], ['', '', ''],
                      ['', '', ''], ['', '', ''], ['', '', ''], ['', '', ''], ['bmp_return.bin', '', '']]
        elif value == self._viewlist[11]:
            self.viewpos = 11
            result = [['bmp_custom1.bin', '', ''], ['bmp_custom2.bin', '', ''], ['bmp_custom3.bin', '', ''],
                      ['bmp_custom4.bin', '', '']
                , ['bmp_custom5.bin', '', ''], ['bmp_custom6.bin', '', ''], ['bmp_custom7.bin', '', ''],
                      ['bmp_return.bin', '', '']]
        elif value == self._viewlist[12]:
            self.viewpos = 12
            if self.viewcb.GetSelection() == 1:
                result = [['bmp_file.bin', 'bmp_dir.bin', ''], ['', '', ''], ['', '', ''], ['', '', ''], ['', '', ''], ['', '', ''],
                          ['bmp_pageUp.bin', '', ''], ['bmp_pageDown.bin', '', ''], ['bmp_back.bin', '', '']]
            else:
                result = [['bmp_file.bin', 'bmp_dir.bin', ''], ['', '', ''], ['', '', ''], ['', '', ''], ['', '', ''],
                          ['bmp_pageUp.bin', '', ''], ['bmp_pageDown.bin', '', ''], ['bmp_return.bin', '', '']]
        elif value == self._viewlist[13]:
            self.viewpos = 13
            if self.viewcb.GetSelection() == 1:
                result = [['bmp_preview.bin', '', ''], ['bmp_pause.bin', 'bmp_resume.bin', ''],['bmp_stop.bin', '', ''], ['bmp_operate.bin', 'bmp_printing_back.bin', '']]
            else:
                result = [['', '', ''], ['', '', ''], ['', '', ''], ['bmp_menu.bin', '', ''],
                      ['bmp_extru1_no_words.bin', '', ''], ['bmp_extru2_no_words.bin', '', '']
                , ['bmp_bed_no_words.bin', '', ''], ['bmp_fan_no_words.bin', 'bmp_fan_move.bin', '']]
        elif value == self._viewlist[14]:
            self.viewpos = 14
            result = [['bmp_pause.bin', '', ''], ['', '', ''], ['', '', ''], ['bmp_stop.bin', '', ''],
                      ['bmp_temp.bin', '', '']
                , ['bmp_speed.bin', '', ''], ['bmp_more.bin', '', ''], ['bmp_return.bin', '', '']]
        elif value == self._viewlist[15]:
            self.viewpos = 15
            result = [['bmp_resume.bin', '', ''], ['', '', ''], ['', '', ''], ['bmp_stop.bin', '', ''],
                      ['bmp_extruct.bin', '', '']
                , ['bmp_mov.bin', '', ''], ['bmp_temp.bin', '', ''], ['bmp_more.bin', '', '']]
        elif value == self._viewlist[16]:
            self.viewpos = 16
            result = [['bmp_Add.bin', '', ''], ['', '', ''], ['', '', ''], ['bmp_Dec.bin', '', ''],
                      ['bmp_mov.bin', 'bmp_mov_sel.bin', ''], ['bmp_extruct.bin', 'bmp_extruct_sel.bin', '']
                , ['bmp_step1_mm.bin', 'bmp_step5_mm.bin', 'bmp_step10_mm.bin'], ['bmp_return.bin', '', '']]
        elif value == self._viewlist[17]:
            self.viewpos = 17
            result = [['bmp_fan.bin', '', ''], ['bmp_filamentchange.bin', '', ''],
                      ['bmp_auto_off.bin', 'bmp_manual_off.bin', ''], ['bmp_morefunc1.bin', '', '']
                , ['bmp_morefunc2.bin', '', ''], ['bmp_morefunc3.bin', '', ''], ['bmp_morefunc4.bin', '', ''],
                      ['bmp_return.bin', '', '']]
        elif value == self._viewlist[18]:
            self.viewpos = 18
            result = [['bmp_simplified_cn.bin', 'bmp_simplified_cn_sel.bin', ''],
                      ['bmp_traditional_cn.bin', 'bmp_traditional_cn_sel.bin', ''],
                      ['bmp_english.bin', 'bmp_english_sel.bin', ''],
                      ['bmp_russian.bin', 'bmp_russian_sel.bin', ''], ['bmp_spanish.bin', 'bmp_spanish_sel.bin', ''],
                      ['bmp_french.bin', 'bmp_french_sel.bin', ''],
                      ['bmp_italy.bin', 'bmp_italy_sel.bin', ''], ['bmp_return.bin', '', '']]
        elif value == self._viewlist[19]:
            self.viewpos = 19
            result = [['', '', ''], ['', '', ''], ['', '', ''],
                      ['', '', ''], ['', '', ''], ['', '', ''], ['bmp_cloud.bin', '', ''], ['bmp_return.bin', '', '']]
        value = self.viewcb.GetSelection()
        if value == 1:
            if len(self.allimglist35[self.viewpos]) == 0:
                if self.viewpos == 12 and value == 1:
                    self.choosefileimagelist = [[None, None, None], [None, None, None], [None, None, None],
                                                [None, None, None], [None, None, None], [None, None, None],
                                                [None, None, None], [None, None, None], [None, None, None]]
                    self.allimglist35[self.viewpos][:] = self.choosefileimagelist
                elif self.viewpos == 13 and value == 1:
                    self.printingimagelist = [[None, None, None], [None, None, None], [None, None, None],
                                              [None, None, None]]
                    self.allimglist35[self.viewpos][:] = self.printingimagelist
                else:
                    self.imagelist = [[None, None, None], [None, None, None], [None, None, None], [None, None, None],
                                      [None, None, None], [None, None, None], [None, None, None], [None, None, None]]
                    self.allimglist35[self.viewpos][:] = self.imagelist

            else:
                if self.viewpos == 12 and value == 1:
                    self.choosefileimagelist = self.allimglist35[self.viewpos]
                elif self.viewpos == 13 and value == 1:
                    self.printingimagelist = self.allimglist35[self.viewpos]
                else:
                    self.imagelist = self.allimglist35[self.viewpos]
        else:
            if len(self.allimglist32[self.viewpos]) == 0:
                if self.viewpos == 12 and value == 1:
                    self.choosefileimagelist = [[None, None, None], [None, None, None], [None, None, None],[None, None, None],[None, None, None], [None, None, None], [None, None, None],[None, None, None],[None, None, None]]
                    self.allimglist32[self.viewpos][:] = self.choosefileimagelist
                elif self.viewpos == 13 and value == 1:
                    self.printingimagelist = [[None, None, None],[None, None, None],[None, None, None],[None, None, None]]
                    self.allimglist32[self.viewpos][:] = self.printingimagelist
                else:
                    self.imagelist = [[None, None, None], [None, None, None], [None, None, None], [None, None, None], [None, None, None], [None, None, None], [None, None, None], [None, None, None]]
                    self.allimglist32[self.viewpos][:] = self.imagelist

            else:
                if self.viewpos == 12 and value == 1:
                    self.choosefileimagelist = self.allimglist32[self.viewpos]
                elif self.viewpos == 13 and value == 1:
                    self.printingimagelist = self.allimglist32[self.viewpos]
                else:
                    self.imagelist = self.allimglist32[self.viewpos]
        return result

    def getbinname(self,value):
        result = []
        # 0_(u'准备打印'), 1_(u'预热'), 2_(u'挤出'), 3_(u'移动'), 4_(u'回零'), 5_(u'调平'), 6_(u'设置'), 7_(u'风扇'),
        # 8_(u'换料'),9 _(u'文件系统'), 10_(u'更多'), 11_(u'选择文件'), 12_(u'正在打印'), 13_(u'操作'), 14_(u'暂停'), 15_(u'变速'), 16_(u'更多（打印中）'),17_(u'语言')
        #18_(u'WIFI')
        if value == self._viewlist[0]:
            self.viewpos = 0
            result = [['bmp_logo.bin', '', ''], ['', '', ''], ['', '', ''],
                      ['', '', '']
                , ['', '', ''], ['', '', ''],
                      ['', '', ''], ['', '', '']]
        elif value == self._viewlist[1]:
            self.viewpos = 1
            result = [['bmp_preHeat.bin', '', ''], ['bmp_mov.bin', '', ''], ['bmp_zero.bin', '', ''],
                      ['bmp_printing.bin', '', '']
                , ['bmp_extruct.bin', '', ''], ['bmp_leveling.bin', 'bmp_autoleveling.bin', ''],
                      ['bmp_set.bin', '', ''], ['bmp_more.bin', '', '']]
        elif value == self._viewlist[2]:
            self.viewpos = 2
            result = [['bmp_Add.bin', '', ''], ['', '', ''], ['', '', ''], ['bmp_Dec.bin', '', ''],
                      ['bmp_bed.bin', 'bmp_extru1.bin', 'bmp_extru2.bin']
                , ['bmp_step1_degree.bin', 'bmp_step5_degree.bin', 'bmp_step10_degree.bin'], ['bmp_speed0.bin', '', ''],
                      ['bmp_return.bin', '', '']]
        elif value == self._viewlist[3]:
            self.viewpos = 3
            result = [['bmp_in.bin', '', ''], ['', '', ''], ['', '', ''], ['bmp_out.bin', '', ''],
                      ['bmp_extru1.bin', 'bmp_extru2.bin', '']
                , ['bmp_step1_mm.bin', 'bmp_step5_mm.bin', 'bmp_step10_mm.bin'],
                      ['bmp_speed_slow.bin', 'bmp_speed_normal.bin', 'bmp_speed_high.bin'], ['bmp_return.bin', '', '']]
        elif value == self._viewlist[4]:
            self.viewpos = 4
            result = [['bmp_xAdd.bin', '', ''], ['bmp_yAdd.bin', '', ''], ['bmp_zAdd.bin', '', ''],
                      ['bmp_step_move0_1.bin', 'bmp_step_move1.bin', 'bmp_step_move10.bin'], ['bmp_xDec.bin', '', ''],
                      ['bmp_yDec.bin', '', ''], ['bmp_zDec.bin', '', ''], ['bmp_return.bin', '', '']]
        elif value == self._viewlist[5]:
            self.viewpos = 5
            result = [['bmp_zeroA.bin', '', ''], ['bmp_zeroX.bin', '', ''], ['bmp_zeroY.bin', '', ''],
                      ['bmp_zeroZ.bin', '', ''], ['', '', ''], ['', '', ''], ['', '', ''], ['bmp_return.bin', '', '']]
        elif value == self._viewlist[6]:
            self.viewpos = 6
            result = [['bmp_leveling1.bin', '', ''], ['bmp_leveling2.bin', '', ''], ['bmp_leveling3.bin', '', ''],
                      ['bmp_leveling4.bin', '', '']
                , ['bmp_leveling5.bin', '', ''], ['', '', ''], ['', '', ''], ['bmp_return.bin', '', '']]
        elif value == self._viewlist[7]:
            self.viewpos = 7
            result = [['bmp_wifi.bin ', '', ''], ['bmp_fan.bin', '', ''], ['bmp_about.bin  ', '', ''],
                      ['bmp_filamentchange.bin', '', '']
                , ['bmp_breakpoint.bin', '', ''], ['bmp_function.bin', '', ''], ['bmp_language.bin', '', ''],
                      ['bmp_return.bin', '', '']]
        elif value == self._viewlist[8]:
            self.viewpos = 8
            result = [['bmp_Add.bin', '', ''], ['', '', ''], ['', '', ''], ['bmp_Dec.bin', '', ''],
                      ['bmp_speed255.bin', '', '']
                , ['bmp_speed127.bin', '', ''], ['bmp_speed0.bin', '', ''], ['bmp_return.bin', '', '']]
        elif value == self._viewlist[9]:
            self.viewpos = 9
            result = [['bmp_in.bin', '', ''], ['', '', ''], ['', '', ''], ['bmp_out.bin', '', ''],
                      ['bmp_extru1.bin', 'bmp_extru2.bin', '']
                , ['', '', ''],
                      ['', '', ''], ['bmp_return.bin', '', '']]
        elif value == self._viewlist[10]:
            self.viewpos = 10
            result = [['bmp_sd.bin', 'bmp_sd_sel.bin', ''], ['bmp_usb.bin', 'bmp_usb_sel.bin', ''], ['', '', ''],
                      ['', '', ''], ['', '', ''], ['', '', ''], ['', '', ''], ['bmp_return.bin', '', '']]
        elif value == self._viewlist[11]:
            self.viewpos = 11
            result = [['bmp_custom1.bin', '', ''], ['bmp_custom2.bin', '', ''], ['bmp_custom3.bin', '', ''],
                      ['bmp_custom4.bin', '', '']
                , ['bmp_custom5.bin', '', ''], ['bmp_custom6.bin', '', ''], ['bmp_custom7.bin', '', ''],
                      ['bmp_return.bin', '', '']]
        elif value == self._viewlist[12]:
            self.viewpos = 12
            if self.viewcb.GetSelection() == 1:
                result = [['bmp_file.bin', 'bmp_dir.bin', ''], ['', '', ''], ['', '', ''], ['', '', ''], ['', '', ''],
                          ['', '', ''], ['bmp_pageUp.bin', '', ''], ['bmp_pageDown.bin', '', ''], ['bmp_back.bin', '', '']]
            else:
                result = [['bmp_file.bin', 'bmp_dir.bin', ''], ['', '', ''], ['', '', ''], ['', '', ''], ['', '', ''],
                      ['bmp_pageUp.bin', '', ''], ['bmp_pageDown.bin', '', ''], ['bmp_return.bin', '', '']]
        elif value == self._viewlist[13]:
            self.viewpos = 13
            if self.viewcb.GetSelection() == 1:
                result = [['bmp_preview.bin', '', ''], ['bmp_pause.bin', 'bmp_resume.bin', ''], ['bmp_stop.bin', '', ''], ['bmp_operate.bin', 'bmp_printing_back.bin', '']]
            else:
                result = [['', '', ''], ['', '', ''], ['', '', ''], ['bmp_menu.bin', '', ''],
                      ['bmp_extru1_no_words.bin', '', ''], ['bmp_extru2_no_words.bin', '', '']
                , ['bmp_bed_no_words.bin', '', ''], ['bmp_fan_no_words.bin', 'bmp_fan_move.bin', '']]
        elif value == self._viewlist[14]:
            self.viewpos = 14
            result = [['bmp_pause.bin', '', ''], ['', '', ''], ['', '', ''], ['bmp_stop.bin', '', ''],
                      ['bmp_temp.bin', '', '']
                , ['bmp_speed.bin', '', ''], ['bmp_more.bin', '', ''], ['bmp_return.bin', '', '']]
        elif value == self._viewlist[15]:
            self.viewpos = 15
            result = [['bmp_resume.bin', '', ''], ['', '', ''], ['', '', ''], ['bmp_stop.bin', '', ''],
                      ['bmp_extruct.bin', '', '']
                , ['bmp_mov.bin', '', ''], ['bmp_temp.bin', '', ''], ['bmp_more.bin', '', '']]
        elif value == self._viewlist[16]:
            self.viewpos = 16
            result = [['bmp_Add.bin', '', ''], ['', '', ''], ['', '', ''], ['bmp_Dec.bin', '', ''],
                      ['bmp_mov.bin', 'bmp_mov_sel.bin', ''], ['bmp_extruct.bin', 'bmp_extruct_sel.bin', '']
                , ['bmp_step1_mm.bin', 'bmp_step5_mm.bin', 'bmp_step10_mm.bin'], ['bmp_return.bin', '', '']]
        elif value == self._viewlist[17]:
            self.viewpos = 17
            result = [['bmp_fan.bin', '', ''], ['bmp_filamentchange.bin', '', ''],
                      ['bmp_auto_off.bin', 'bmp_manual_off.bin', ''], ['bmp_morefunc1.bin', '', '']
                , ['bmp_morefunc2.bin', '', ''], ['bmp_morefunc3.bin', '', ''], ['bmp_morefunc4.bin', '', ''],
                      ['bmp_return.bin', '', '']]
        elif value == self._viewlist[18]:
            self.viewpos = 18
            result = [['bmp_simplified_cn.bin', 'bmp_simplified_cn_sel.bin', ''],
                      ['bmp_traditional_cn.bin', 'bmp_traditional_cn_sel.bin', ''],
                      ['bmp_english.bin', 'bmp_english_sel.bin', ''],
                      ['bmp_russian.bin', 'bmp_russian_sel.bin', ''], ['bmp_spanish.bin', 'bmp_spanish_sel.bin', ''],
                      ['bmp_french.bin', 'bmp_french_sel.bin', ''],
                      ['bmp_italy.bin', 'bmp_italy_sel.bin', ''], ['bmp_return.bin', '', '']]
        elif value == self._viewlist[19]:
            self.viewpos = 19
            result = [['', '', ''], ['', '', ''], ['', '', ''],
                      ['', '', ''], ['', '', ''], ['', '', ''], ['bmp_cloud.bin', '', ''], ['bmp_return.bin', '', '']]
        value = self.viewcb.GetSelection()
        if value == 1:
            if len(self.allimglist35[self.viewpos]) == 0:
                if self.viewpos == 12 and (value == 1):
                    self.choosefileimagelist = [[None, None, None], [None, None, None], [None, None, None],
                                                [None, None, None], [None, None, None], [None, None, None],
                                                [None, None, None], [None, None, None], [None, None, None]]
                    self.allimglist35[self.viewpos][:] = self.choosefileimagelist
                elif self.viewpos == 13 and (value == 1):
                    self.printingimagelist = [[None, None, None], [None, None, None], [None, None, None],
                                              [None, None, None]]
                    self.allimglist35[self.viewpos][:] = self.printingimagelist
                else:
                    self.imagelist = [[None, None, None], [None, None, None], [None, None, None], [None, None, None],
                                      [None, None, None], [None, None, None], [None, None, None], [None, None, None]]
                    self.allimglist35[self.viewpos][:] = self.imagelist
            else:
                if self.viewpos == 12 and value == 1:
                    self.choosefileimagelist = self.allimglist35[self.viewpos]
                elif self.viewpos == 13 and value == 1:
                    self.printingimagelist = self.allimglist35[self.viewpos]
                else:
                    self.imagelist = self.allimglist35[self.viewpos]
        else:
            if len(self.allimglist32[self.viewpos]) == 0:
                if self.viewpos == 12 and value == 1:
                    self.choosefileimagelist = [[None, None, None], [None, None, None], [None, None, None], [None, None, None], [None, None, None], [None, None, None], [None, None, None], [None, None, None], [None, None, None]]
                    self.allimglist32[self.viewpos][:] = self.choosefileimagelist
                elif self.viewpos == 13 and value == 1:
                    self.printingimagelist = [[None, None, None], [None, None, None], [None, None, None], [None, None, None]]
                    self.allimglist32[self.viewpos][:] = self.printingimagelist
                else:
                    self.imagelist = [[None, None, None], [None, None, None], [None, None, None], [None, None, None],[None, None, None], [None, None, None], [None, None, None], [None, None, None]]
                    self.allimglist32[self.viewpos][:] = self.imagelist
            else:
                if self.viewpos == 12 and value == 1:
                    self.choosefileimagelist = self.allimglist32[self.viewpos]
                elif self.viewpos == 13 and value == 1:
                    self.printingimagelist = self.allimglist32[self.viewpos]
                else:
                    self.imagelist = self.allimglist32[self.viewpos]
        self.addone.SetBitmap(self.underbitmap)
        self.addtwo.SetBitmap(self.underbitmap)
        self.addthree.SetBitmap(self.underbitmap)
        return result

    def gettextlist(self):
        locale = wx.Locale(wx.LANGUAGE_ENGLISH)
        locale.AddCatalogLookupPathPrefix('locale')
        self.languagename = self.getLanguage()
        ibRet = locale.AddCatalog(self.languagename)
        if self.viewpos == 0:
            return ['', '', '', '', '', '', '', '']
        elif self.viewpos == 1:
            return [_(u'预热'), _(u'移动'), _(u'回零'), _(u'打印'), _(u'挤出'), _(u'调平'), _(u'设置'), _(u'更多')]
        elif self.viewpos == 2:
            return [_(u'增加'), _(u''), _(u''), _(u'减少'), _(u'热床'), _(u'1℃'), _(u'关闭'), _(u'返回')]
        elif self.viewpos == 3:
            return [_(u'进料'), _(u''), _(u''), _(u'退料'), _(u'喷头1'), _(u'5mm'), _(u'低速'), _(u'返回')]
        elif self.viewpos == 4:
            return [_(u'X+'), _(u'Y+'), _(u'Z+'), _(u'1mm'), _(u'X-'), _(u'Y-'), _(u'Z-'), _(u'返回')]
        elif self.viewpos == 5:
            return [_(u'All'), _(u'X'), _(u'Y'), _(u'Z'), _(u''), _(u''), _(u''), _(u'返回')]
        elif self.viewpos == 6:
            return [_(u'第一点'), _(u'第二点'), _(u'第三点'), _(u'第四点'), _(u'第五点'), _(u''), _(u''), _(u'返回')]
        elif self.viewpos == 7:
            return [_(u'Wifi'), _(u'风扇'), _(u'关于'), _(u'换料'), _(u'断点续打'), _(u'关闭电机'), _(u'语言'), _(u'返回')]
        elif self.viewpos == 8:
            return [_(u'增加'), _(u''), _(u''), _(u'减少'), _(u'100%'), _(u'50%'), _(u'0%'), _(u'返回')]
        elif self.viewpos == 9:
            return [_(u'进料'), _(u''), _(u''), _(u'退料'), _(u'喷头1'), _(u'预热'), _(u'停止'), _(u'返回')]
        elif self.viewpos == 10:
            return [_(u'SD'), _(u'USB'), _(u''), _(u''), _(u''), _(u''), _(u''), _(u'返回')]
        elif self.viewpos == 11:
            return [_(u'更多1'), _(u'更多2'), _(u'更多3'), _(u'更多4'), _(u'更多5'), _(u'更多6'), _(u'更多7'), _(u'返回')]
        elif self.viewpos == 12:
            if self.viewcb.GetSelection() == 1:
                return [_(u'MKS.gcode'), _(u''), _(u''), _(u''), _(u''), _(u''), _(u'test.g'), _(u'test.g'), _(u'test.g')]
            else:
                return [_(u'test.g'), _(u''), _(u''), _(u''), _(u''), _(u''), _(u''), _(u'返回')]
        elif self.viewpos == 13:
            if self.viewcb.GetSelection() == 1:
                return [_(u''), _(u'test.g'), _(u'test.g'), _(u'test.g')]
            else:
                return [_(u''), _(u''), _(u''), _(u'操作'), _(u'200/200'), _(u'200/200'), _(u'60/60'), _(u'255')]
        elif self.viewpos == 14:
            return [_(u'暂停'), _(u''), _(u''), _(u'停止'), _(u'温度'), _(u'换料'), _(u'更多'), _(u'返回')]
        elif self.viewpos == 15:
            return [_(u'恢复'), _(u''), _(u''), _(u'停止'), _(u'挤出'), _(u'移动'), _(u'换料'), _(u'更多')]
        elif self.viewpos == 16:
            return [_(u'增加'), _(u''), _(u''), _(u'减少'), _(u'移动'), _(u'挤出'), _(u'5%'), _(u'返回')]
        elif self.viewpos == 17:
            return [_(u'风扇'), _(u'换料'), _(u'自动关机'), _(u'更多1'), _(u'更多2'), _(u'更多3'), _(u'更多4'), _(u'返回')]
        elif self.viewpos == 18:
            return [_(u'简体'), _(u'繁体'), _(u'英语'), _(u'俄语'), _(u'西班牙语'), _(u'法语'), _(u'意大利语'), _(u'返回')]
        elif self.viewpos == 19:
            return [_(u''), _(u''), _(u''), _(u''), _(u''), _(u''), _(u'云服务'), _(u'返回')]
        else:
            return ['', '', '', '', '', '', '', '']

    def image2bin(self,image,binfile):
        f = open(binfile, 'wb')
        pixs = image.load()
        for y in range(image.size[1]):
            for x in range(image.size[0]):
                R = pixs[x, y][0] >> 3
                G = pixs[x, y][1] >> 2
                B = pixs[x, y][2] >> 3
                rgb = (R << 11) | (G << 5) | B
                strHex = "%x" % rgb
                if len(strHex) == 3:
                    strHex = '0' + strHex[0:3]
                elif len(strHex) == 2:
                    strHex = '00' + strHex[0:2]
                elif len(strHex) == 1:
                    strHex = '000' + strHex[0:1]
                if strHex[2:4] != '':
                    f.write(pack('B', int(strHex[2:4], 16)))
                if strHex[0:2] != '':
                    f.write(pack('B', int(strHex[0:2], 16)))
        f.close()

    def bin2image(self, binfile, outname):
        value = self.viewcb.GetSelection()
        temppath = sys.path[0] + "\\tempimg32\\" + outname + ".png"
        if value == 1:
            temppath = sys.path[0] + "\\tempimg35\\" + outname + ".png"
        else:
            temppath = sys.path[0]+"\\tempimg32\\"+outname+".png"
        f = open(binfile, "rb")
        content = f.read()
        x=0
        y=0
        picwidth = self._picwidth
        picheight = self._picheight
        if outname == "bmp_logo":
            picwidth = 320
            picheight = 240
            value = self.viewcb.GetSelection()
            if value == 1:
                picwidth = 480
                picheight = 320
        elif outname == "bmp_preview":
            picwidth = 200
            picheight = 200
        elif outname == "bmp_pause" or outname == "bmp_stop":
            picwidth = 200
            picheight = 200
            value = self.viewcb.GetSelection()
            if value == 1:
                picwidth = 150
                picheight = 80
        elif len(content)/2 < picwidth*picheight:
            picwidth = 150
            picheight = 80
            if len(content)/2 <picwidth*picheight:
                picwidth = 117
                picheight = 92
                if len(content)/2 < picwidth*picheight:
                    picwidth = 100
                    picheight = 100
                    if len(content)/2 < picwidth*picheight:
                        return
        image = Image.new('RGB', (picwidth, picheight))
        for i in range(0, len(content), 2):
            two = "%x" % ord(content[i])
            one = "%x" % ord(content[i + 1])
            rg = bin(int(one, 16)).replace('0b', '')
            gb = bin(int(two, 16)).replace('0b', '')
            while len(rg) < 8:
                rg = '0' + rg
            while len(gb) < 8:
                gb = '0' + gb
            r = int(rg[0:5] + '000', 2)
            g = int(rg[5:8] + gb[0:3] + '00', 2)
            b = int(gb[3:8] + '000', 2)
            image.putpixel((x, y), (r, g, b))
            x = x+1
            if x >= picwidth:
                y = y+1
                x = 0
            if y >= picheight:
                break
        if outname == 'filamentchange':
            print(image.size())
        image.save(temppath, 'png')

class DIYFrame(wx.Frame):
    def __init__(self):
        super(DIYFrame, self).__init__(None, title=u"MKSTOOL")
        self.icon = wx.Icon('mkstool.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.icon)
        locale = wx.Locale(wx.LANGUAGE_ENGLISH)
        locale.AddCatalogLookupPathPrefix('locale')
        self.languagename = self.getLanguage()
        ibRet = locale.AddCatalog(self.languagename)
        self._viewlist = [_(u'开机logo'),_(u'工具'),_(u'预热'),_(u'挤出'),_(u'移动'),_(u'回零'),_(u'调平'),_(u'设置'),_(u'风扇'),
                          _(u'换料'),_(u'更多'),_(u'选择文件'),_(u'正在打印'),_(u'操作'),_(u'暂停'),_(u'变速'),_(u'更多（打印中）'),_(u'语言'),_(u'WIFI'),_(u'准备打印'),_(u'机器参数')]
        self.selectedviewpos = 0
        self._typelist = ["MKS Robin-TFT24/28/32", "MKS Robin Nano-TFT24/28/32", "MKS Robin Nano-TFT35", "MKS Robin Nano-TFT35-DIY-IAR", "MKS Robin Mini-TFT24/28/32", "MKS Robin2-TFT35"]
        self._pixellist = [[480, 320, 117, 140]]
        self.languagelist = [u'中文', u'English']
        self.imagelist = [[None,None,None],[None,None,None],[None,None,None],[None,None,None],[None,None,None],[None,None,None],[None,None,None],[None,None,None]]
        self.choosefileimagelist = [[None, None, None], [None, None, None], [None, None, None], [None, None, None], [None, None, None],[None, None, None], [None, None, None], [None, None, None], [None, None, None]]
        self.printingimagelist = [[None, None, None], [None, None, None], [None, None, None], [None, None, None]]
        self.allimglistdiy = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
        # 标题 选项 类型 导出名 提示 默认值 校验器
        self.configdt = [[_(u'屏幕首页显示模式'), [_(u'0:经典模式'),_(u'1:简约模式')], 'choose', '>cfg_screen_display_mode', _(u'屏幕首页显示模式'), 0, ''],
                         [_(u'屏幕翻转180度'), [_(u'0x00:不翻转'), _(u'0xEE:翻转')], 'choose', '>cfg_screen_overturn_180 0x00', _(u'屏幕翻转180度'), 0, ''],
                         [_(u'语言切换方式'), [_(u'0:配置文件选项切换语言'),_(u'1:屏幕按钮切换语言')], 'choose', '>cfg_language_adjust_type', _(u'语言切换方式'), 1, ''],
                         [_(u'语言'), [_(u'1:简体中文'), _(u'2:繁体中文'), _(u'3:英文'), _(u'4:俄语'), _(u'5:西班牙语'), _(u'6:法语'), _(u'7:意大利语')], 'choose', '>cfg_language_type', _(u'语言'), 2, ''],
                         [_(u'机型设置'), [_(u'0:Cartesian'), _(u'1:DELTA'), _(u'2:COREXY')], 'choose', '>MACHINETPYE',_(u'机型设置'), 0, ''],
                         [_(u'热床'), [_(u'0:禁止'), _(u'1:开启')], 'choose', '>HAS_TEMP_BED', _(u'热床'), 1, ''],
                         [_(u'挤出头数量'), [1], 'edit', '>EXTRUDERS', _(u'挤出头数量'), 1, ''],
                         [_(u'SINGLE_NOZZLE'), [_(u'0:不支持'), _(u'1:支持')], 'choose', '>SINGLE_NOZZLE', _(u'SINGLE_NOZZLE'), 0, ''],
                         [_(u'使能双Z功能'), [_(u'0:禁止'), _(u'1:开启')], 'choose', '>Z2_STEPPER_DRIVERS', '', 0, ''],
                         [_(u'使能Z轴双限位'), [_(u'0:禁止'), _(u'1:开启')], 'choose', '>Z2_ENDSTOPS', '', 0, ''],
                         [_(u'Z轴第二个限位接口'), [_(u'0:不使用'), _(u'1:Z_MAX'), _(u'2:Z_MIN')], 'choose', '>Z2_USE_ENDSTOP', '', 0, ''],
                         [_(u'X轴最小行程'), [1], 'edit', '>X_MIN_POS', _(u'X轴最小行程,范围为-999~99999'), 0, 'type1'],
                         [_(u'Y轴最小行程'), [1], 'edit', '>Y_MIN_POS', _(u'Y轴最小行程,范围为-999~99999'), 0, 'type1'],
                         [_(u'Z轴最小行程'), [1], 'edit', '>Z_MIN_POS', '', 0, 'type1'],
                         [_(u'X轴最大行程'), [1], 'edit', '>X_MAX_POS', '', 210, 'type1'],
                         [_(u'Y轴最大行程'), [1], 'edit', '>Y_MAX_POS', '', 210, 'type1'],
                         [_(u'Z轴最大行程'), [1], 'edit', '>Z_MAX_POS', '', 210, 'type1'],
                         [_(u'暂停时X轴的位置'), [1], 'edit', '>FILAMENT_CHANGE_X_POS', '', 5, 'type1'],
                         [_(u'暂停时Y轴的位置'), [1], 'edit', '>FILAMENT_CHANGE_Y_POS', '', 5, 'type1'],
                         [_(u'暂停时Z轴的位置'), [1], 'edit', '>FILAMENT_CHANGE_Z_ADD', '', 5, 'type1'],
                         [_(u'双头时X轴的偏移值'), [1], 'edit', '>HOTEND_OFFSET_X', '', 20, 'type1'],
                         [_(u'双头时Y轴的偏移值'), [1], 'edit', '>HOTEND_OFFSET_Y', '', 5, 'type1'],
                         [_(u'X轴的电机方向'), [_(u'0:反转'), _(u'1:正转')], 'choose', '>INVERT_X_DIR', '', 1, ''],
                         [_(u'Y轴的电机方向'), [_(u'0:反转'), _(u'1:正转')], 'choose', '>INVERT_Y_DIR', '', 1, ''],
                         [_(u'Z轴的电机方向'), [_(u'0:反转'), _(u'1:正转')], 'choose', '>INVERT_Z_DIR', '', 1, ''],
                         [_(u'E0轴的电机方向'), [_(u'0:反转'), _(u'1:正转')], 'choose', '>INVERT_E0_DIR', '', 1, ''],
                         [_(u'E1轴的电机方向'), [_(u'0:反转'), _(u'1:正转')], 'choose', '>INVERT_E1_DIR', '', 1, ''],
                         [_(u'X轴脉冲值（Steps/mm）'), [1], 'edit', '>DEFAULT_X_STEPS_PER_UNIT', '', 80, 'type2'],
                         [_(u'Y轴脉冲值（Steps/mm）'), [1], 'edit', '>DEFAULT_Y_STEPS_PER_UNIT', '', 80, 'type2'],
                         [_(u'Z轴脉冲值（Steps/mm）'), [1], 'edit', '>DEFAULT_Z_STEPS_PER_UNIT', '', 4000, 'type2'],
                         [_(u'E0轴脉冲值（Steps/mm）'), [1], 'edit', '>DEFAULT_E0_STEPS_PER_UNIT', '', 90, 'type2'],
                         [_(u'E1轴脉冲值（Steps/mm）'), [1], 'edit', '>DEFAULT_E1_STEPS_PER_UNIT', '', 90, 'type2'],
                         [_(u'X轴默认速度 (mm/s)'), [1], 'edit', '>DEFAULT_X_MAX_FEEDRATE', '', 200, 'type2'],
                         [_(u'Y轴默认速度 (mm/s)'), [1], 'edit', '>DEFAULT_Y_MAX_FEEDRATE', '', 200, 'type2'],
                         [_(u'Z轴默认速度 (mm/s)'), [1], 'edit', '>DEFAULT_Z_MAX_FEEDRATE', '', 40, 'type2'],
                         [_(u'E0轴默认速度 (mm/s)'), [1], 'edit', '>DEFAULT_E0_MAX_FEEDRATE', '', 70, 'type2'],
                         [_(u'E1轴默认速度 (mm/s)'), [1], 'edit', '>DEFAULT_E1_MAX_FEEDRATE', '', 70, 'type2'],
                         [_(u'X轴默认最大加速度 (mm/s)'), [1], 'edit', '>DEFAULT_X_MAX_ACCELERATION', '', 1000, 'type2'],
                         [_(u'Y轴默认最大加速度 (mm/s)'), [1], 'edit', '>DEFAULT_Y_MAX_ACCELERATION', '', 1000, 'type2'],
                         [_(u'Z轴默认最大加速度 (mm/s)'), [1], 'edit', '>DEFAULT_Z_MAX_ACCELERATION', '', 100, 'type2'],
                         [_(u'E0轴默认最大加速度 (mm/s)'), [1], 'edit', '>DEFAULT_E0_MAX_ACCELERATION', '', 1000, 'type2'],
                         [_(u'E1轴默认最大加速度 (mm/s)'), [1], 'edit', '>DEFAULT_E1_MAX_ACCELERATION', '', 1000, 'type2'],
                         [_(u'X,Y,Z,E 打印时的默认加速度'), [1], 'edit', '>DEFAULT_ACCELERATION', '', 1000, 'type2'],
                         [_(u'X,Y,Z,E 回抽默认加速度'), [1], 'edit', '>DEFAULT_RETRACT_ACCELERATION', '', 1000, 'type2'],
                         [_(u'X,Y,Z 非打印时的默认加速度'), [1], 'edit', '>DEFAULT_TRAVEL_ACCELERATION', '', 1000, 'type2'],
                         [_(u'默认最小速度'), [1], 'edit', '>DEFAULT_MINIMUMFEEDRATE', '', 0, 'type2'],
                         [_(u'>DEFAULT_MINSEGMENTTIME'), [1], 'edit', '>DEFAULT_MINSEGMENTTIME', '', 20000, 'type2'],
                         [_(u'>DEFAULT_MINTRAVELFEEDRATE'), [1], 'edit', '>DEFAULT_MINTRAVELFEEDRATE', '', 0, 'type2'],
                         [_(u'X轴 Jerk (mm/s)'), [1], 'edit', '>DEFAULT_XJERK', '', 20, 'type2'],
                         [_(u'Y轴 Jerk (mm/s)'), [1], 'edit', '>DEFAULT_YJERK', '', 20, 'type2'],
                         [_(u'Z轴 Jerk (mm/s)'), [1], 'edit', '>DEFAULT_ZJERK', '', 0.4, 'type2'],
                         [_(u'E轴 Jerk (mm/s)'), [1], 'edit', '>DEFAULT_EJERK', '', 5, 'type2'],
                         [_(u'X轴高低电平使能'), [_(u'0:低'), _(u'1:高')], 'choose', '>X_ENABLE_ON', '', 0, ''],
                         [_(u'Y轴高低电平使能'), [_(u'0:低'), _(u'1:高')], 'choose', '>Y_ENABLE_ON', '', 0, ''],
                         [_(u'Z轴高低电平使能'), [_(u'0:低'), _(u'1:高')], 'choose', '>Z_ENABLE_ON', '', 0, ''],
                         [_(u'E轴高低电平使能'), [_(u'0:低'), _(u'1:高')], 'choose', '>E_ENABLE_ON', '', 0, ''],
                         [_(u'脉冲保持时间'), [1], 'edit', '>PULSE_DELAY', _(u'脉冲保持时间（单位：机器周期）'), 5, 'type2'],
                         [_(u'挤出头热敏类型'), [_(u'1:100k热敏'), _(u'-3:MAX31855热电偶')], 'choose', '>TEMP_SENSOR_0', '', 1, ''],
                         [_(u'挤出机最低挤出温度'), [1], 'edit', '>EXTRUDE_MINTEMP', '', 170, 'type2'],
                         [_(u'挤出头1最低温度'), [1], 'edit', '>HEATER_0_MINTEMP', '', 5, 'type2'],
                         [_(u'挤出头1最大温度'), [1], 'edit', '>HEATER_0_MAXTEMP', '', 275, 'type2'],
                         [_(u'挤出头2最低温度'), [1], 'edit', '>HEATER_1_MINTEMP', '', 5, 'type2'],
                         [_(u'挤出头2最大温度'), [1], 'edit', '>HEATER_1_MAXTEMP', '', 275, 'type2'],
                         [_(u'热床最大温度'), [1], 'edit', '>BED_MAXTEMP', '', 150, 'type2'],
                         [_(u'热床最小温度'), [1], 'edit', '>BED_MINTEMP', '', 5, 'type2'],
                         [_(u'>THERMAL_PROTECTION_PERIOD'), [1], 'edit', '>THERMAL_PROTECTION_PERIOD', '', 140, 'type2'],
                         [_(u'>THERMAL_PROTECTION_HYSTERESIS'), [1], 'edit', '>THERMAL_PROTECTION_HYSTERESIS', '', 4, 'type2'],
                         [_(u'>WATCH_TEMP_PERIOD'), [1], 'edit', '>WATCH_TEMP_PERIOD', '', 120, 'type2'],
                         [_(u'>WATCH_TEMP_INCREASE'), [1], 'edit', '>WATCH_TEMP_INCREASE', '', 2, 'type2'],
                         [_(u'>THERMAL_PROTECTION_BED_PERIOD'), [1], 'edit', '>THERMAL_PROTECTION_BED_PERIOD', '', 120, 'type2'],
                         [_(u'>THERMAL_PROTECTION_BED_HYSTERESIS'), [1], 'edit', '>THERMAL_PROTECTION_BED_HYSTERESIS', '', 2, 'type2'],
                         [_(u'>WATCH_BED_TEMP_PERIOD'), [1], 'edit', '>WATCH_BED_TEMP_PERIOD', '', 160, 'type2'],
                         [_(u'>WATCH_BED_TEMP_INCREASE'), [1], 'edit', '>WATCH_BED_TEMP_INCREASE', '', 2, 'type2'],
                         [_(u'挤出头温控模式选择'), [_(u'0:bang-bang'), _(u'1:PID')], 'choose', '>PIDTEMPE', '', 1, ''],
                         [_(u'挤出头温控P值设置'), [1], 'edit', '>DEFAULT_Kp', '', 22.2, 'type2'],
                         [_(u'挤出头温控I值设置'), [1], 'edit', '>DEFAULT_Ki', '', 1.08, 'type2'],
                         [_(u'挤出头温控D值设置'), [1], 'edit', '>DEFAULT_Kd', '', 114, 'type2'],
                         [_(u'热床温度调控模式选择'), [_(u'0:bang-bang'), _(u'1:PID')], 'choose', '>PIDTEMPBED', '', 0, ''],
                         [_(u'热床温控P值设置'), [1], 'edit', '>DEFAULT_bedKp', '', 10.02, 'type2'],
                         [_(u'热床温控I值设置'), [1], 'edit', '>DEFAULT_bedKi', '', 0.023, 'type2'],
                         [_(u'热床温控D值设置'), [1], 'edit', '>DEFAULT_bedKd', '', 305.4, 'type2'],
                         [_(u'最小软限位'), [_(u'0:禁止'), _(u'1:开启')], 'choose', '>MIN_SOFTWARE_ENDSTOPS', '', 1, ''],
                         [_(u'最大软限位'), [_(u'0:禁止'), _(u'1:开启')], 'choose', '>MAX_SOFTWARE_ENDSTOPS', '', 1, ''],
                         [_(u'使能X轴最小值限位开关'), [_(u'0:禁止'), _(u'1:开启')], 'choose', '>USE_XMIN_PLUG', '', 1, ''],
                         [_(u'使能Y轴最小值限位开关'), [_(u'0:禁止'), _(u'1:开启')], 'choose', '>USE_YMIN_PLUG', '', 1, ''],
                         [_(u'使能Z轴最小值限位开关'), [_(u'0:禁止'), _(u'1:开启')], 'choose', '>USE_ZMIN_PLUG', '', 1, ''],
                         [_(u'使能X轴最大值限位开关'), [_(u'0:禁止'), _(u'1:开启')], 'choose', '>USE_XMAX_PLUG', '', 0, ''],
                         [_(u'使能Y轴最大值限位开关'), [_(u'0:禁止'), _(u'1:开启')], 'choose', '>USE_YMAX_PLUG', '', 0, ''],
                         [_(u'使能Z轴最大值限位开关'), [_(u'0:禁止'), _(u'1:开启')], 'choose', '>USE_ZMAX_PLUG', '', 0, ''],
                         [_(u'X轴最小限位开关类型'), [_(u'0:常开'), _(u'1:关闭')], 'choose', '>X_MIN_ENDSTOP_INVERTING', '', 0, ''],
                         [_(u'Y轴最小限位开关类型'), [_(u'0:常开'), _(u'1:关闭')], 'choose', '>Y_MIN_ENDSTOP_INVERTING', '', 0, ''],
                         [_(u'Z轴最小限位开关类型'), [_(u'0:常开'), _(u'1:关闭')], 'choose', '>Z_MIN_ENDSTOP_INVERTING', '', 0, ''],
                         [_(u'X轴最大限位开关类型'), [_(u'0:常开'), _(u'1:关闭')], 'choose', '>X_MAX_ENDSTOP_INVERTING', '', 1, ''],
                         [_(u'Y轴最大限位开关类型'), [_(u'0:常开'), _(u'1:关闭')], 'choose', '>Y_MAX_ENDSTOP_INVERTING', '', 1, ''],
                         [_(u'Z轴最大限位开关类型'), [_(u'0:常开'), _(u'1:关闭')], 'choose', '>Z_MAX_ENDSTOP_INVERTING', '', 1, ''],
                         [_(u'Z_PROBE限位开关类型'), [_(u'0:常开'), _(u'1:关闭')], 'choose', '>Z_MIN_PROBE_ENDSTOP_INVERTING', '', 1, ''],
                         [_(u'X轴回零方向'), [_(u'-1:最小值方向'), _(u'1:最大值方向')], 'choose', '>X_HOME_DIR', '', -1, ''],
                         [_(u'Y轴回零方向'), [_(u'-1:最小值方向'), _(u'1:最大值方向')], 'choose', '>Y_HOME_DIR', '', -1, ''],
                         [_(u'Z轴回零方向'), [_(u'-1:最小值方向'), _(u'1:最大值方向')], 'choose', '>Z_HOME_DIR', '', -1, ''],
                         [_(u'XY轴回零速度 (mm/m)'), [1], 'edit', '>HOMING_FEEDRATE_XY', '', 2400, 'type2'],
                         [_(u'Z轴回零速度 (mm/m)'), [1], 'edit', '>HOMING_FEEDRATE_Z', '', 2400, 'type2'],
                         [_(u'回零时xy轴的顺序'), [_(u'0:X先回零'), _(u'1:Y先回零')], 'choose', '>HOME_Y_BEFORE_X', '', 0, ''],
                         [_(u'打完关机'), [_(u'0:禁止'), _(u'1:开启')], 'choose', '>cfg_print_over_auto_close', '', 1, ''],
                         [_(u'打完关机延时时间（秒）'), [1], 'edit', '>PRINT_FINISHED_COUNT', _(U'打完关机延时时间（单位：秒）'), 180, 'type2'],
                         [_(u'是否接UPS电源'), [_(u'0:禁止'), _(u'1:开启')], 'choose', '>cfg_have_ups_device', '', 0, ''],
                         [_(u'接入断电检测模块'), [_(u'0:mks pwc'), _(u'1:mks 220det'), _(u'0:mks ups')], 'choose','>cfg_insert_det_module', '', 0, ''],
                         [_(u'挤出头1断料检测'), [_(u'0:低电平触发'), _(u'1:高电平触发')], 'choose', '>cfg_filament_det0_trigger_level', '', 0, ''],
                         [_(u'挤出头2断料检测'), [_(u'0:低电平触发'), _(u'1:高电平触发')], 'choose', '>cfg_filament_det1_trigger_level', '', 0, ''],
                         [_(u'换料进料的长度'), [1], 'edit', '>cfg_filament_load_length', '', 100, 'type2'],
                         [_(u'换料进料速度配置(mm/min)'), [1], 'edit', '>cfg_filament_load_speed', '', 800, 'type2'],
                         [_(u'换料进料最低限制温度配置'), [1], 'edit', '>cfg_filament_load_limit_temperature', '', 200, 'type2'],
                         [_(u'换料退料的长度'), [1], 'edit', '>cfg_filament_unload_length', '', 100, 'type2'],
                         [_(u'换料退料速度配置(mm/min)'), [1], 'edit', '>cfg_filament_unload_speed', '', 800, 'type2'],
                         [_(u'换料退料最低限制温度配置'), [1], 'edit', '>cfg_filament_unload_limit_temperature', '', 200, 'type2'],
                         [_(u'调平方式'), [_(u'0:手动调平'), _(u'1:自动调平')], 'choose', '>cfg_leveling_mode', '', 0, ''],
                         [_(u'手动调平的调平点数'), [_(u'3:3'), _(u'4:4'), _(u'5:5')], 'choose', '>cfg_point_number', '', 5, ''],
                         [_(u'调平点1（X,Y）'), [1], 'edit', '>cfg_point1:', '', '20,20', 'type2'],
                         [_(u'调平点2（X,Y）'), [1], 'edit', '>cfg_point2:', '', '200,20', 'type2'],
                         [_(u'调平点3（X,Y）'), [1], 'edit', '>cfg_point3:', '', '200,200', 'type2'],
                         [_(u'调平点4（X,Y）'), [1], 'edit', '>cfg_point4:', '', '20,200', 'type2'],
                         [_(u'调平点5（X,Y）'), [1], 'edit', '>cfg_point5:', '', '100,100', 'type2'],
                         [_(u'自动调平指令'), [1], 'edit', '>cfg_auto_leveling_cmd:', '', 'G28;G29;', 'type3'],
                         [_(u'自动调平方式'), [_(u'0:不使用调平'), _(u'3:多点自动调平'), _(u'5:手动网格调平')], 'choose', '>BED_LEVELING_METHOD', '', 0, ''],
                         [_(u'调平的探针'), [_(u'0:不使用'), _(u'1:接Z_MIN'), _(u'2:接ZMAX')], 'choose', '>Z_MIN_PROBE_PIN_MODE', '', 0, ''],
                         [_(u'BLTOUCH'), [_(u'0:禁用'), _(u'1:启用')], 'choose', '>BLTOUCH','', 0, ''],
                         [_(u'探针X轴偏移量'), [1], 'edit', '>Z_PROBE_OFFSET_FROM_EXTRUDER', '', 0, 'type1'],
                         [_(u'探针Y轴偏移量'), [1], 'edit', '>X_PROBE_OFFSET_FROM_EXTRUDER', '', 0, 'type1'],
                         [_(u'探针Z轴偏移量'), [1], 'edit', '>Y_PROBE_OFFSET_FROM_EXTRUDER', '', 0, 'type1'],
                         [_(u'调平时探针XY轴移动速度(mm/m)'), [1], 'edit', '>XY_PROBE_SPEED', '', 4000, 'type2'],
                         [_(u'调平时探针下降第一段速度(mm/m)'), [1], 'edit', '>Z_PROBE_SPEED_FAST', '', 600, 'type2'],
                         [_(u'调平时探针下降第二段速度(mm/m)'), [1], 'edit', '>Z_PROBE_SPEED_SLOW', '', 300, 'type2'],
                         [_(u'Z_SAFE_HOMING'), [_(u'0:不使能'), _(u'1:使能')], 'choose', '>Z_SAFE_HOMING', _(u'使能，避免回零时探针在热床'), 0, ''],
                         [_(u'自动调平X轴上点数'), [1], 'edit', '>GRID_MAX_POINTS_X', '', 3, 'type2'],
                         [_(u'自动调平Y轴上点数'), [1], 'edit', '>GRID_MAX_POINTS_Y', '', 3, 'type2'],
                         [_(u'Z轴抬起/放下的距离'), [1], 'edit', '>Z_CLEARANCE_DEPLOY_PROBE', '', 20, 'type2'],
                         [_(u'Z轴在两个调平点的的移动高度'), [1], 'edit', '>Z_CLEARANCE_BETWEEN_PROBES', '', 20, 'type2'],
                         [_(u'调平热床边界距离X1'), [1], 'edit', '>LEFT_PROBE_BED_POSITION', '', 30, 'type2'],
                         [_(u'调平热床边界距离X2'), [1], 'edit', '>RIGHT_PROBE_BED_POSITION', '', 200, 'type2'],
                         [_(u'调平热床边界距离Y1'), [1], 'edit', '>FRONT_PROBE_BED_POSITION', '', 30, 'type2'],
                         [_(u'调平热床边界距离Y2'), [1], 'edit', '>BACK_PROBE_BED_POSITION', '', 200, 'type2'],
                         [_(u'MESH_BED_LEVELING调平模式下边界距离范围'), [1], 'edit', '>MESH_INSET', '', 20, 'type2'],
                         [_(u'DELTA_SEGMENTS_PER_SECOND'), [1], 'edit', '>DELTA_SEGMENTS_PER_SECOND', '', 40, 'type2'],
                         [_(u'DELTA_DIAGONAL_ROD'), [1], 'edit', '>DELTA_DIAGONAL_ROD', '', 346, 'type2'],
                         [_(u'DELTA_SMOOTH_ROD_OFFSET'), [1], 'edit', '>DELTA_SMOOTH_ROD_OFFSET', '', 211, 'type2'],
                         [_(u'DELTA_EFFECTOR_OFFSET'), [1], 'edit', '>DELTA_EFFECTOR_OFFSET', '', 28, 'type2'],
                         [_(u'DELTA_CARRIAGE_OFFSET'), [1], 'edit', '>DELTA_CARRIAGE_OFFSET', '', 14.5, 'type2'],
                         [_(u'DELTA_RADIUS'), [1], 'edit', '>DELTA_RADIUS', '', 169, 'type2'],
                         [_(u'DELTA_HEIGHT'), [1], 'edit', '>DELTA_HEIGHT', '', 302, 'type2'],
                         [_(u'DELTA_PRINTABLE_RADIUS'), [1], 'edit', '>DELTA_PRINTABLE_RADIUS', '', 125, 'type2'],
                         [_(u'DELTA_CALIBRATION_RADIUS'), [1], 'edit', '>DELTA_CALIBRATION_RADIUS', '', 100, 'type2'],
                         [_(u'WIFI模式'), [_(u'0:STA'), _(u'1:AP')], 'choose', '>CFG_WIFI_MODE', '', 1, ''],
                         [_(u'WIFI名称'), [1], 'edit', '>CFG_WIFI_AP_NAME', '', 'WIFITEST', 'type3'],
                         [_(u'WIFI密码'), [1], 'edit', '>CFG_WIFI_KEY_CODE', '', 'makerbase', 'type3'],
                         [_(u'云服务使能'), [_(u'0:禁止'), _(u'1:使能')], 'choose', '>CFG_CLOUD_ENABLE', '', 1, ''],
                         [_(u'云服务链接'), [1], 'edit', '>CFG_WIFI_CLOUD_HOST', '', 'www.baizhongyun.cn', 'type3'],
                         [_(u'云服务端口'), [1], 'edit', '>CFG_CLOUD_PORT', '', '10086', 'type2'],
                         [_(u'使用wifi列表扫描'), [_(u'0:禁用'), _(u'1:启用')], 'choose', '>WISI_LIST_SCAN', _(u'是否使用wifi列表扫描'), 1, ''],
                         [_(u'显示wifi按钮'), [_(u'0:显示'), _(u'1:不显示')], 'choose', '>DISABLE_WIFI', '', 0, ''],
                         [_(u'About_type'), [1], 'edit', '>about_type:', '', 'Robin_nano35', ''],
                         [_(u'About_version'), [1], 'edit', '>about_version:', '', 'V2.0.2', ''],
                         [_(u'About_company'), [1], 'edit', '>about_company:', '', '', ''],
                         [_(u'About_email'), [1], 'edit', '>about_email:', '', '', ''],
                         [_(u'暂停挤出量(mm)'), [1], 'edit', '>PAUSE_UNLOAD_LEN', _(u'暂停挤出量(mm)'), '-3', 'type1'],
                         [_(u'恢复挤出量(mm)'), [1], 'edit', '>RESUME_LOAD_LEN', _(u'恢复挤出量(mm)'), '10', 'type2'],
                         [_(u'恢复挤出增加百分比(%)'), [1], 'edit', '>RESUME_SPEED', _(u'恢复挤出增加百分比，为0时该项不起作用（单位：%）'), '80', ''],
                         [_(u'唤醒功能'), [_(u'0:关闭'), _(u'1:开启')], 'choose', '>cfg_Standby_mode', _(u'是否开启唤醒功能'), 0, ''],
                         [_(u'进入休眠时间(s)'), [1], 'edit', '>cfg_Standby_gap_time', _(u'设置进入休眠时间（单位：秒）'), '600', 'type2'],
                         [_(u'设置界面自定义功能'), [_(u'0:不显示'), _(u'1:显示')], 'choose', '>setmenu_func1_display', '', 0, ''],
                         [_(u'setmenu_func1'), [1], 'edit', '>setmenu_func1', _(u'每条指令必须用分号";"隔开'), 'M84;', 'type3'],
                         [_(u'更多界面自定义数量按钮'), [1], 'edit', '>moreitem_pic_cnt', '', '7', ''],
                         [_(u'更多界面自定义按钮1'), [1], 'edit', '>moreitem_button1_cmd:', _(u'每条指令必须用分号";"隔开'), 'G28 X0;G28 Y0;G28 Z0;', 'type3'],
                         [_(u'更多界面自定义按钮2'), [1], 'edit', '>moreitem_button2_cmd:', _(u'每条指令必须用分号";"隔开'), 'G28 X0;G28 Y0;G28 Z0;', 'type3'],
                         [_(u'更多界面自定义按钮3'), [1], 'edit', '>moreitem_button3_cmd:', _(u'每条指令必须用分号";"隔开'), 'G28 X0;G28 Y0;G28 Z0;', 'type3'],
                         [_(u'更多界面自定义按钮4'), [1], 'edit', '>moreitem_button4_cmd:', _(u'每条指令必须用分号";"隔开'), 'G28 X0;G28 Y0;G28 Z0;', 'type3'],
                         [_(u'更多界面自定义按钮5'), [1], 'edit', '>moreitem_button5_cmd:', _(u'每条指令必须用分号";"隔开'), 'G28 X0;G28 Y0;G28 Z0;', 'type3'],
                         [_(u'更多界面自定义按钮6'), [1], 'edit', '>moreitem_button6_cmd:', _(u'每条指令必须用分号";"隔开'), 'G28 X0;G28 Y0;G28 Z0;', 'type3'],
                         [_(u'更多界面自定义按钮7'), [1], 'edit', '>moreitem_button7_cmd:', _(u'每条指令必须用分号";"隔开'), 'G28 X0;G28 Y0;G28 Z0;', 'type3'],
                         [_(u'打印中更多界面自定义数量按钮'), [1], 'edit', '>morefunc_cnt', '', '7', 'type2'],
                         [_(u'打印中更多界面自定义按钮1'), [1], 'edit', '>morefunc1_cmd:', _(u'每条指令必须用分号";"隔开'), 'G28;', 'type3'],
                         [_(u'打印中更多界面自定义按钮2'), [1], 'edit', '>morefunc2_cmd:', _(u'每条指令必须用分号";"隔开'), 'G28;', 'type3'],
                         [_(u'打印中更多界面自定义按钮3'), [1], 'edit', '>morefunc3_cmd:', _(u'每条指令必须用分号";"隔开'), 'G28;', 'type3'],
                         [_(u'打印中更多界面自定义按钮4'), [1], 'edit', '>morefunc4_cmd:', _(u'每条指令必须用分号";"隔开'), 'G28;', 'type3'],
                         [_(u'打印中更多界面自定义按钮5'), [1], 'edit', '>morefunc5_cmd:', _(u'每条指令必须用分号";"隔开'), 'G28;', 'type3'],
                         [_(u'打印中更多界面自定义按钮6'), [1], 'edit', '>morefunc6_cmd:', _(u'每条指令必须用分号";"隔开'), 'G28;', 'type3'],
                         [_(u'打印中更多界面自定义按钮7'), [1], 'edit', '>morefunc7_cmd:', _(u'每条指令必须用分号";"隔开'), 'G28;', 'type3'],
                         [_(u'屏幕背景色'), [1], 'edit', '>cfg_background_color', '', '0x000000', 'type3'],
                         [_(u'标题文字'), [1], 'edit', '>cfg_title_color', '', '0xFFFFFF', 'type3'],
                         [_(u'状态栏背景色'), [1], 'edit', '>cfg_state_bkcolor', '', '0x000000', 'type3'],
                         [_(u'状态栏字体颜色'), [1], 'edit', '>cfg_state_textcolor', '', '0xFFFFFF', 'type3'],
                         [_(u'文件目录按钮背景色'), [1], 'edit', '>cfg_filename_bkcolor', '', '0x000000', 'type3'],
                         [_(u'文件目录按钮字体颜色'), [1], 'edit', '>cfg_filename_textcolor', '', '0xFFFFFF', 'type3'],
                         [_(u'通用按钮背景色'), [1], 'edit', '>cfg_btn_bkcolor', '', '0x000000', 'type3'],
                         [_(u'通用按钮文字颜色'), [1], 'edit', '>cfg_btn_textcolor', '', '0xFFFFFF', 'type3'],
                         [_(u'状态按钮背景色'), [1], 'edit', '>cfg_state_btn_bkcolor', '', '0x000000', 'type3'],
                         [_(u'状态按钮字体颜色'), [1], 'edit', '>cfg_state_btn_textcolor', '', '0xFFFFFF', 'type3'],
                         [_(u'"返回"键背景色'), [1], 'edit', '>cfg_back_btn_bkcolor', '', '0x000000', 'type3'],
                         [_(u'"返回"键字体颜色'), [1], 'edit', '>cfg_back_btn_textcolor', '', '0xFFFFFF', 'type3'],
                         [_(u'选定按钮背景色'), [1], 'edit', '>cfg_sel_btn_bkcolor', '', '0x000000', 'type3'],
                         [_(u'选定按钮字体颜色'), [1], 'edit', '>cfg_sel_btn_textcolor', '', '0xFFFFFF', 'type3'],
                         [_(u'对话框按钮背景色'), [1], 'edit', '>cfg_dialog_btn_bkcolor', '', '0x000000', 'type3'],
                         [_(u'对话框按钮字体颜色'), [1], 'edit', '>cfg_dialog_btn_textcolor', '', '0xFFFFFF', 'type3'],
                         [_(u'按钮字体偏移底边位置'), [1], 'edit', '>cfg_btn_text_offset', '', 23, 'type2']
                         ]
        self._textlist = []
        self.btnlist = []
        self.choosefilebtnlist = []
        self.printingbtnlist = []
        self.widgetlist = []
        self.selectedpath = ""
        self.outputpath = None
        self.viewimglist = None
        self.selectbtnpos = 0
        self.viewpos = 0
        self.underselectpos = 0
        self._picwidth = 117
        self._picheight = 140
        self.progressing = False
        self._mdialog = None
        self.initview()
        self.Update()

    def initview(self):
        self.SetMinSize((650, 580))
        self.SetSize((650, 580))
        self._mainpanel = wx.Panel(self,-1)
        self.toppanel = wx.Panel(self._mainpanel,-1,size=(-1,23))

        #toppanelview
        self.viewcb = wx.ComboBox(self.toppanel, -1, value=self._typelist[0], choices=self._typelist,style=wx.CB_READONLY)
        self.viewcb.Bind(wx.EVT_COMBOBOX, lambda evt, widget=self.viewcb: self.pixelchange(evt, widget))
        self.viewcb.Enable(False)
        self._dlgbutton = wx.Button(self.toppanel, -1, _(u'配置文件'))
        self._dlgbutton.Bind(wx.EVT_BUTTON, self.showConfigDialog)
        # self.wtext = wx.StaticText(self.toppanel,-1,_(u'宽：'),style=wx.ALIGN_CENTER | wx.ST_NO_AUTORESIZE)
        # self.wctr = wx.TextCtrl(self.toppanel, -1, value='78',size=(50,-1))
        # self.htext = wx.StaticText(self.toppanel, -1,_(u'高：'), style=wx.ALIGN_CENTER | wx.ST_NO_AUTORESIZE)
        # self.hctr = wx.TextCtrl(self.toppanel, -1, value='104', size=(50, -1))
        self.language = wx.ComboBox(self.toppanel, -1, value=self.languagelist[0],choices=self.languagelist,style=wx.CB_READONLY)
        self.language.Bind(wx.EVT_COMBOBOX, lambda evt, widget=self.language: self.changelanguage(evt, widget))
        if self.languagename == 'en':
            self.language.SetValue(self.languagelist[1])
        self.topsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.topsizer.Add(self.viewcb,0,wx.LEFT|wx.RIGHT,border=10)
        # self.topsizer.Add(self.wtext, 0, wx.TOP, border=5)
        # self.topsizer.Add(self.wctr, 0, wx.RIGHT, border=10)
        # self.topsizer.Add(self.htext, 0, wx.TOP, border=5)
        # self.topsizer.Add(self.hctr, 0, wx.RIGHT, border=10)
        self.topsizer.Add(self.language,0,wx.LEFT,border=10)
        self.topsizer.Add(self._dlgbutton, 0, wx.LEFT, border=10)
        self.toppanel.SetSizer(self.topsizer)

        self.makeImage('bai.png','#ffffff',False)
        self.makeImage('hei.png', '#000000',False)
        self.normalbitmap = wx.Image(os.path.abspath("")+"\\bai.png", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.hnormalbitmap = wx.Image(os.path.abspath("") + "\\hei.png", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.bottompanel = wx.Panel(self._mainpanel,-1)
        self.bottompanel.SetMinSize((480, 320))
        self.bottompanel.SetBackgroundColour('#000000')

        #topsizer with four image
        self.btlogo = self.getStaticBmp(self._mainpanel, self.normalbitmap, lambda e, pos=0: self.ChangeBitmap(e, pos))
        self.btlogo.SetMinSize((480, 320))
        self.btlogo.SetBackgroundColour('#000000')
        self.btlogo.SetDropTarget(FileDropTarget(self, self.dropCallback, 0))
        self.btone = self.getStaticBmp(self.bottompanel,self.normalbitmap, lambda e, pos=0: self.ChangeBitmap(e, pos))
        self.bttwo = self.getStaticBmp(self.bottompanel,self.normalbitmap, lambda e, pos=1: self.ChangeBitmap(e, pos))
        self.btthree = self.getStaticBmp(self.bottompanel,self.normalbitmap, lambda e, pos=2: self.ChangeBitmap(e, pos))
        self.btfour = self.getStaticBmp(self.bottompanel,self.normalbitmap, lambda e, pos=3: self.ChangeBitmap(e, pos))
        self.btone.SetDropTarget(FileDropTarget(self, self.dropCallback, 0))
        self.bttwo.SetDropTarget(FileDropTarget(self, self.dropCallback, 1))
        self.btthree.SetDropTarget(FileDropTarget(self, self.dropCallback, 2))
        self.btfour.SetDropTarget(FileDropTarget(self, self.dropCallback, 3))

        self.bbone = self.getStaticBmp(self.bottompanel,self.normalbitmap, lambda e, pos=4: self.ChangeBitmap(e, pos))
        self.bbtwo = self.getStaticBmp(self.bottompanel,self.normalbitmap, lambda e, pos=5: self.ChangeBitmap(e, pos))
        self.bbthree = self.getStaticBmp(self.bottompanel,self.normalbitmap, lambda e, pos=6: self.ChangeBitmap(e, pos))
        self.bbfour = self.getStaticBmp(self.bottompanel,self.normalbitmap, lambda e, pos=7: self.ChangeBitmap(e, pos))
        self.bbone.SetDropTarget(FileDropTarget(self, self.dropCallback, 4))
        self.bbtwo.SetDropTarget(FileDropTarget(self, self.dropCallback, 5))
        self.bbthree.SetDropTarget(FileDropTarget(self, self.dropCallback, 6))
        self.bbfour.SetDropTarget(FileDropTarget(self, self.dropCallback, 7))

        self.btnlist[:] =[self.btone,self.bttwo,self.btthree,self.btfour,self.bbone,self.bbtwo,self.bbthree,self.bbfour]

        # self.btone.SetSize((320, 240))
        # for i in range(1, len(self.btnlist)):
            # self.btnlist[i].Hide()

        self.choosefilepanel = wx.Panel(self._mainpanel,-1)
        self.choosefilepanel.SetMinSize((480, 320))
        self.choosefilepanel.SetBackgroundColour('#000000')
        # 第一列
        self.cfone = self.getStaticBmp(self.choosefilepanel, self.normalbitmap, lambda e, pos=0: self.choosefileChangeBitmap(e, pos))
        self.cftwo = self.getStaticBmp(self.choosefilepanel, self.normalbitmap, lambda e, pos=1: self.choosefileChangeBitmap(e, pos))
        self.cfone.SetDropTarget(FileDropTarget(self, self.dropCallback, 0))
        self.cftwo.SetDropTarget(FileDropTarget(self, self.dropCallback, 1))
        # 第二列
        self.cfbone = self.getStaticBmp(self.choosefilepanel, self.normalbitmap, lambda e, pos=2: self.choosefileChangeBitmap(e, pos))
        self.cfbtwo = self.getStaticBmp(self.choosefilepanel, self.normalbitmap, lambda e, pos=3: self.choosefileChangeBitmap(e, pos))
        self.cfbone.SetDropTarget(FileDropTarget(self, self.dropCallback, 2))
        self.cfbtwo.SetDropTarget(FileDropTarget(self, self.dropCallback, 3))
        # 第三列
        self.cfdone = self.getStaticBmp(self.choosefilepanel, self.normalbitmap, lambda e, pos=4: self.choosefileChangeBitmap(e, pos))
        self.cfdtwo = self.getStaticBmp(self.choosefilepanel, self.normalbitmap, lambda e, pos=5: self.choosefileChangeBitmap(e, pos))
        self.cfdone.SetDropTarget(FileDropTarget(self, self.dropCallback, 4))
        self.cfdtwo.SetDropTarget(FileDropTarget(self, self.dropCallback, 5))
        # 竖列
        self.cfhone = self.getWHBmp(self.choosefilepanel, self.normalbitmap,117,92, lambda e, pos=6: self.choosefileChangeBitmap(e, pos))
        self.cfhtwo = self.getWHBmp(self.choosefilepanel, self.normalbitmap,117,92, lambda e, pos=7: self.choosefileChangeBitmap(e, pos))
        self.cfhthree = self.getWHBmp(self.choosefilepanel, self.normalbitmap,117,92, lambda e, pos=8: self.choosefileChangeBitmap(e, pos))
        self.cfhone.SetDropTarget(FileDropTarget(self, self.dropCallback, 6))
        self.cfhtwo.SetDropTarget(FileDropTarget(self, self.dropCallback, 7))
        self.cfhthree.SetDropTarget(FileDropTarget(self, self.dropCallback, 8))
        self.choosefilebtnlist[:] = [self.cfone, self.cftwo, self.cfbone, self.cfbtwo, self.cfdone, self.cfdtwo, self.cfhone, self.cfhtwo, self.cfhthree]
        self.cflefttopsizer = wx.BoxSizer(wx.VERTICAL)
        self.cflefttopsizer.Add(self.cfone, 0, wx.ALL|wx.ALIGN_CENTER|wx.ALIGN_RIGHT, border=1)
        self.cflefttopsizer.Add(self.cftwo, 0, wx.ALL|wx.ALIGN_CENTER|wx.ALIGN_RIGHT, border=1)
        self.cfleftbotsizer = wx.BoxSizer(wx.VERTICAL)
        self.cfleftbotsizer.Add(self.cfbone, 0, wx.ALL|wx.ALIGN_CENTER,border=1)
        self.cfleftbotsizer.Add(self.cfbtwo, 0, wx.ALL|wx.ALIGN_CENTER, border=1)
        self.cfleftsizer = wx.BoxSizer(wx.VERTICAL)
        self.cfleftsizer.Add(self.cfdone, 0, wx.ALL,border=1)
        self.cfleftsizer.Add(self.cfdtwo, 0, wx.ALL, border=1)
        self.cfrightsizer = wx.BoxSizer(wx.VERTICAL)
        self.cfrightsizer.Add(self.cfhone, 0, wx.ALL,border=1)
        self.cfrightsizer.Add(self.cfhtwo, 0,  wx.ALL, border=1)
        self.cfrightsizer.Add(self.cfhthree, 0,  wx.ALL, border=1)
        self.cfsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.cfsizer.Add(self.cflefttopsizer, 2, wx.ALIGN_CENTER|wx.ALIGN_RIGHT, border=1)
        self.cfsizer.Add(self.cfleftbotsizer, 1, wx.ALIGN_CENTER, border=1)
        self.cfsizer.Add(self.cfleftsizer, 1, wx.ALIGN_CENTER, border=1)
        self.cfsizer.Add(self.cfrightsizer, 2, wx.ALIGN_CENTER|wx.ALIGN_LEFT, border=1)
        self.choosefilepanel.SetSizer(self.cfsizer)

        self.printingpanel = wx.Panel(self._mainpanel, -1)
        self.printingpanel.SetMinSize((480, 320))
        self.printingpanel.SetBackgroundColour('#000000')
        self.ptone = self.getWHBmp(self.printingpanel, self.normalbitmap,200,200, lambda e, pos=0: self.printingChangeBitmap(e, pos))
        self.ptone.SetDropTarget(FileDropTarget(self, self.dropCallback, 0))
        self.pbone = self.getWHBmp(self.printingpanel, self.normalbitmap,150,80, lambda e, pos=1: self.printingChangeBitmap(e, pos))
        self.pbtwo = self.getWHBmp(self.printingpanel, self.normalbitmap,150,80, lambda e, pos=2: self.printingChangeBitmap(e, pos))
        self.pbthree = self.getWHBmp(self.printingpanel, self.normalbitmap,150,80, lambda e, pos=3: self.printingChangeBitmap(e, pos))
        self.pbone.SetDropTarget(FileDropTarget(self, self.dropCallback, 1))
        self.pbtwo.SetDropTarget(FileDropTarget(self, self.dropCallback, 2))
        self.pbthree.SetDropTarget(FileDropTarget(self, self.dropCallback, 3))
        self.printingbtnlist[:] = [self.ptone, self.pbone, self.pbtwo, self.pbthree]
        self.ptsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.ptsizer.Add(self.ptone, 0, wx.ALL | wx.ALIGN_BOTTOM, border=1)
        self.pbsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.pbsizer.Add(self.pbone, 0, wx.ALL,border=1)
        self.pbsizer.Add(self.pbtwo, 0, wx.TOP|wx.BOTTOM, border=1)
        self.pbsizer.Add(self.pbthree, 0, wx.ALL, border=1)
        self.printingsizer = wx.BoxSizer(wx.VERTICAL)
        self.printingsizer.Add(self.ptsizer, 1, wx.ALIGN_BOTTOM | wx.ALIGN_CENTER, border=0)
        self.printingsizer.Add(self.pbsizer, 1, wx.ALIGN_CENTER, border=0)
        self.printingpanel.SetSizer(self.printingsizer)
        #
        # # 操作与暂停
        # self.btone1 = self.getWHBmp(self.bottompanel,self.normalbitmap, lambda e, pos=0: self.ChangeBitmap(e, pos))
        # self.bttwo1 = self.getWHBmp(self.bottompanel,self.normalbitmap, lambda e, pos=1: self.ChangeBitmap(e, pos))
        # self.btthree1 = self.getWHBmp(self.bottompanel,self.normalbitmap, lambda e, pos=2: self.ChangeBitmap(e, pos))
        # self.btfour1 = self.getWHBmp(self.bottompanel,self.normalbitmap, lambda e, pos=3: self.ChangeBitmap(e, pos))
        # self.btone1.SetDropTarget(FileDropTarget(self, self.dropCallback, 0))
        # self.bttwo1.SetDropTarget(FileDropTarget(self, self.dropCallback, 1))
        # self.btthree1.SetDropTarget(FileDropTarget(self, self.dropCallback, 2))
        # self.btfour1.SetDropTarget(FileDropTarget(self, self.dropCallback, 3))
        # self.btnlist1[:] =[self.btone1,self.bttwo1,self.btthree1,self.btfour1,self.bbone,self.bbtwo,self.bbthree,self.bbfour]
        # self.btsizer1 = wx.BoxSizer(wx.HORIZONTAL)
        # self.btsizer1.Add(self.btone1, 0, wx.ALL | wx.ALIGN_BOTTOM, border=1)
        # self.btsizer1.Add(self.bttwo1, 0, wx.TOP | wx.BOTTOM | wx.ALIGN_BOTTOM, border=1)
        # self.btsizer1.Add(self.btthree1, 0, wx.LEFT | wx.TOP | wx.BOTTOM | wx.ALIGN_BOTTOM, border=1)
        # self.btsizer1.Add(self.btfour1, 0, wx.ALL | wx.ALIGN_BOTTOM, border=1)
        # # bottomsizer width four image
        # self.bbsizer = wx.BoxSizer(wx.HORIZONTAL)
        # self.bbsizer1.Add(self.bbone, 0, wx.ALL, border=1)
        # self.bbsizer1.Add(self.bbtwo, 0, wx.TOP | wx.BOTTOM, border=1)
        # self.bbsizer1.Add(self.bbthree, 0, wx.LEFT | wx.TOP | wx.BOTTOM, border=1)
        # self.bbsizer1.Add(self.bbfour, 0, wx.ALL, border=1)


        self.btsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.btsizer.Add(self.btone,0,wx.ALL|wx.ALIGN_BOTTOM,border=1)
        self.btsizer.Add(self.bttwo, 0, wx.TOP|wx.BOTTOM|wx.ALIGN_BOTTOM, border=1)
        self.btsizer.Add(self.btthree, 0, wx.LEFT|wx.TOP|wx.BOTTOM|wx.ALIGN_BOTTOM, border=1)
        self.btsizer.Add(self.btfour, 0, wx.ALL|wx.ALIGN_BOTTOM, border=1)
        #bottomsizer width four image
        self.bbsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.bbsizer.Add(self.bbone, 0, wx.ALL,border=1)
        self.bbsizer.Add(self.bbtwo, 0, wx.TOP|wx.BOTTOM, border=1)
        self.bbsizer.Add(self.bbthree, 0, wx.LEFT|wx.TOP|wx.BOTTOM, border=1)
        self.bbsizer.Add(self.bbfour, 0, wx.ALL, border=1)

        self.bottomsizer = wx.BoxSizer(wx.VERTICAL)
        self.bottomsizer.Add(self.btsizer,1,wx.ALIGN_BOTTOM|wx.ALIGN_CENTER,border=0)
        self.bottomsizer.Add(self.bbsizer, 1, wx.ALIGN_CENTER, border=0)
        self.bottompanel.SetSizer(self.bottomsizer)
        self.makeImage('zxc.png', '#000000',True)
        self.underbitmap = wx.Image(os.path.abspath("") + "\\zxc.png", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        # self.underbitmap = self.underbitmap.ConvertToBitmap()
        self.addview = wx.Panel(self._mainpanel, -1, size=(355, 140), style=wx.SIMPLE_BORDER)
        # self.addview.SetMaxSize((355, 140))
        self.addview.SetMinSize((471, 140))
        self.addone = self.getStaticBmp(self.addview,self.underbitmap,lambda e, pos=0: self.addImage(e,pos),lambda e, pos=0:self.showpopupmenu(e,pos))
        self.addtwo = self.getStaticBmp(self.addview,self.underbitmap,lambda e, pos=1: self.addImage(e,pos),lambda e, pos=1:self.showpopupmenu(e,pos))
        self.addthree = self.getStaticBmp(self.addview,self.underbitmap,lambda e, pos=2: self.addImage(e,pos),lambda e, pos=2:self.showpopupmenu(e,pos))
        self.addone.SetDropTarget(FileDropTarget(self, self.dropOTTCallback, 0))
        self.addtwo.SetDropTarget(FileDropTarget(self, self.dropOTTCallback, 1))
        self.addthree.SetDropTarget(FileDropTarget(self, self.dropOTTCallback, 2))
        self.addsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.addsizer.Add(self.addone,0,wx.ALIGN_CENTER|wx.RIGHT|wx.LEFT,border=30)
        self.addsizer.Add(self.addtwo, 0, wx.ALIGN_CENTER, border=0)
        self.addsizer.Add(self.addthree, 0, wx.ALIGN_CENTER|wx.RIGHT|wx.LEFT, border=30)
        self.addview.SetSizer(self.addsizer)

        self.addone.Disable()
        self.addtwo.Disable()
        self.addthree.Disable()


        self.footbar = wx.Panel(self._mainpanel,-1,size=(-1,23))
        self.message = wx.StaticText(self.footbar,-1,_(u'准备..'),style=wx.ALIGN_LEFT | wx.ST_NO_AUTORESIZE)
        self.outputbutton = wx.Button(self.footbar, -1, _(u"导出文件"))
        self.inputbutton = wx.Button(self.footbar, -1, _(u'导入文件夹'))
        self.examplebutton = wx.Button(self.footbar, -1, _(u'导入模板'))
        self.outputbutton.Bind(wx.EVT_BUTTON,self.exportbin)
        self.inputbutton.Bind(wx.EVT_BUTTON, self.inputbin)
        self.examplebutton.Bind(wx.EVT_BUTTON, self.inputexample)
        self.footsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.footsizer.Add(self.message,1,wx.EXPAND|wx.TOP,border=5)
        self.footsizer.Add(self.inputbutton, 0, wx.EXPAND, border = 0)
        self.footsizer.Add(self.outputbutton,0,wx.EXPAND,border=0)
        self.footsizer.Add(self.examplebutton,0,wx.EXPAND,border=0)
        self.footbar.SetSizer(self.footsizer)


        self._mainsizer = wx.BoxSizer(wx.VERTICAL)
        self._mainsizer.Add(self.toppanel,0,wx.EXPAND,border=0)
        self._mainsizer.Add(self.btlogo, 0, wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM,border=5)
        self._mainsizer.Add(self.bottompanel,0,wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM,border=5)
        self._mainsizer.Add(self.choosefilepanel, 0, wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=5)
        self._mainsizer.Add(self.printingpanel, 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=5)
        self._mainsizer.Add(self.addview,0,wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM,border=5)
        self._mainsizer.Add(self.footbar,0,wx.EXPAND|wx.ALIGN_BOTTOM,border=0)

        self.bottompanel.Hide()
        self.choosefilepanel.Hide()
        self.printingpanel.Hide()

        self._listview = wx.ListBox(self._mainpanel, -1, choices=self._viewlist)
        self._listview.SetSelection(0)
        self._listview.Bind(wx.EVT_LISTBOX,lambda evt,widget = self._listview:self.comboboxsl(evt,widget))
        self._newmainsizer = wx.BoxSizer(wx.HORIZONTAL)
        self._newmainsizer.Add(self._listview, 0, wx.EXPAND)
        self._newmainsizer.Add(self._mainsizer, 1, wx.EXPAND)
        self.addview.Layout()
        self._mainpanel.SetSizer(self._newmainsizer)

    def inputexample(self,e):
        pathname = sys.path[0] + "\\mks_picdiy\\"
        self.progressthread = threading.Thread(target=lambda pn=pathname: self.inprogress(pn))
        self.progressthread.setDaemon(True)
        self.progressthread.start()

    def dropCallback(self, txt, pos):
        try:
            # Image.open(txt)
            size = Image.open(txt).size
            listvalue = self._listview.GetSelection()
            value = self.viewcb.GetSelection()
            if listvalue == 0:
                if (size[0] != 480 or size[1] != 320):
                    self.message.SetLabel(u'请放入480x320像素的bmp格式文件')
                    return
            elif listvalue == 11:
                if pos == 0:
                    if (size[0] != 117 or size[1] != 140):
                        self.message.SetLabel(u'请放入117x140像素的bmp格式文件')
                        return
                else:
                    if (size[0] != 117 or size[1] != 92):
                        self.message.SetLabel(u'请放入117x92像素的bmp格式文件')
                        return
            elif listvalue == 12:
                if pos == 0:
                    if (size[0] != 200 or size[1] != 200):
                        self.message.SetLabel(u'请放入200x200像素的bmp格式文件')
                        return
                else:
                    if (size[0] != 150 or size[1] != 80):
                        self.message.SetLabel(u'请放入150x80像素的bmp格式文件')
                        return
            else:
                if (size[0] != 117 or size[1] != 140):
                    self.message.SetLabel(u'请放入117x140像素的bmp格式文件')
                    return
            if self.viewimglist[pos][0] != '':
                if listvalue == 11:
                    self.choosefileimagelist[pos][0] = txt
                    self.allimglistdiy[self.viewpos][:] = self.choosefileimagelist
                    self.choosefilebtnlist[pos].SetBitmap(self.getBitmap(txt, self.gettextlist()[pos]))
                elif listvalue == 12:
                    self.printingimagelist[pos][0] = txt
                    self.allimglistdiy[self.viewpos][:] = self.printingimagelist
                    self.printingbtnlist[pos].SetBitmap(self.getBitmap(txt, self.gettextlist()[pos]))
                else:
                    self.imagelist[pos][0] = txt
                    self.allimglistdiy[self.viewpos][:] = self.imagelist
                    self.btnlist[pos].SetBitmap(self.getBitmap(txt, self.gettextlist()[pos]))
                self.addone.SetBitmap(self.getBitmap(txt, ''))
                self.message.SetLabel(u'导入文件成功')
        except Exception as e:
            return

    def dropOTTCallback(self, txt, pos):
        try:
            # Image.open(txt)
            size = Image.open(txt).size
            listvalue = self._listview.GetSelection()
            value = self.viewcb.GetSelection()
            print(size[0], size[1], value)
            if listvalue == 0:
                if (size[0] != 480 or size[1] != 320):
                    self.message.SetLabel(u'请放入480x320像素的bmp格式文件')
                    return
            elif listvalue == 11:
                if pos == 0:
                    if (size[0] != 117 or size[1] != 140):
                        self.message.SetLabel(u'请放入117x140像素的bmp格式文件')
                        return
                else:
                    if (size[0] != 117 or size[1] != 92):
                        self.message.SetLabel(u'请放入117x92像素的bmp格式文件')
                        return
            elif listvalue == 12:
                if pos == 0:
                    if (size[0] != 200 or size[1] != 200):
                        self.message.SetLabel(u'请放入200x200像素的bmp格式文件')
                        return
                else:
                    if (size[0] != 150 or size[1] != 80):
                        self.message.SetLabel(u'请放入150x80像素的bmp格式文件')
                        return
            else:
                if (size[0] != 117 or size[1] != 140):
                    self.message.SetLabel(u'请放入117x140像素的bmp格式文件')
                    return
            if self.viewimglist[self.selectbtnpos][pos] != '':
                if listvalue == 11:
                    self.choosefileimagelist[self.selectbtnpos][pos] = txt
                    self.allimglistdiy[self.viewpos][:] = self.choosefileimagelist
                    if pos == 0:
                        self.choosefilebtnlist[self.selectbtnpos].SetBitmap(self.getBitmap(txt, self.gettextlist()[self.selectbtnpos]))
                        self.addone.SetBitmap(self.getBitmap(txt, ''))
                    elif pos == 1:
                        self.addtwo.SetBitmap(self.getBitmap(txt, ''))
                    elif pos == 2:
                        self.addthree.SetBitmap(self.getBitmap(txt, ''))
                elif listvalue == 12:
                    self.printingimagelist[self.selectbtnpos][pos] = txt
                    self.allimglistdiy[self.viewpos][:] = self.printingimagelist
                    if pos == 0:
                        self.printingbtnlist[self.selectbtnpos].SetBitmap(self.getBitmap(txt, self.gettextlist()[self.selectbtnpos]))
                        self.addone.SetBitmap(self.getBitmap(txt, ''))
                    elif pos == 1:
                        self.addtwo.SetBitmap(self.getBitmap(txt, ''))
                    elif pos == 2:
                        self.addthree.SetBitmap(self.getBitmap(txt, ''))
                else:
                    self.imagelist[self.selectbtnpos][pos] = txt
                    self.allimglistdiy[self.viewpos][:] = self.imagelist

                    if pos == 0:
                        self.btnlist[self.selectbtnpos].SetBitmap(self.getBitmap(txt, self.gettextlist()[self.selectbtnpos]))
                        self.addone.SetBitmap(self.getBitmap(txt, ''))
                    elif pos == 1:
                        self.addtwo.SetBitmap(self.getBitmap(txt, ''))
                    elif pos == 2:
                        self.addthree.SetBitmap(self.getBitmap(txt, ''))
                self.message.SetLabel(u'导入文件成功')
        except Exception as e:
            return

    def RefreshBitmap(self):
        # self.SetSize((510, 410))

        if self.viewimglist is None:
            self.viewimglist = self.getbinname(self._viewlist[0])
        if self.viewpos == 11:
            list = self.choosefileimagelist
            self.viewimglist = self.getbinname(self._viewlist[11])
        elif self.viewpos == 12:
            list = self.printingimagelist
        else:
            list = self.allimglistdiy[self.viewpos]
        for i in range(0,len(self.viewimglist)):
            if self.viewpos == 0 and list[0][0] is not None:
                self.btlogo.SetBitmap(self.getBitmap(list[0][0], ''))
            elif self.viewimglist[i][0] == '':
                if self.viewpos == 11:
                    self.choosefilebtnlist[i].SetBitmap(self.hnormalbitmap)
                elif self.viewpos == 12:
                    if i < 4:
                        self.printingbtnlist[i].SetBitmap(self.hnormalbitmap)
                else:
                    self.btnlist[i].SetBitmap(self.hnormalbitmap)
            else:
                if i < len(list) and list[i][0] is not None:
                    if self.viewpos == 11:
                        self.choosefilebtnlist[i].SetBitmap(self.getBitmap(list[i][0], self.gettextlist()[i]))
                        self.addone.SetBitmap(self.getBitmap(list[i][0], ''))
                    elif self.viewpos == 12:
                        if i < 4:
                            self.printingbtnlist[i].SetBitmap(self.getBitmap(list[i][0], self.gettextlist()[i]))
                            self.addone.SetBitmap(self.getBitmap(list[i][0], ''))
                    else:
                        self.btnlist[i].SetBitmap(self.getBitmap(list[i][0], self.gettextlist()[i]))
                        self.addone.SetBitmap(self.getBitmap(list[i][0], ''))
                elif list[i][1] is not None:
                    self.addtwo.SetBitmap(self.getBitmap(list[i][1], ''))
                elif list[i][2] is not None:
                    self.addthree.SetBitmap(self.getBitmap(list[i][2], ''))
                else:
                    if self.viewpos == 11:
                        self.choosefilebtnlist[i].SetBitmap(self.normalbitmap)
                    elif self.viewpos == 12:
                        if i < 4:
                            self.printingbtnlist[i].SetBitmap(self.normalbitmap)
                    else:
                        self.btnlist[i].SetBitmap(self.normalbitmap)

    def getLanguage(self):
        result = 'en'
        if not os.path.exists(os.path.abspath('')+'\\l.l'):
            f = open(os.path.abspath('')+'\\l.l','w')
            f.write(result)
            f.close()
        else:
            f = open(os.path.abspath('')+'\\l.l','r')
            content = f.read()
            if content == 'zh_CN':
                result = content
            f.close()
        return result
    def changelanguage(self,e,widget):
        value = widget.GetValue()
        content = 'zh_CN'
        f = open(os.path.abspath('') + '\\l.l', 'w')
        if value == self.languagelist[0]:
            f.write(content)
        elif value == self.languagelist[1]:
            f.write('en')
        f.close()



    def addImage(self,e,pos):
        with wx.FileDialog(self, _(u"选择你的图标文件"),defaultDir=self.selectedpath, wildcard="img files (*.png;*.jpg;)|*.png;*.jpg;",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            pathname = fileDialog.GetPath()
            size = Image.open(pathname).size
            listvalue = self._listview.GetSelection()
            value = self.viewcb.GetSelection()
            if listvalue == 0:
                if (size[0] != 480 or size[1] != 320):
                    self.message.SetLabel(u'请放入480x320像素的bmp格式文件')
                    return
            elif listvalue == 11:
                if self.selectbtnpos == 0:
                    if (size[0] != 117 or size[1] != 140):
                        self.message.SetLabel(u'请放入117x140像素的bmp格式文件')
                        return
                else:
                    if (size[0] != 117 or size[1] != 92):
                        self.message.SetLabel(u'请放入117x92像素的bmp格式文件')
                        return
            elif listvalue == 12:
                if self.selectbtnpos == 0:
                    if (size[0] != 200 or size[1] != 200):
                        self.message.SetLabel(u'请放入200x200像素的bmp格式文件')
                        return
                else:
                    if (size[0] != 150 or size[1] != 80):
                        self.message.SetLabel(u'请放入150x80像素的bmp格式文件')
                        return
            else:
                if (size[0] != 117 or size[1] != 140):
                    self.message.SetLabel(u'请放入117x140像素的bmp格式文件')
                    return
            if listvalue == 11:
                self.choosefileimagelist[self.selectbtnpos][pos] = pathname
                self.allimglistdiy[self.viewpos][:] = self.choosefileimagelist
                self.choosefilebtnlist[self.selectbtnpos].SetBitmap()
            elif listvalue == 12:
                self.printingimagelist[self.selectbtnpos][pos] = pathname
                self.allimglistdiy[self.viewpos][:] = self.printingimagelist
                self.printingbtnlist[self.selectbtnpos].SetBitmap(self.getBitmap(pathname, self.gettextlist()[self.selectbtnpos]))
            else:
                self.imagelist[self.selectbtnpos][pos] = pathname
                self.allimglistdiy[self.viewpos][:] = self.imagelist
                self.btnlist[self.selectbtnpos].SetBitmap(self.getBitmap(pathname, self.gettextlist()[self.selectbtnpos]))
            if pos == 0:
                self.addone.SetBitmap(self.getBitmap(pathname, ''))
            elif pos == 1:
                self.addtwo.SetBitmap(self.getBitmap(pathname, ''))
            elif pos == 2:
                self.addthree.SetBitmap(self.getBitmap(pathname, ''))
            # i = 0
            # for a in self.allimglist:
            #     if len(a)>0:
            #         for b in a:
            #             for c in b:
            #                 if c is not None:
            #                     i+=1
            # self.message.SetLabel(_(u'已添加 ')+str(i)+_(u'张图片'))
            self.selectedpath = fileDialog.GetDirectory()
        e.Skip()

    def showImage(self,e):
        if self.underselectpos == 0 and self.imagelist[self.selectbtnpos][0] is not None:
            self.btnlist[self.selectbtnpos].SetBitmap(self.getBitmap(self.imagelist[self.selectbtnpos][0], ''))
        elif self.underselectpos == 1 and self.imagelist[self.selectbtnpos][1] is not None:
            self.btnlist[self.selectbtnpos].SetBitmap(self.getBitmap(self.imagelist[self.selectbtnpos][1], ''))
        elif self.underselectpos == 2 and self.imagelist[self.selectbtnpos][2] is not None:
            self.btnlist[self.selectbtnpos].SetBitmap(self.getBitmap(self.imagelist[self.selectbtnpos][2], ''))
        if e is not None:
            e.Skip()
    def deleteimg(self,e):
        value = self.viewcb.GetSelection()
        if self.underselectpos == 0:
            self.imagelist[self.selectbtnpos][0] = None
            self.allimglistdiy[self.viewpos][:] = self.imagelist
            self.addone.SetBitmap(self.underbitmap)
        elif self.underselectpos == 1:
            self.imagelist[self.selectbtnpos][1] = None
            self.allimglistdiy[self.viewpos][:] = self.imagelist
            self.addtwo.SetBitmap(self.underbitmap)
        elif self.underselectpos == 2:
            self.imagelist[self.selectbtnpos][2] = None
            self.allimglistdiy[self.viewpos][:] = self.imagelist
            self.addthree.SetBitmap(self.underbitmap)

    def showpopupmenu(self,e,pos):
        menu = wx.Menu()
        # addtt = wx.MenuItem(menu, wx.NewId(), _(u'添加到预览界面'))
        deltt = wx.MenuItem(menu, wx.NewId(), _(u'删除'))
        id = menu.Append(0,_(u'添加到预览界面'))

        self.underselectpos = pos
        # self.Bind(wx.EVT_MENU,self.showImage,addtt)
        # self.Bind(wx.EVT_MENU,self.deleteimg, deltt)
        self.Bind(wx.EVT_MENU,self.showImage,id)
        id = menu.Append(1, _(u'删除'))
        self.Bind(wx.EVT_MENU, self.deleteimg, id)
        self.PopupMenu(menu, self.ScreenToClient(wx.GetMousePosition()))
        menu.Destroy()
        e.Skip()

    def getBitmap(self,filepath, text):
        try:
            bmp = wx.Image(filepath, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
            if text is not '':
                dc = wx.MemoryDC()
                dc.SelectObject(bmp)
                # dc.Clear()
                dc.SetTextForeground((255, 255, 255))
                tw, th = dc.GetTextExtent(text)
                mh = 10
                if self.viewcb.GetSelection() == 1:
                    mh = 25
                dc.DrawText(text, (self._picwidth - tw) / 2, self._picheight - th - mh)
                dc.SelectObject(wx.NullBitmap)
            return bmp
        except Exception as e:
            return self.normalbitmap

    def sizeChange(self,e):
        # .Bind(wx.EVT_TEXT, lambda evt: self.checkisnum(evt, rightpart))
        width = self._picwidth
        height = self._picheight
        if width >= 78 and height>=104:
            # self.SetSize((510, 410))
            self.SetSize()
    def ChangeBitmap(self,e,pos):
        # self.addone.SetBitmap(self.normalbitmap)
        # self.addone.Disable()
        self.selectbtnpos = pos
        self.addone.Enable()
        self.addtwo.Enable()
        self.addthree.Enable()
        self.addone.SetBitmap(self.underbitmap)
        self.addtwo.SetBitmap(self.underbitmap)
        self.addthree.SetBitmap(self.underbitmap)
        if self.viewimglist is None:
            self.viewimglist = self.getbinname(self._viewlist[0])
        if self.viewimglist[pos][0] == '':
            self.addone.Disable()
        else:
            if self.imagelist[pos][0] is not None:
                self.addone.SetBitmap(self.getBitmap(self.imagelist[pos][0], ''))
        if self.viewimglist[pos][1] == '':
            self.addtwo.Disable()
        else:
            if self.imagelist[pos][1] is not None:
                self.addtwo.SetBitmap(self.getBitmap(self.imagelist[pos][1], ''))
        if self.viewimglist[pos][2] == '':
            self.addthree.Disable()
        else:
            if self.imagelist[pos][2] is not None:
                self.addthree.SetBitmap(self.getBitmap(self.imagelist[pos][2], ''))
        if e is not None:
            e.Skip()

    def choosefileChangeBitmap(self,e,pos):
        # self.addone.SetBitmap(self.normalbitmap)
        # self.addone.Disable()
        self.selectbtnpos = pos
        self.addone.Enable()
        self.addtwo.Enable()
        self.addthree.Enable()
        self.addone.SetBitmap(self.underbitmap)
        self.addtwo.SetBitmap(self.underbitmap)
        self.addthree.SetBitmap(self.underbitmap)
        if self.viewimglist is None:
            self.viewimglist = self.getbinname(self._viewlist[11])
        if self.viewimglist[pos][0] == '':
            self.addone.Disable()
        else:
            if self.choosefileimagelist[pos][0] is not None:
                self.addone.SetBitmap(self.getBitmap(self.choosefileimagelist[pos][0], ''))
        if self.viewimglist[pos][1] == '':
            self.addtwo.Disable()
        else:
            if self.choosefileimagelist[pos][1] is not None:
                self.addtwo.SetBitmap(self.getBitmap(self.choosefileimagelist[pos][1], ''))
        if self.viewimglist[pos][2] == '':
            self.addthree.Disable()
        else:
            if self.choosefileimagelist[pos][2] is not None:
                self.addthree.SetBitmap(self.getBitmap(self.choosefileimagelist[pos][2], ''))
        if e is not None:
            e.Skip()
    def printingChangeBitmap(self,e,pos):
        # self.addone.SetBitmap(self.normalbitmap)
        # self.addone.Disable()
        self.selectbtnpos = pos
        self.addone.Enable()
        self.addtwo.Enable()
        self.addthree.Enable()
        self.addone.SetBitmap(self.underbitmap)
        self.addtwo.SetBitmap(self.underbitmap)
        self.addthree.SetBitmap(self.underbitmap)
        if self.viewimglist is None:
            self.viewimglist = self.getbinname(self._viewlist[12])
        if self.viewimglist[pos][0] == '':
            self.addone.Disable()
        else:
            if self.printingimagelist[pos][0] is not None:
                self.addone.SetBitmap(self.getBitmap(self.printingimagelist[pos][0], ''))
        if self.viewimglist[pos][1] == '':
            self.addtwo.Disable()
        else:
            if self.printingimagelist[pos][1] is not None:
                self.addtwo.SetBitmap(self.getBitmap(self.printingimagelist[pos][1], ''))
        if self.viewimglist[pos][2] == '':
            self.addthree.Disable()
        else:
            if self.printingimagelist[pos][2] is not None:
                self.addthree.SetBitmap(self.getBitmap(self.printingimagelist[pos][2], ''))
        if e is not None:
            e.Skip()

    def getStaticBmp(self,parent,bmp,func=None,rfun=None):

        width = int(float(self._picwidth))
        height = int(float(self._picheight))
        staticbitmap = wx.BitmapButton(parent, -1, bitmap=bmp, size=(width, height))
        if func is not None:
            staticbitmap.Bind(wx.EVT_BUTTON, func)
        if rfun is not None:
            staticbitmap.Bind(wx.EVT_RIGHT_UP,rfun)
        return staticbitmap

    def getWHBmp(self,parent,bmp,w,h,func=None,rfun=None):
        staticbitmap = wx.BitmapButton(parent, -1, bitmap=bmp, size=(w, h))
        if func is not None:
            staticbitmap.Bind(wx.EVT_BUTTON, func)
        if rfun is not None:
            staticbitmap.Bind(wx.EVT_RIGHT_UP,rfun)
        return staticbitmap

    def makeImage(self,filename,color,hasX):
        width = int(float(self._picwidth))
        height = int(float(self._picheight))
        image = Image.new('RGB', (width,height ), color)
        if hasX:
            draw = ImageDraw.Draw(image)
            draw.line((10,image.size[1]/2,image.size[0]-10,image.size[1]/2), fill=(255,255,255,255),width=3)
            draw.line((image.size[0]/2, 20, image.size[0]/2, image.size[1]-20), fill=(255,255,255,255),width=3)
        image.save(os.path.abspath('')+'\\'+filename,'png')

    def makeWHImage(self,filename,color,hasX,W,H):
        width = int(float(W))
        height = int(float(H))
        image = Image.new('RGB', (width,height ), color)
        if hasX:
            draw = ImageDraw.Draw(image)
            draw.line((10,image.size[1]/2,image.size[0]-10,image.size[1]/2), fill=(255,255,255,255),width=3)
            draw.line((image.size[0]/2, 20, image.size[0]/2, image.size[1]-20), fill=(255,255,255,255),width=3)
        image.save(os.path.abspath('')+'\\'+filename,'png')

    def comboboxsl(self,evt,widget):
        value = self._listview.GetString(self._listview.GetSelection())
        if self._listview.GetSelection() == 0:
            self.btlogo.Show()
            self.bottompanel.Hide()
            self.choosefilepanel.Hide()
            self.printingpanel.Hide()
        elif self._listview.GetSelection() == 11:
            self.btlogo.Hide()
            self.bottompanel.Hide()
            self.choosefilepanel.Show()
            self.printingpanel.Hide()
        elif self._listview.GetSelection() == 12:
            self.btlogo.Hide()
            self.bottompanel.Hide()
            self.choosefilepanel.Hide()
            self.printingpanel.Show()
        else:
            self.btlogo.Hide()
            self.choosefilepanel.Hide()
            self.bottompanel.Show()
            self.printingpanel.Hide()
        self._mainsizer.Layout()
        self.addsizer.Layout()
        self.addview.Layout()
        self._newmainsizer.Layout()
        self.viewimglist = self.getbinname(value)
        self.RefreshBitmap()
        evt.Skip()

    def pixelchange(self, evt, widget):
        if self.progressing:
            return
        if len(self._pixellist) > 0:
            self._picwidth = self._pixellist[0][2]
            self._picheight = self._pixellist[0][3]
            self.btlogo.SetSize((self._pixellist[0][0], self._pixellist[0][1]))
            for i in range(len(self.btnlist)):
                self.btnlist[i].SetSize((self._picwidth, self._picheight))
                self.btnlist[i].SetMinSize((self._picwidth, self._picheight))
                self.btnlist[i].SetMaxSize((self._picwidth, self._picheight))
            for i in range(len(self.choosefilebtnlist)):
                if i > 5:
                    self.choosefilebtnlist[i].SetSize((117, 92))
                    self.choosefilebtnlist[i].SetMinSize((117, 92))
                    self.choosefilebtnlist[i].SetMaxSize((117, 92))
                else:
                    self.choosefilebtnlist[i].SetSize((self._picwidth, self._picheight))
                    self.choosefilebtnlist[i].SetMinSize((self._picwidth, self._picheight))
                    self.choosefilebtnlist[i].SetMaxSize((self._picwidth, self._picheight))
            self.makeImage('bai.png', '#ffffff', False)
            self.makeImage('hei.png', '#000000', False)
            self.normalbitmap = wx.Image(os.path.abspath("") + "\\bai.png", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
            self.hnormalbitmap = wx.Image(os.path.abspath("") + "\\hei.png", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.btsizer.Layout()
        self.bbsizer.Layout()
        self.cfleftbotsizer.Layout()
        self.cflefttopsizer.Layout()
        self.cfleftsizer.Layout()
        self.cfrightsizer.Layout()
        self.cfsizer.Layout()
        self._mainsizer.Layout()
        self.addsizer.Layout()
        self.addview.Layout()
        self._newmainsizer.Layout()
        self.RefreshBitmap()
        # evt.Skip()

    def showConfigDialog(self, e):
        locale = wx.Locale(wx.LANGUAGE_ENGLISH)
        locale.AddCatalogLookupPathPrefix('locale')
        self.languagename = self.getLanguage()
        ibRet = locale.AddCatalog(self.languagename)
        self.widgetlist[:] = []
        if self._mdialog:
            self._mdialog.Hide()
        self._mdialog = wx.Dialog(self, -1, _(u'配置文件'), style=wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        self.isMax = False
        # self._mdialog.Bind(wx.EVT_SPLITTER_DOUBLECLICKED, self.OnDoubleClick())
        panel = wx.ScrolledWindow(self._mdialog, -1)
        panelsizer = wx.BoxSizer(wx.VERTICAL)
        totalheight = 1
        count = -1
        for mlist in self.configdt:
            ## 0标题 1选项 2类型 3导出名 4提示 5默认值
            tv = wx.StaticText(panel, -1, mlist[0])
            eachsizer = wx.BoxSizer(wx.HORIZONTAL)
            eachsizer.Add(tv, 1, wx.EXPAND)
            count += 1
            if mlist[2] == 'choose':
                indexi = 0
                for i in range(len(mlist[1])):
                    if str(mlist[1][i][:mlist[1][i].find(':')]) == str(mlist[5]):
                        indexi = i
                        break
                mwidget = wx.ComboBox(panel, -1, value=mlist[1][indexi], choices=mlist[1], style=wx.CB_READONLY)
                mwidget.SetName(mlist[3])
                mwidget.Bind(wx.EVT_COMBOBOX,lambda evt,widget=mwidget:self.cbchange(evt,widget))
                mwidget.SetToolTipString(mlist[0] if mlist[4] == '' else mlist[4])
                totalheight = totalheight+mwidget.GetSize()[1]+6
                eachsizer.Add(mwidget, 1, wx.EXPAND)
                # self.widgetlist.append(mwidget)
            elif mlist[2] == 'edit':
                # for defaultvalue in mlist[5]:
                valida = MyNumberValidator(mlist[6], self, count)
                mwidget = wx.TextCtrl(panel, -1, validator=valida)
                mwidget.SetName(mlist[3])
                mwidget.SetLabelText(str(mlist[5]))
                # if mlist[6] == 'type1':
                #     tips = u':范围为-999~99999'
                # elif mlist[6] == 'type2':
                #     tips = u':范围为0~99999'
                # else:
                #     tips = u''
                mwidget.SetToolTipString((mlist[0] if mlist[4] == '' else mlist[4]))
                mwidget.Bind(wx.EVT_TEXT,lambda evt,widget=mwidget,vali=valida:self.edchange(evt,widget,vali))
                totalheight = totalheight + mwidget.GetSize()[1] + 6
                eachsizer.Add(mwidget, 1, wx.EXPAND)
                # self.widgetlist.append(mwidget)
            panelsizer.AddSizer(eachsizer, 0, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=3)
        panel.SetScrollbars(15, 15, 1000, totalheight)
        panel.SetSizer(panelsizer)
        btnyes = wx.Button(self._mdialog, -1, _(u'导出配置文件'))
        btnyes.Bind(wx.EVT_BUTTON, self.outputConfig)
        btnimport = wx.Button(self._mdialog, -1, _(u'导入配置文件'))
        btnimport.Bind(wx.EVT_BUTTON,self.importConfig)
        btnsizer = wx.BoxSizer(wx.HORIZONTAL)
        btnsizer.Add(btnyes, 1, wx.ALIGN_CENTER)
        btnsizer.Add(btnimport, 1, wx.ALIGN_CENTER)
        mdsizer = wx.BoxSizer(wx.VERTICAL)
        mdsizer.Add(panel, 1, wx.EXPAND)
        mdsizer.AddSizer(btnsizer, 0, wx.EXPAND)
        self._mdialog.SetSizer(mdsizer)
        self._mdialog.SetMinSize((580, 600))
        self._mdialog.SetSize((580,600))
        self._mdialog.Show()

    def cbchange(self, e, widget):
        for i in range(len(self.configdt)):
            if widget.GetName() == self.configdt[i][3]:
                self.configdt[i][5] = widget.GetStringSelection()[:widget.GetStringSelection().find(':')]
                break

    def edchange(self, e, widget, vali):
        for i in range(len(self.configdt)):
            if widget.GetName() == self.configdt[i][3]:
                self.configdt[i][5] = widget.GetValue()
                vali.value = self.configdt[i][5]
                break
    def getValue(self,id):
        print 'getValue'
        print self.configdt[id][5]
        return self.configdt[id][5]

    def outputConfig(self, e):
        filename = "robin_nano35_cfg.txt"
        with wx.FileDialog(self, _(u"选择你的配置文件"),defaultDir=self.selectedpath,defaultFile=filename, wildcard="txt file (*.*)|*.*",
                           style=wx.SAVE) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            pathname = fileDialog.GetPath()
            configfile = open(pathname, 'w')
            for i in range(len(self.configdt)):
                configfile.write(str(self.configdt[i][3])+' ' +str(self.configdt[i][5])+ '    #' + self.configdt[i][4].encode(sys.getfilesystemencoding())+'\r\n')
            # for mlist in self.configdt:
            #     configfile.write(str(mlist[3])+' ' +str(mlist[5])+ '    #' + mlist[4].encode(sys.getfilesystemencoding())+'\r\n')
            configfile.close()
        self._mdialog.Hide()

    def importConfig(self, e):
        with wx.FileDialog(self, _(u"选择你的配置文件"),defaultDir=self.selectedpath, wildcard="txt file (*.*)|*.*",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            pathname = fileDialog.GetPath()
            configfile = open(pathname, 'r')
            configline = configfile.readline()
            while configline:
                for i in range(len(self.configdt)):
                    if self.configdt[i][3] in configline:
                        endpos = len(configline)
                        if configline.rfind("#") != -1:
                            endpos = configline.rfind('#')
                        self.configdt[i][5] = configline[configline.find(self.configdt[i][3])+len(self.configdt[i][3]):endpos].replace('\t', '').replace(' ', '')
                        break
                configline = configfile.readline()
            configfile.close()
        self.showConfigDialog(None)


    def exportbin(self,e):
        with wx.DirDialog(self, _(u"选择保存的文件夹"),style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dirDialog:

            if dirDialog.ShowModal() == wx.ID_CANCEL:
                return
            pathname = dirDialog.GetPath()
            # self.message.SetLabel(_(u'正在导出bin文件，请不要关闭'))
            self.progressthread = threading.Thread(target=lambda pn=pathname: self.progress(pn))
            self.progressthread.setDaemon(True)
            self.progressthread.start()
        e.Skip()

    def inputbin(self, e):
        with wx.DirDialog(self, _(u"选择导入的文件夹"),style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dirDialog:

            if dirDialog.ShowModal() == wx.ID_CANCEL:
                return
            pathname = dirDialog.GetPath()
            self.progressthread = threading.Thread(target=lambda pn=pathname: self.inprogress(pn))
            self.progressthread.setDaemon(True)
            self.progressthread.start()
        e.Skip()

    def inprogress(self, pathname):
        value = self.viewcb.GetSelection()
        locale = wx.Locale(wx.LANGUAGE_ENGLISH)
        locale.AddCatalogLookupPathPrefix('locale')
        self.languagename = self.getLanguage()
        ibRet = locale.AddCatalog(self.languagename)
        self.progressing = True
        try:
            filelist = os.listdir(pathname)
            temppos = self.viewpos
            temppath = sys.path[0] + "\\tempimgdiy\\"
            if os.path.exists(temppath):
                shutil.rmtree(temppath)
            os.mkdir(temppath)
            self.message.SetLabel(_(u'正在导入bin文件夹'))
            fid = 0
            for f in filelist:
                self.bin2image(pathname + "\\" + f, f[:-4])
                self.message.SetLabel(_(u'已导入:') + str(fid) + "/" + str(len(filelist)))
                fid = fid + 1
            self.message.SetLabel(_(u'正在加载图片'))
            for v in range(len(self._viewlist)):
                result = self.rgetbinname(self._viewlist[v])
                if v == 11:
                    self.choosefileimagelist = [[None, None, None], [None, None, None], [None, None, None], [None, None, None],[None, None, None], [None, None, None], [None, None, None], [None, None, None], [None, None, None]]
                    for r in range(len(result)):
                        if result[r][0] is not '' and os.path.exists(temppath + result[r][0].replace('.bin', '.png')):
                            self.choosefileimagelist[r][0] = temppath + result[r][0].replace('.bin', '.png')
                        if result[r][1] is not '' and os.path.exists(temppath + result[r][1].replace('.bin', '.png')):
                            self.choosefileimagelist[r][1] = temppath + result[r][1].replace('.bin', '.png')
                        if result[r][2] is not '' and os.path.exists(temppath + result[r][2].replace('.bin', '.png')):
                            self.choosefileimagelist[r][2] = temppath + result[r][2].replace('.bin', '.png')
                    self.allimglistdiy[v][:] = self.choosefileimagelist
                    self.choosefileimagelist[:] = self.allimglistdiy[self.viewpos]
                elif v == 12:
                    self.printingimagelist = [[None, None, None], [None, None, None], [None, None, None],[None, None, None]]
                    for r in range(len(result)):
                        if r < 4:
                            if result[r][0] is not '' and os.path.exists(temppath + result[r][0].replace('.bin', '.png')):
                                self.printingimagelist[r][0] = temppath + result[r][0].replace('.bin', '.png')
                            if result[r][1] is not '' and os.path.exists(temppath + result[r][1].replace('.bin', '.png')):
                                self.printingimagelist[r][1] = temppath + result[r][1].replace('.bin', '.png')
                            if result[r][2] is not '' and os.path.exists(temppath + result[r][2].replace('.bin', '.png')):
                                self.printingimagelist[r][2] = temppath + result[r][2].replace('.bin', '.png')
                    self.allimglistdiy[v][:] = self.printingimagelist
                    self.printingimagelist[:] = self.allimglistdiy[self.viewpos]
                else:
                    self.imagelist = [[None, None, None], [None, None, None], [None, None, None], [None, None, None],
                              [None, None, None], [None, None, None], [None, None, None], [None, None, None]]
                    for r in range(len(result)):
                        if result[r][0] is not '' and os.path.exists(temppath + result[r][0].replace('.bin', '.png')):
                            self.imagelist[r][0] = temppath + result[r][0].replace('.bin', '.png')
                        if result[r][1] is not '' and os.path.exists(temppath + result[r][1].replace('.bin', '.png')):
                            self.imagelist[r][1] = temppath + result[r][1].replace('.bin', '.png')
                        if result[r][2] is not '' and os.path.exists(temppath + result[r][2].replace('.bin', '.png')):
                            self.imagelist[r][2] = temppath + result[r][2].replace('.bin', '.png')

                    self.allimglistdiy[v][:] = self.imagelist
                    self.imagelist[:] = self.allimglistdiy[self.viewpos]

            self.viewpos = temppos
            self.RefreshBitmap()
            self.message.SetLabel(_(u'已完成导入'))
            self.progressing = False
        except Exception as e:
            self.progressing = False
    def progress(self,pathname):
        q = 0
        for i in range(0, len(self.allimglistdiy)):
            if len(self.allimglistdiy[i]) > 0:
                namelist = self.getbinname(self._viewlist[i])
                for j in range(0, len(self.allimglistdiy[i])):
                    for k in range(0, len(self.allimglistdiy[i][j])):
                        if self.allimglistdiy[i][j][k] is not None:
                            q += 1
                            self.image2bin(Image.open(self.allimglistdiy[i][j][k]), pathname + '\\' + namelist[j][k])
                            self.message.SetLabel(_(u'已导出') + str(q) + _(u'个bin文件'))

        self.message.SetLabel(_(u'已完成导出，可以关闭'))

    def rgetbinname(self, value):
        result = []
        # 0_(u'准备打印'), 1_(u'预热'), 2_(u'挤出'), 3_(u'移动'), 4_(u'回零'), 5_(u'调平'), 6_(u'设置'), 7_(u'风扇'),
        # 8_(u'换料'),9 _(u'文件系统'), 10_(u'更多'), 11_(u'选择文件'), 12_(u'正在打印'), 13_(u'操作'), 14_(u'暂停'), 15_(u'变速'), 16_(u'更多（打印中）'),17_(u'语言')
        # 18_(u'WIFI')
        if value == self._viewlist[0]:
            self.viewpos = 0
            result = [['bmp_logo.bin', '', ''], ['', '', ''], ['', '', ''],
                      ['', '', '']
                , ['', '', ''], ['', '', ''],
                      ['', '', ''], ['', '', '']]
        elif value == self._viewlist[1]:
            self.viewpos = 1
            result = [['bmp_preHeat.bin', '', ''], ['bmp_extruct.bin', '', ''], ['bmp_mov.bin', '', ''],
                      ['bmp_zero.bin', '', '']
                , ['bmp_leveling.bin', 'bmp_autoleveling.bin', ''], ['bmp_filamentchange.bin', '', ''],
                      ['bmp_more.bin', '', ''], ['bmp_return.bin', '', '']]
        elif value == self._viewlist[2]:
            self.viewpos = 2
            result = [['bmp_Add.bin', '', ''], ['', '', ''], ['', '', ''], ['bmp_Dec.bin', '', ''],
                      ['bmp_bed.bin', 'bmp_extru1.bin', 'bmp_extru2.bin']
                , ['bmp_step1_degree.bin', 'bmp_step5_degree.bin', 'bmp_step10_degree.bin'], ['bmp_speed0.bin', '', ''],
                      ['bmp_return.bin', '', '']]
        elif value == self._viewlist[3]:
            self.viewpos = 3
            result = [['bmp_in.bin', '', ''], ['', '', ''], ['', '', ''], ['bmp_out.bin', '', ''],
                      ['bmp_extru1.bin', 'bmp_extru2.bin', '']
                , ['bmp_step1_mm.bin', 'bmp_step5_mm.bin', 'bmp_step10_mm.bin'],
                      ['bmp_speed_slow.bin', 'bmp_speed_normal.bin', 'bmp_speed_high.bin'], ['bmp_return.bin', '', '']]
        elif value == self._viewlist[4]:
            self.viewpos = 4
            result = [['bmp_xAdd.bin', '', ''], ['bmp_yAdd.bin', '', ''], ['bmp_zAdd.bin', '', ''],
                      ['bmp_step_move0_1.bin', 'bmp_step_move1.bin', 'bmp_step_move10.bin'], ['bmp_xDec.bin', '', ''],
                      ['bmp_yDec.bin', '', ''], ['bmp_zDec.bin', '', ''], ['bmp_return.bin', '', '']]
        elif value == self._viewlist[5]:
            self.viewpos = 5
            result = [['bmp_zero.bin', '', ''], ['bmp_zeroX.bin', '', ''], ['bmp_zeroY.bin', '', ''],
                      ['bmp_zeroZ.bin', '', ''], ['bmp_function1.bin', '', ''], ['', '', ''], ['', '', ''], ['bmp_return.bin', '', '']]
        elif value == self._viewlist[6]:
            self.viewpos = 6
            result = [['bmp_leveling1.bin', '', ''], ['bmp_leveling2.bin', '', ''], ['bmp_leveling3.bin', '', ''],
                      ['bmp_leveling4.bin', '', '']
                , ['bmp_leveling5.bin', '', ''], ['', '', ''], ['', '', ''], ['bmp_return.bin', '', '']]
        elif value == self._viewlist[7]:
            self.viewpos = 7
            result = [['bmp_wifi.bin ', '', ''], ['bmp_fan.bin', '', ''], ['bmp_about.bin  ', '', ''],
                      ['bmp_breakpoint.bin', '', '']
                , ['bmp_machine_para.bin', '', ''], ['bmp_function1.bin', '', ''], ['bmp_language.bin', '', ''],
                      ['bmp_return.bin', '', '']]
        elif value == self._viewlist[8]:
            self.viewpos = 8
            result = [['bmp_Add.bin', '', ''], ['', '', ''], ['', '', ''], ['bmp_Dec.bin', '', ''],
                      ['bmp_speed255.bin', '', '']
                , ['bmp_speed127.bin', '', ''], ['bmp_speed0.bin', '', ''], ['bmp_return.bin', '', '']]
        elif value == self._viewlist[9]:
            self.viewpos = 9
            result = [['bmp_in.bin', '', ''], ['', '', ''], ['', '', ''], ['bmp_out.bin', '', ''],
                      ['bmp_extru1.bin', 'bmp_extru2.bin', '']
                , ['', '', ''],
                      ['', '', ''], ['bmp_return.bin', '', '']]
        elif value == self._viewlist[10]:
            self.viewpos = 10
            result = [['bmp_custom1.bin', '', ''], ['bmp_custom2.bin', '', ''], ['bmp_custom3.bin', '', ''],
                      ['bmp_custom4.bin', '', '']
                , ['bmp_custom5.bin', '', ''], ['bmp_custom6.bin', '', ''], ['bmp_custom7.bin', '', ''],
                      ['bmp_return.bin', '', '']]
        elif value == self._viewlist[11]:
            self.viewpos = 11
            result = [['bmp_file.bin', 'bmp_dir.bin', ''], ['', '', ''], ['', '', ''], ['', '', ''], ['', '', ''],
                          ['', '', ''], ['bmp_pageUp.bin', '', ''], ['bmp_pageDown.bin', '', ''], ['bmp_back.bin', '', '']]
        elif value == self._viewlist[12]:
            self.viewpos = 12
            result = [['bmp_preview.bin', '', ''], ['bmp_pause.bin', 'bmp_resume.bin', ''], ['bmp_stop.bin', '', ''], ['bmp_operate.bin', 'bmp_printing_back.bin', '']]
        elif value == self._viewlist[13]:
            self.viewpos = 13
            result = [['bmp_temp.bin', '', ''], ['bmp_fan.bin', '', ''], ['bmp_filamentchange.bin', '', ''], ['bmp_speed.bin', '', ''],
                      ['bmp_more.bin', '', '']
                , ['bmp_manual_off.bin', '', ''], ['', '', ''], ['bmp_return.bin', '', '']]
        elif value == self._viewlist[14]:
            self.viewpos = 14
            result = [['bmp_temp.bin', '', ''], ['bmp_fan.bin', '', ''], ['bmp_filamentchange.bin', '', ''],
                      ['bmp_extruct.bin', '', ''],
                      ['bmp_mov.bin', '', ''], ['bmp_more.bin', '', ''], ['bmp_manual_off.bin', '', ''],
                      ['bmp_return.bin', '', '']]
        elif value == self._viewlist[15]:
            self.viewpos = 15
            result = [['bmp_Add.bin', '', ''], ['', '', ''], ['', '', ''], ['bmp_Dec.bin', '', ''],
                      ['bmp_mov_changeSpeed.bin', 'bmp_mov_sel.bin', ''], ['bmp_speed_extruct.bin', 'bmp_extruct_sel.bin', '']
                , ['bmp_step1_percent.bin', 'bmp_step5_percent.bin', 'bmp_step10_percent.bin'], ['bmp_return.bin', '', '']]
        elif value == self._viewlist[16]:
            self.viewpos = 16
            result = [['', '', ''], ['', '', ''],
                      ['', '', ''], ['', '', '']
                , ['', '', ''], ['', '', ''], ['', '', ''],
                      ['bmp_return.bin', '', '']]
        elif value == self._viewlist[17]:
            self.viewpos = 17
            result = [['bmp_simplified_cn.bin', 'bmp_simplified_cn_sel.bin', ''],
                      ['bmp_traditional_cn.bin', 'bmp_traditional_cn_sel.bin', ''],
                      ['bmp_english.bin', 'bmp_english_sel.bin', ''],
                      ['bmp_russian.bin', 'bmp_russian_sel.bin', ''], ['bmp_spanish.bin', 'bmp_spanish_sel.bin', ''],
                      ['bmp_french.bin', 'bmp_french_sel.bin', ''],
                      ['bmp_italy.bin', 'bmp_italy_sel.bin', ''], ['bmp_return.bin', '', '']]
        elif value == self._viewlist[18]:
            self.viewpos = 18
            result = [['', '', ''], ['', '', ''], ['', '', ''],
                      ['', '', ''], ['', '', ''], ['', '', ''], ['bmp_wifi.bin', '', ''], ['bmp_return.bin', '', '']]
        elif value == self._viewlist[19]:
            self.viewpos = 19
            result = [['bmp_tool.bin', '', ''], ['bmp_set.bin', '', ''], ['bmp_printing.bin', '', ''],
                      ['', '', ''], ['', '', ''], ['', '', ''], ['', '', ''], ['', '', '']]
        elif value == self._viewlist[20]:
            self.viewpos = 20
            result = [['bmp_MachineSetting.bin', '', ''], ['bmp_TemperatureSetting.bin', '', ''], ['bmp_MotorSetting.bin', '', ''],
                      ['bmp_AdvanceSetting.bin', '', ''], ['', '', ''], ['', '', ''], ['', '', ''], ['bmp_return.bin', '', '']]

        if len(self.allimglistdiy[self.viewpos]) == 0:
            if self.viewpos == 11:
                self.choosefileimagelist = [[None, None, None], [None, None, None], [None, None, None],
                                            [None, None, None], [None, None, None], [None, None, None],
                                            [None, None, None], [None, None, None], [None, None, None]]
                self.allimglistdiy[self.viewpos][:] = self.choosefileimagelist
            elif self.viewpos == 12:
                self.printingimagelist = [[None, None, None], [None, None, None], [None, None, None],
                                          [None, None, None]]
                self.allimglistdiy[self.viewpos][:] = self.printingimagelist
            else:
                self.imagelist = [[None, None, None], [None, None, None], [None, None, None], [None, None, None],
                                  [None, None, None], [None, None, None], [None, None, None], [None, None, None]]
                self.allimglistdiy[self.viewpos][:] = self.imagelist

        else:
            if self.viewpos == 12:
                self.choosefileimagelist = self.allimglistdiy[self.viewpos]
            elif self.viewpos == 13:
                self.printingimagelist = self.allimglistdiy[self.viewpos]
            else:
                self.imagelist = self.allimglistdiy[self.viewpos]
        return result

    def getbinname(self,value):
        result = []
        # 0_(u'工具'), 1_(u'预热'), 2_(u'挤出'), 3_(u'移动'), 4_(u'回零'), 5_(u'调平'), 6_(u'设置'), 7_(u'风扇'),
        # 8_(u'换料'),9 _(u'文件系统'), 10_(u'更多'), 11_(u'选择文件'), 12_(u'正在打印'), 13_(u'操作'), 14_(u'暂停'), 15_(u'变速'), 16_(u'更多（打印中）'),17_(u'语言')
        #18_(u'WIFI'), 19_准备打印, 20机器参数
        if value == self._viewlist[0]:
            self.viewpos = 0
            result = [['bmp_logo.bin', '', ''], ['', '', ''], ['', '', ''],
                      ['', '', '']
                , ['', '', ''], ['', '', ''],
                      ['', '', ''], ['', '', '']]
        elif value == self._viewlist[1]:
            self.viewpos = 1
            result = [['bmp_preHeat.bin', '', ''], ['bmp_extruct.bin', '', ''], ['bmp_mov.bin', '', ''],
                      ['bmp_zero.bin', '', '']
                , ['bmp_leveling.bin', 'bmp_autoleveling.bin', ''], ['bmp_filamentchange.bin', '', ''],
                      ['bmp_more.bin', '', ''], ['bmp_return.bin', '', '']]
        elif value == self._viewlist[2]:
            self.viewpos = 2
            result = [['bmp_Add.bin', '', ''], ['', '', ''], ['', '', ''], ['bmp_Dec.bin', '', ''],
                      ['bmp_bed.bin', 'bmp_extru1.bin', 'bmp_extru2.bin']
                , ['bmp_step1_degree.bin', 'bmp_step5_degree.bin', 'bmp_step10_degree.bin'], ['bmp_speed0.bin', '', ''],
                      ['bmp_return.bin', '', '']]
        elif value == self._viewlist[3]:
            self.viewpos = 3
            result = [['bmp_in.bin', '', ''], ['', '', ''], ['', '', ''], ['bmp_out.bin', '', ''],
                      ['bmp_extru1.bin', 'bmp_extru2.bin', '']
                , ['bmp_step1_mm.bin', 'bmp_step5_mm.bin', 'bmp_step10_mm.bin'],
                      ['bmp_speed_slow.bin', 'bmp_speed_normal.bin', 'bmp_speed_high.bin'], ['bmp_return.bin', '', '']]
        elif value == self._viewlist[4]:
            self.viewpos = 4
            result = [['bmp_xAdd.bin', '', ''], ['bmp_yAdd.bin', '', ''], ['bmp_zAdd.bin', '', ''],
                      ['bmp_step_move0_1.bin', 'bmp_step_move1.bin', 'bmp_step_move10.bin'], ['bmp_xDec.bin', '', ''],
                      ['bmp_yDec.bin', '', ''], ['bmp_zDec.bin', '', ''], ['bmp_return.bin', '', '']]
        elif value == self._viewlist[5]:
            self.viewpos = 5
            result = [['bmp_zero.bin', '', ''], ['bmp_zeroX.bin', '', ''], ['bmp_zeroY.bin', '', ''],
                      ['bmp_zeroZ.bin', '', ''], ['bmp_function1.bin', '', ''], ['', '', ''], ['', '', ''], ['bmp_return.bin', '', '']]
        elif value == self._viewlist[6]:
            self.viewpos = 6
            result = [['bmp_leveling1.bin', '', ''], ['bmp_leveling2.bin', '', ''], ['bmp_leveling3.bin', '', ''],
                      ['bmp_leveling4.bin', '', '']
                , ['bmp_leveling5.bin', '', ''], ['', '', ''], ['', '', ''], ['bmp_return.bin', '', '']]
        elif value == self._viewlist[7]:
            self.viewpos = 7
            result = [['bmp_wifi.bin ', '', ''], ['bmp_fan.bin', '', ''], ['bmp_about.bin  ', '', ''],
                      ['bmp_breakpoint.bin', '', '']
                , ['bmp_machine_para.bin', '', ''], ['bmp_function1.bin', '', ''], ['bmp_language.bin', '', ''],
                      ['bmp_return.bin', '', '']]
        elif value == self._viewlist[8]:
            self.viewpos = 8
            result = [['bmp_Add.bin', '', ''], ['', '', ''], ['', '', ''], ['bmp_Dec.bin', '', ''],
                      ['bmp_speed255.bin', '', '']
                , ['bmp_speed127.bin', '', ''], ['bmp_speed0.bin', '', ''], ['bmp_return.bin', '', '']]
        elif value == self._viewlist[9]:
            self.viewpos = 9
            result = [['bmp_in.bin', '', ''], ['', '', ''], ['', '', ''], ['bmp_out.bin', '', ''],
                      ['bmp_extru1.bin', 'bmp_extru2.bin', '']
                , ['', '', ''],
                      ['', '', ''], ['bmp_return.bin', '', '']]
        elif value == self._viewlist[10]:
            self.viewpos = 10
            result = [['bmp_custom1.bin', '', ''], ['bmp_custom2.bin', '', ''], ['bmp_custom3.bin', '', ''],
                      ['bmp_custom4.bin', '', '']
                , ['bmp_custom5.bin', '', ''], ['bmp_custom6.bin', '', ''], ['bmp_custom7.bin', '', ''],
                      ['bmp_return.bin', '', '']]
        elif value == self._viewlist[11]:
            self.viewpos = 11
            result = [['bmp_file.bin', 'bmp_dir.bin', ''], ['', '', ''], ['', '', ''], ['', '', ''], ['', '', ''],
                          ['', '', ''], ['bmp_pageUp.bin', '', ''], ['bmp_pageDown.bin', '', ''], ['bmp_back.bin', '', '']]
        elif value == self._viewlist[12]:
            self.viewpos = 12
            result = [['bmp_preview.bin', '', ''], ['bmp_pause.bin', 'bmp_resume.bin', ''], ['bmp_stop.bin', '', ''], ['bmp_operate.bin', 'bmp_printing_back.bin', '']]
        elif value == self._viewlist[13]:
            self.viewpos = 13
            result = [['bmp_temp.bin', '', ''], ['bmp_fan.bin', '', ''], ['bmp_filamentchange.bin', '', ''], ['bmp_speed.bin', '', ''],
                      ['bmp_more.bin', '', '']
                , ['bmp_manual_off.bin', '', ''], ['', '', ''], ['bmp_return.bin', '', '']]
        elif value == self._viewlist[14]:
            self.viewpos = 14
            result = [['bmp_temp.bin', '', ''], ['bmp_fan.bin', '', ''], ['bmp_filamentchange.bin', '', ''], ['bmp_extruct.bin', '', ''],
                      ['bmp_mov.bin', '', ''], ['bmp_more.bin', '', ''], ['bmp_manual_off.bin', '', ''], ['bmp_return.bin', '', '']]
        elif value == self._viewlist[15]:
            self.viewpos = 15
            result = [['bmp_Add.bin', '', ''], ['', '', ''], ['', '', ''], ['bmp_Dec.bin', '', ''],
                      ['bmp_mov.bin', 'bmp_mov_sel.bin', ''], ['bmp_extruct.bin', 'bmp_extruct_sel.bin', '']
                , ['bmp_step1_mm.bin', 'bmp_step5_mm.bin', 'bmp_step10_mm.bin'], ['bmp_return.bin', '', '']]
        elif value == self._viewlist[16]:
            self.viewpos = 16
            result = [['', '', ''], ['', '', ''],
                      ['', '', ''], ['', '', '']
                , ['', '', ''], ['', '', ''], ['', '', ''],
                      ['bmp_return.bin', '', '']]
        elif value == self._viewlist[17]:
            self.viewpos = 17
            result = [['bmp_simplified_cn.bin', 'bmp_simplified_cn_sel.bin', ''],
                      ['bmp_traditional_cn.bin', 'bmp_traditional_cn_sel.bin', ''],
                      ['bmp_english.bin', 'bmp_english_sel.bin', ''],
                      ['bmp_russian.bin', 'bmp_russian_sel.bin', ''], ['bmp_spanish.bin', 'bmp_spanish_sel.bin', ''],
                      ['bmp_french.bin', 'bmp_french_sel.bin', ''],
                      ['bmp_italy.bin', 'bmp_italy_sel.bin', ''], ['bmp_return.bin', '', '']]
        elif value == self._viewlist[18]:
            self.viewpos = 18
            result = [['', '', ''], ['', '', ''], ['', '', ''],
                      ['', '', ''], ['', '', ''], ['', '', ''], ['bmp_wifi.bin', '', ''], ['bmp_return.bin', '', '']]
        elif value == self._viewlist[19]:
            self.viewpos = 19
            result = [['bmp_tool.bin', '', ''], ['bmp_set.bin', '', ''], ['bmp_printing.bin', '', ''],
                      ['', '', ''], ['', '', ''], ['', '', ''], ['', '', ''], ['', '', '']]
        elif value == self._viewlist[20]:
            self.viewpos = 20
            result = [['bmp_MachineSetting.bin', '', ''], ['bmp_TemperatureSetting.bin', '', ''], ['bmp_MotorSetting.bin', '', ''],
                      ['bmp_AdvanceSetting.bin', '', ''], ['', '', ''], ['', '', ''], ['', '', ''], ['bmp_return.bin', '', '']]
        if len(self.allimglistdiy[self.viewpos]) == 0:
            if self.viewpos == 11:
                self.choosefileimagelist = [[None, None, None], [None, None, None], [None, None, None],
                                            [None, None, None], [None, None, None], [None, None, None],
                                            [None, None, None], [None, None, None], [None, None, None]]
                self.allimglistdiy[self.viewpos][:] = self.choosefileimagelist
            elif self.viewpos == 12:
                self.printingimagelist = [[None, None, None], [None, None, None], [None, None, None],
                                          [None, None, None]]
                self.allimglistdiy[self.viewpos][:] = self.printingimagelist
            else:
                self.imagelist = [[None, None, None], [None, None, None], [None, None, None], [None, None, None],
                                  [None, None, None], [None, None, None], [None, None, None], [None, None, None]]
                self.allimglistdiy[self.viewpos][:] = self.imagelist
        else:
            if self.viewpos == 11:
                self.choosefileimagelist = self.allimglistdiy[self.viewpos]
            elif self.viewpos == 12:
                self.printingimagelist = self.allimglistdiy[self.viewpos]
            else:
                self.imagelist = self.allimglistdiy[self.viewpos]
        self.addone.SetBitmap(self.underbitmap)
        self.addtwo.SetBitmap(self.underbitmap)
        self.addthree.SetBitmap(self.underbitmap)
        return result

    def gettextlist(self):
        locale = wx.Locale(wx.LANGUAGE_ENGLISH)
        locale.AddCatalogLookupPathPrefix('locale')
        self.languagename = self.getLanguage()
        ibRet = locale.AddCatalog(self.languagename)
        if self.viewpos == 0:
            return ['', '', '', '', '', '', '', '']
        elif self.viewpos == 1:
            return [_(u'预热'), _(u'挤出'), _(u'移动'), _(u'回零'), _(u'调平'), _(u'换料'), _(u'更多'), _(u'返回')]
        elif self.viewpos == 2:
            return [_(u'增加'), _(u''), _(u''), _(u'减少'), _(u'热床'), _(u'1℃'), _(u'关闭'), _(u'返回')]
        elif self.viewpos == 3:
            return [_(u'进料'), _(u''), _(u''), _(u'退料'), _(u'喷头1'), _(u'5mm'), _(u'低速'), _(u'返回')]
        elif self.viewpos == 4:
            return [_(u'X+'), _(u'Y+'), _(u'Z+'), _(u'1mm'), _(u'X-'), _(u'Y-'), _(u'Z-'), _(u'返回')]
        elif self.viewpos == 5:
            return [_(u'All'), _(u'X'), _(u'Y'), _(u'Z'), _(u'关闭电机'), _(u''), _(u''), _(u'返回')]
        elif self.viewpos == 6:
            return [_(u'第一点'), _(u'第二点'), _(u'第三点'), _(u'第四点'), _(u'第五点'), _(u''), _(u''), _(u'返回')]
        elif self.viewpos == 7:
            return [_(u'Wifi'), _(u'风扇'), _(u'关于'), _(u'断点续打'), _(u'机器参数'), _(u'关闭电机'), _(u'语言'), _(u'返回')]
        elif self.viewpos == 8:
            return [_(u'增加'), _(u''), _(u''), _(u'减少'), _(u'100%'), _(u'50%'), _(u'0%'), _(u'返回')]
        elif self.viewpos == 9:
            return [_(u'进料'), _(u''), _(u''), _(u'退料'), _(u'喷头1'), _(u'预热'), _(u'停止'), _(u'返回')]
        elif self.viewpos == 10:
            return [_(u'更多1'), _(u'更多2'), _(u'更多3'), _(u'更多4'), _(u'更多5'), _(u'更多6'), _(u'更多7'), _(u'返回')]
        elif self.viewpos == 11:
            return [_(u'MKS.gcode'), _(u''), _(u''), _(u''), _(u''), _(u''), _(u'test.g'), _(u'test.g'), _(u'test.g')]
        elif self.viewpos == 12:
            return [_(u''), _(u'test.g'), _(u'test.g'), _(u'test.g')]
        elif self.viewpos == 13:
            return [_(u'温度'), _(u'风扇'), _(u'换料'), _(u'变速'), _(u'更多'), _(u'手动关机'), _(u''), _(u'返回')]
        elif self.viewpos == 14:
            return [_(u'温度'), _(u'风扇'), _(u'换料'), _(u'挤出'), _(u'移动'), _(u'更多'), _(u'手动关机'), _(u''), _(u'返回')]
        elif self.viewpos == 15:
            return [_(u'增加'), _(u''), _(u''), _(u'减少'), _(u'移动'), _(u'挤出'), _(u'5%'), _(u'返回')]
        elif self.viewpos == 16:
            return [_(u''), _(u''), _(u''), _(u''), _(u''), _(u''), _(u''), _(u'返回')]
        elif self.viewpos == 17:
            return [_(u'简体'), _(u'繁体'), _(u'英语'), _(u'俄语'), _(u'西班牙语'), _(u'法语'), _(u'意大利语'), _(u'返回')]
        elif self.viewpos == 18:
            return [_(u''), _(u''), _(u''), _(u''), _(u''), _(u''), _(u'重新连接'), _(u'返回')]
        elif self.viewpos == 19:
            return [_(u'工具'), _(u'设置'), _(u'打印'), _(u''), _(u''), _(u''), _(u''), _(u'')]
        elif self.viewpos == 20:
            return [_(u'机器设置'), _(u'温度设置'), _(u'电机设置'), _(u'高级设置'), _(u''), _(u''), _(u''), _(u'返回')]
        else:
            return ['', '', '', '', '', '', '', '']

    def image2bin(self,image,binfile):
        f = open(binfile, 'wb')
        pixs = image.load()
        for y in range(image.size[1]):
            for x in range(image.size[0]):
                R = pixs[x, y][0] >> 3
                G = pixs[x, y][1] >> 2
                B = pixs[x, y][2] >> 3
                rgb = (R << 11) | (G << 5) | B
                strHex = "%x" % rgb
                if len(strHex) == 3:
                    strHex = '0' + strHex[0:3]
                elif len(strHex) == 2:
                    strHex = '00' + strHex[0:2]
                elif len(strHex) == 1:
                    strHex = '000' + strHex[0:1]
                if strHex[2:4] != '':
                    f.write(pack('B', int(strHex[2:4], 16)))
                if strHex[0:2] != '':
                    f.write(pack('B', int(strHex[0:2], 16)))
        f.close()

    def bin2image(self, binfile, outname):
        value = self.viewcb.GetSelection()
        temppath = sys.path[0] + "\\tempimgdiy\\" + outname + ".png"
        f = open(binfile, "rb")
        content = f.read()
        x=0
        y=0
        picwidth = self._picwidth
        picheight = self._picheight
        picwidth = 117
        picheight = 140
        if outname == "bmp_logo":
            picwidth = 480
            picheight = 320
        elif outname == "bmp_preview":
            picwidth = 200
            picheight = 200
        elif outname == "bmp_pause" or outname == "bmp_stop":
            picwidth = 150
            picheight = 80
        elif len(content)/2 < picwidth*picheight:
            picwidth = 150
            picheight = 80
            if len(content)/2 <picwidth*picheight:
                picwidth = 117
                picheight = 92
                if len(content)/2 < picwidth*picheight:
                    picwidth = 100
                    picheight = 100
                    if len(content)/2 < picwidth*picheight:
                        return
        image = Image.new('RGB', (picwidth, picheight))
        for i in range(0, len(content), 2):
            two = "%x" % ord(content[i])
            one = "%x" % ord(content[i + 1])
            rg = bin(int(one, 16)).replace('0b', '')
            gb = bin(int(two, 16)).replace('0b', '')
            while len(rg) < 8:
                rg = '0' + rg
            while len(gb) < 8:
                gb = '0' + gb
            r = int(rg[0:5] + '000', 2)
            g = int(rg[5:8] + gb[0:3] + '00', 2)
            b = int(gb[3:8] + '000', 2)
            image.putpixel((x, y), (r, g, b))
            x = x+1
            if x >= picwidth:
                y = y+1
                x = 0
            if y >= picheight:
                break
        if outname == 'filamentchange':
            print(image.size())
        image.save(temppath, 'png')

class chooseFrame(wx.Frame):
    def __init__(self):
        super(chooseFrame, self).__init__(None, title=u"MKSTOOL")
        self.icon = wx.Icon('mkstool.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.icon)
        locale = wx.Locale(wx.LANGUAGE_ENGLISH)
        locale.AddCatalogLookupPathPrefix('locale')
        self.languagename = self.getLanguage()
        ibRet = locale.AddCatalog(self.languagename)
        self._typelist = ["MKS Robin-TFT24/28/32", "MKS Robin Nano-TFT24/28/32", "MKS Robin Nano-TFT35", "MKS Robin Nano-TFT35-DIY-IAR", "MKS Robin Mini-TFT24/28/32", "MKS Robin2-TFT35"]
        self.languagelist = [u'中文', u'English']
        self.SetMaxSize((300, 200))
        self.SetSize((300, 200))
        # self._mainpanel = wx.Panel(self, -1)
        self.toppanel = wx.Panel(self, -1, size=(-1, 23))

        #toppanelview
        self.typetext = wx.StaticText(self.toppanel, -1, _(u'请选择类型：'), style=wx.ALIGN_CENTER | wx.ST_NO_AUTORESIZE)
        self.viewcb = wx.ComboBox(self.toppanel, -1, value=self._typelist[0], choices=self._typelist,style=wx.CB_READONLY)
        # self.viewcb.Bind(wx.EVT_COMBOBOX,lambda evt, widget= self.viewcb: self.pixelchange(evt,widget))

        self.langtext = wx.StaticText(self.toppanel, -1, _(u'请选择语言：'), style=wx.ALIGN_CENTER | wx.ST_NO_AUTORESIZE)
        self.language = wx.ComboBox(self.toppanel, -1, value=self.languagelist[0],choices=self.languagelist,style=wx.CB_READONLY)
        self.language.Bind(wx.EVT_COMBOBOX, lambda evt, widget=self.language: self.changelanguage(evt, widget))

        self._dlgbutton = wx.Button(self.toppanel, -1, _(u'确定'))
        self._dlgbutton.Bind(wx.EVT_BUTTON, self.pixelchange)

        if self.languagename == 'en':
            self.language.SetValue(self.languagelist[1])

        self.topsizer = wx.BoxSizer(wx.VERTICAL)
        self.topsizer.Add(self.typetext, 0, wx.LEFT | wx.RIGHT | wx.TOP, border=10)
        self.topsizer.Add(self.viewcb, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)
        self.topsizer.Add(self.langtext, 1, wx.LEFT | wx.RIGHT, border=10)
        self.topsizer.Add(self.language, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)
        self.topsizer.Add(self._dlgbutton, 2, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, border=10)
        self.toppanel.SetSizer(self.topsizer)
        self.Update()

    def pixelchange(self, e):
        value = self.viewcb.GetSelection()
        if value == 2 or value == 5:
            frames = mainwindow()
            frames.viewcb.SetSelection(1)
            frames.viewcbcopy.SetSelection(value)
        elif value == 3:
            frames = DIYFrame()
            frames.viewcb.SetSelection(3)
        else:
            frames = mainwindow()
            frames.viewcb.SetSelection(0)
            frames.viewcbcopy.SetSelection(value)
        frames.Show(True)
        self.Close()
        frames.pixelchange(None, None)
        frames.RefreshBitmap()


    def getLanguage(self):
        result = 'en'
        if not os.path.exists(os.path.abspath('')+'\\l.l'):
            f = open(os.path.abspath('')+'\\l.l','w')
            f.write(result)
            f.close()
        else:
            f = open(os.path.abspath('')+'\\l.l','r')
            content = f.read()
            if content == 'zh_CN':
                result = content
            f.close()
        return result

    def changelanguage(self,e,widget):
        value = widget.GetValue()
        content = 'zh_CN'
        f = open(os.path.abspath('') + '\\l.l', 'w')
        if value == self.languagelist[0]:
            f.write(content)
        elif value == self.languagelist[1]:
            f.write('en')
        f.close()

class MyNumberValidator( wx.PyValidator ):# 创建验证器子类
	# def __init__( self, name):
	# 	wx.PyValidator.__init__(self)
	# 	self.ValidInput = ['.', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
	# 	self.StringLength = 0
     #    self.name = name
     #    # self.type = 0
	# 	self.Bind(wx.EVT_CHAR,self.OnCharChanged)  #  绑定字符改变事件

    def __init__( self, obj, parent, id):
        super(MyNumberValidator,self).__init__()
        self.obj = obj
        self.value = ''
        self.parent = parent
        self.id = id
        self.ValidInput = ['.', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        print self.value
        self.Max = 1
        self.Min = 1
        if self.obj == 'type1':
            # 限制只能为数字，范围为-999~99999
            self.ValidInput = ['.', '-', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
            self.Max = 99999
            self.Min = -999
        elif self.obj == 'type2':
            # 限制只能为数字，范围为0~99999
            self.ValidInput = ['.', ',', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
            self.Max = 99999
            self.Min = 0
        elif self.obj == 'type3':
            # 限制只能为字母数字
            self.ValidInput = [';', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
            self.Max = 5
            self.Min = 1
        self.StringLength = 0
        self.Bind(wx.EVT_CHAR, self.OnCharChanged)  #  绑定字符改变事件

    def OnCharChanged(self, event):
        # self.value = self.parent.configbt[self.id][5]
        self.value = self.parent.getValue(self.id)
        # 得到输入字符的 ASCII 码
        keycode = event.GetKeyCode()
        # 退格（ASCII 码 为8），删除一个字符。
        if keycode == 8:
            if self.StringLength > 1:
                self.StringLength -= 1
            # 事件继续传递
            event.Skip()
            return

        # 把 ASII 码 转成字符
        InputChar = chr(keycode)
        print 'onchange'
        print self.StringLength
        print self.value
        if InputChar in self.ValidInput:
            # 第一个字符为 .,非法，拦截该事件，不会成功输入
            if InputChar == '.' and self.StringLength == 0:
                return False
            elif self.StringLength >= 5 and (self.obj == 'type1' or self.obj == 'type2'):
                print(self.StringLength)
                return False
            # elif self.obj == 'type1':
            #     if self.value != '':
            #         if self.value > 99999:
            #             return False
            #         elif self.value < -999:
            #             return False
            # elif self.obj == 'type2':
            #     if self.value != '':
            #         if self.value > 99999:
            #             return False
                # 在允许输入的范围，继续传递该事件。
            else:
                event.Skip()
                self.StringLength += 1
                return True
        return False
    def Clone(self):
        # Return a new validator for the same field of the same object.
        return self.__class__(self.obj, self.parent, self.id)

    def Validate(self,win):#1 使用验证器方法
        return True

    def TransferToWindow(self):
        return True

    def TransferFromWindow(self):
        return True

app = wx.App(False)
# frame = mainwindow()
frame = chooseFrame()
frame.Show(True)
# frame.RefreshBitmap()
app.MainLoop()