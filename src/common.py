#!/usr/bin/python
# -*- coding: utf-8 -*-

def signed_byte(value):
	u''' 8bit 符号付整数変換 '''
	if value >= 0x80:
		return 0xFF - value - 1
	else:
		return value

def signed_short(value):
	u''' 16bit 符号付整数変換 '''
	if value >= 0x8000:
		return 0xFFFF - value - 1
	else:
		return value

def signed_long(value):
	u''' 32bit 符号付整数変換 '''
	if value >= 0x80000000:
		return 0xFFFFFFFF - value - 1
	else:
		return value

def make_short(hi, lo):
	u''' 16bitデータ生成 '''
	return (((hi & 0xFF) << 8) |
			 (lo & 0xFF))

def make_long(hh, hl, lh, ll):
	u''' 32bitデータ生成 '''
	return (((hh & 0xFF) << 24) |
			((hl & 0xFF) << 16) |
			((lh & 0xFF) << 8) |
			 (ll & 0xFF))
