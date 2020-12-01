
# -*- coding: UTF-8 -*-
import re
import requests
import urllib3

class Stock(object):
	def __init__(self, ticker, attrs):
		self.ticker = ticker
		if isinstance(attrs, (int, float)):
			self.key_amount = attrs
			self.is_key = True
		else:
			self.init_attrs(attrs)
			self.is_key = False

	def init_attrs(self, attrs):
		self.name=''
		self.weight_1 = attrs[0]
		self.stock_weight = attrs[1]
		self.day_percent = attrs[2]
		self.price_limit = attrs[3]
		self.weight_2 = attrs[4]
		self.buy_in = attrs[5]
		self.own_amount = attrs[6]
		self.sell_out = attrs[7]
		self.sell_amount = attrs[8]
		self.if_track_1 = True
		self.if_track_2 = False
		self.deal_cond_1 = False
		self.deal_cond_2 = False

	def decode(self, res):
		pattern = re.compile(r'"([^"]*)"', re.M)
		decode_str = pattern.findall(res) # return list
		allparts = decode_str[0].split(",")
		self.name = allparts[0]
		self.new = round(float(allparts[3]),4)
		self.percent_float = (float(allparts[3]) - float(allparts[2])) / float(allparts[2]) # 当前价
		self.percent_str = str(round((float(allparts[3]) - float(allparts[2])) / float(allparts[2]) * 100, 3))+"%"
		self.zhangdie = round(float(allparts[3]) - float(allparts[2]), 4)
		self.zuoshou = float(allparts[2])
		self.time = allparts[30]+' '+allparts[31]
		self.buy_one_pr = float(allparts[11])
		self.buy_one_amt = float(allparts[10])
		self.sell_one_pr = float(allparts[21])
		self.sell_one_amt= float(allparts[20])
		self.percent_float_buy_one = (float(allparts[11]) - float(allparts[2])) / float(allparts[2]) # 买一
		self.percent_float_sell_one = (float(allparts[21]) - float(allparts[2])) / float(allparts[2]) # 卖一


class DataManager(object):
	def __init__(self):
		self.url = 'http://hq.sinajs.cn/list='
		self.stock_list = []
		self.key_stock = None

	def add_stock(self, ticker, attrs):
		self.stock_list.append(Stock(ticker, attrs))

	def add_key_stock(self, key_ticker, key_amount):
		s = Stock(key_ticker, key_amount)
		self.key_stock = s
		self.stock_list.append(s)

	
	def update(self):
		# web request
		http = urllib3.PoolManager(timeout=5.0)
		urllib3.disable_warnings()
		res = http.request('GET', self.url + self.get_requst_str())

		content = str(res.data, "gbk")

		if False and is_tradingtime(dtnow.time()): # pass for debug
			warning = "刚刚网络链接有问题，请注意！"
			send_msg_dingding(warning)

		res_array = content.split(";")
		for stock, res in zip(self.stock_list, res_array):
			stock.decode(res)
			
	def get_requst_str(self):
		request_str = ""

		for stock in self.stock_list:
			request_str += (stock.ticker + ',')
		return request_str
	
