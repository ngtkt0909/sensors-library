#!/usr/bin/python
# -*- coding: utf-8 -*-

from common import signed_byte
from common import signed_short
from common import make_short

class L3GD20:
	u'''
	STマイクロ社製 L3GD20 ジャイロセンサモジュール
	'''

	# Register Map
	__REG_WHO_AM_I      = 0x0F
	__REG_CTRL_REG1     = 0x20
	__REG_CTRL_REG2     = 0x21
	__REG_CTRL_REG3     = 0x22
	__REG_CTRL_REG4     = 0x23
	__REG_CTRL_REG5     = 0x24
	__REG_OUT_TEMP      = 0x26
	__REG_STATUS_REG    = 0x27
	__REG_OUT_X_L       = 0x28
	__REG_OUT_X_H       = 0x29
	__REG_OUT_Y_L       = 0x2A
	__REG_OUT_Y_H       = 0x2B
	__REG_OUT_Z_L       = 0x2C
	__REG_OUT_Z_H       = 0x2D
	__REG_FIFO_CTRL_REG = 0x2E
	__REG_FIFLE_SRC_REG = 0x2F
	__REG_INT1_CFG      = 0x30
	__REG_INT1_SRC      = 0x31
	__REG_INT1_TSH_X    = 0x32
	__REG_INT1_TSH_Y    = 0x34
	__REG_INT1_TSH_Z    = 0x36
	__REG_INT1_DURATION = 0x39

	# Slave Address
	__SLAVE_ADDR_GND = 0x6A		# CS == GND
	__SLAVE_ADDR_VDD = 0x6B		# CS == VDD

	# CTRL_REG1
	__CTRL_REG1_PD_OFF  = 0x08				# normal mode or sleep mode
	__CTRL_REG1_ZEN     = 0x04				# Z axis enable
	__CTRL_REG1_YEN     = 0x02				# Y axis enable
	__CTRL_REG1_XEN     = 0x01				# X axis enable

	# CTRL_REG4
	__CTRL_REG4_FS_250  = 0x00				# ±250 dps
	__CTRL_REG4_FS_500  = 0x10				# ±500 dps
	__CTRL_REG4_FS_2000 = 0x20				# ±2000 dps

	# FIFO_CTRL_REG
	__FIFO_CTRL_REG_BYPASS       = 0x00		# Bypass mode
	__FIFO_CTRL_REG_FIFO         = 0x20		# FIFO mode
	__FIFO_CTRL_REG_STREAM       = 0x40		# Stream mode
	__FIFO_CTRL_REG_STREAM_FIFO  = 0x60		# Stream-to-FIFO mode
	__FIFO_CTRL_REG_BYPASS_STREM = 0x80		# Bypass-to-Stream mode

	# 1LSB当たりの角速度（dps/LSB）
	__GYRO_DPS_PER_LSB_250  = 0.00875		# ±250 dps
	__GYRO_DPS_PER_LSB_500  = 0.0175		# ±500 dps
	__GYRO_DPS_PER_LSB_2000 = 0.07			# ±2000 dps

	# 設定項目
	__CFG_FULL_SCALE = __CTRL_REG4_FS_250
	__CFG_FIFO_MODE  = __FIFO_CTRL_REG_FIFO

	def __init__(self, bus_id, cs):
		u''' 初期化 '''
		import smbus
		self.slave_addr = self.__SLAVE_ADDR_VDD if cs else self.__SLAVE_ADDR_GND
		self.bus = smbus.SMBus(bus_id)
		# 接続確認
		assert self.bus.read_byte_data(self.slave_addr, self.__REG_WHO_AM_I) == 0xD4
		# レジスタ設定
		self.bus.write_byte_data(self.slave_addr, self.__REG_CTRL_REG1,
			self.__CTRL_REG1_PD_OFF |
			self.__CTRL_REG1_XEN |
			self.__CTRL_REG1_YEN |
			self.__CTRL_REG1_ZEN)
		self.bus.write_byte_data(self.slave_addr, self.__REG_CTRL_REG4, self.__CFG_FULL_SCALE)
		self.bus.write_byte_data(self.slave_addr, self.__REG_FIFO_CTRL_REG, self.__CFG_FIFO_MODE)
		# 制御値
		if self.__CFG_FULL_SCALE == self.__CTRL_REG4_FS_250:
			self.gyro_dps_per_lsb = self.__GYRO_DPS_PER_LSB_250
		elif self.__CFG_FULL_SCALE == self.__CTRL_REG4_FS_500:
			self.gyro_dps_per_lsb = self.__GYRO_DPS_PER_LSB_500
		elif self.__CFG_FULL_SCALE == self.__CTRL_REG4_FS_2000:
			self.gyro_dps_per_lsb == self.__GYRO_DPS_PER_LSB_2000
		else: assert False

	def get_x(self):
		u''' 角速度（X軸）を取得 '''
		lo = self.bus.read_byte_data(self.slave_addr, self.__REG_OUT_X_L)
		hi = self.bus.read_byte_data(self.slave_addr, self.__REG_OUT_X_H)
		return signed_short(make_short(hi, lo)) * self.gyro_dps_per_lsb

	def get_y(self):
		u''' 角速度（Y軸）を取得 '''
		lo = self.bus.read_byte_data(self.slave_addr, self.__REG_OUT_Y_L)
		hi = self.bus.read_byte_data(self.slave_addr, self.__REG_OUT_Y_H)
		return signed_short(make_short(hi, lo)) * self.gyro_dps_per_lsb

	def get_z(self):
		u''' 角速度（Z軸）を取得 '''
		lo = self.bus.read_byte_data(self.slave_addr, self.__REG_OUT_Z_L)
		hi = self.bus.read_byte_data(self.slave_addr, self.__REG_OUT_Z_H)
		return signed_short(make_short(hi, lo)) * self.gyro_dps_per_lsb

	def get_temp(self):
		u''' 温度を取得 '''
		data = self.bus.read_byte_data(self.slave_addr, self.__REG_OUT_TEMP)
		return signed_byte(data)

	def run(self):
		u''' 角速度（X軸，Y軸，Z軸）および温度を連続取得し，CSV形式で表示 '''
		import sys
		import csv
		import datetime
		csvout = csv.writer(sys.stdout, lineterminator='\n')
		csvout.writerow(['DATE', 'GYRO_X', 'GYRO_Y', 'GYRO_Z', 'TEMP'])
		while True:
			now = datetime.datetime.today()
			gyro_x = self.get_x()
			gyro_y = self.get_y()
			gyro_z = self.get_z()
			temp   = self.get_temp()
			csvout.writerow([
				now.strftime('%Y/%m/%d %H:%M:%S.') + '%04d' % (now.microsecond // 1000),
				gyro_x, gyro_y, gyro_z, temp
			])
