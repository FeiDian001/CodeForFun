
# -*- coding: UTF-8 -*-

from stock import Stock, DataManager
import tkinter as tk
import tkinter
from tkinter.ttk import *
import threading
import time
import pywinauto
from pywinauto import clipboard
from pywinauto import keyboard

import pandas as pd
import io


PADX = 10
PADY = 10

INNER_PADX = 10
INNER_PADY = 5

class WindowMnager(object):
	def __init__(self):
		self.init_view()
		self.stat = True
		self.data_manager = DataManager()
		self.data_manager.add_key_stock('sh601939', 4000)
		self.data_manager.add_stock('sh600036', [0.01, 0.4, 0.5, 1000.0, 0.015, 0.0, 0, 0.0, 0])
		self.data_manager.add_stock('sz002142', [0.02, 0.35, 0.5, 33.44, 0.02, 0.0, 0, 0.0, 0])
		self.data_manager.add_stock('sz000001', [0.01, 0.25, 0.5, 1000.0, 0.02, 0.0, 0, 0.0, 0])
		self.update_BCD_tree()
		self.bcd_tree.bind('<Double-1>', self.set_cell_value)  # 双击左键进入编辑
		self.window.mainloop()  # event listener

	
	def init_view(self):
		self.window = tk.Tk()
		self.window.title("股票监控工具")
		self.window.geometry('1380x800')
		self.window.resizable(0, 0) ##

		'''pre pack'''
		#divide into 4 parts
		frame_top = Frame(self.window)
		frame_top.pack(side='top',anchor='n')
		frame_bottom = Frame(self.window)
		frame_bottom.pack(side='top', anchor='n')
		frame_left = LabelFrame(frame_top, text = '股票跟踪')
		frame_left.pack(side='left', anchor='nw',padx=PADX, pady=PADY)
		frame_right = LabelFrame(frame_top, text = 'BCD  输入参数（双击修改参数和跟踪状态）')
		frame_right.pack(side='left',anchor='nw',padx=PADX, pady=PADY)
		frame_b_left = LabelFrame(frame_bottom, text='条件1')
		frame_b_left.pack(side='left', anchor='nw', padx=PADX, pady=PADY)
		frame_b_right = LabelFrame(frame_bottom, text='条件2')
		frame_b_right.pack(side='left', anchor='nw', padx=PADX, pady=PADY)

		'''origin part'''		
		#--tree--
		columns ={"ticker": "代码",
					"name": "名称",
					"new": "最新",
					"percent_str": "涨幅",
					"zhangdie": "涨跌"} #use as index
		MAX_ITEMS = 5
		self.main_tree = Treeview(frame_left, show = "headings", columns = list(columns.keys()),  selectmode = tk.BROWSE)
		self.main_tree.pack(side='top', anchor='w',padx=INNER_PADX, pady=INNER_PADY)
		# main_tree 显示颜色方法和补丁
		# tag 涨跌
		self.main_tree.tag_configure('redrow', background='Salmon', foreground='black')
		self.main_tree.tag_configure('greenrow', background='PaleGreen', foreground='black')

		# treeview不显示颜色补丁方法
		def fixed_map(option):
			return [elm for elm in style.map("Treeview", query_opt=option) if elm[:2] != ("!disabled", "!selected")]

		# 列表不显示颜色补丁
		style = Style()
		style.map("Treeview", foreground=fixed_map("foreground"), background=fixed_map("background"))

		for key, value in columns.items():
			self.main_tree.column(key, width = 70)  # set width
			self.main_tree.heading(key, text = value) # set heading


		#--button--
		button_frame = Frame(frame_left)
		button_frame.pack(side='top', anchor='n')
		self.button_strat = tk.Button(button_frame, text='开始监控', font=('Arial', 10), width=10, command=self.start_update)
		self.button_end = tk.Button(button_frame, text='停止监控', font=('Arial', 10), width=10, command=self.stop_update)
		self.button_strat.pack(side='left', anchor='n',padx=INNER_PADX, pady=INNER_PADY)
		self.button_end.pack(side='left', anchor='n',padx=INNER_PADX, pady=INNER_PADY)
		self.button_end['state'] = 'disable'
	
		
		'''BCD'''
		#--tree--
		self.bcd_columns ={"ticker": "代码",
					"name": "名称",
					"weight_1": "条件1系数",
					"stock_weight": "股票系数",
					"day_percent": "单日比例",
					"price_limit": "价格限制",
					"weight_2": "条件2系数",
					"buy_in": "X买入价", 
					"own_amount": "持有数",
					"sell_out":"A卖出价", 
					"sell_amount":"应买入A数", 
					"if_track_1":"条1跟踪否",
					"if_track_2":"条2跟踪否"} #use as index
		MAX_ITEMS = 5
		self.bcd_tree = Treeview(frame_right, show = "headings", columns = list(self.bcd_columns.keys()),  selectmode = tk.BROWSE)
		self.bcd_tree.pack(side='top',anchor='n',padx=INNER_PADX, pady=INNER_PADY)

		for key, value in self.bcd_columns.items():
			self.bcd_tree.column(key, width = 70)  # set width
			self.bcd_tree.heading(key, text = value) # set heading

		'''condition monitor'''
		#pre pack
		self.condition_text_1 = tk.Text(frame_b_left, width=90, height=25)
		self.condition_text_1.pack(side='left', anchor='n', padx=INNER_PADX, pady=INNER_PADY)
		self.condition_text_2 = tk.Text(frame_b_right, width=90, height=25)
		self.condition_text_2.pack(side='left', anchor='n', padx=INNER_PADX, pady=INNER_PADY)

		# seq_number and log line
		self.snum_text_1 = 0
		self.log_line_text_1 = 0
		self.snum_text_2 = 0
		self.log_line_text_2 = 0

		# transaction
		# self.buy_time = 0




	def start_update(self, *arg):
		self.stat = True
		self.button_strat['state']= 'disable'
		self.button_end['state'] = 'active'

		timer = threading.Thread(target=self.get_data)
		timer.daemon = True
		timer.start()
	
	def stop_update(self, *arg):
		self.stat = False
		self.button_strat['state'] = 'active'
		self.button_end['state'] = 'disable'

	def get_data(self):
		while(self.stat):
			self.data_manager.update()
			self.update_main_tree()
			self.update_condition_text_1()
			print("开始检测")
			self.update_condition_text_2()
			time.sleep(2)

	def update_main_tree(self):
		items = self.main_tree.get_children()
		for item in items:
			self.main_tree.delete(item)
		line = 0
		for stock in self.data_manager.stock_list:
			attr_list = ["ticker", "name", "new", "percent_str", "zhangdie"]
			value = self.get_value_list(stock, attr_list)
			if stock.percent_float > 0:
				self.main_tree.insert("", line, values=value, tags=('redrow',))
			elif stock.percent_float < 0:
				self.main_tree.insert("", line, values=value, tags=('greenrow',))
			else:
				self.main_tree.insert("", line, values=value)
			line += 1

	def update_BCD_tree(self):
		self.data_manager.update()  # ????
		# self.update_main_tree()  # ?????
		line = 0
		attr_list = list(self.bcd_columns.keys())
		for stock in self.data_manager.stock_list:
			if stock != self.data_manager.key_stock:
				self.bcd_tree.insert('', line, values=self.get_value_list(stock, attr_list))

	def get_value_list(self, stock, key_list):
		values = []
		for key in key_list:
			values.append(getattr(stock, key, ''))
		return values

	def update_condition_text_1(self):
		key_stock = self.data_manager.key_stock
		for stock in self.data_manager.stock_list:
			if stock != key_stock and stock.if_track_1:
				# cond_one_pc = key_stock.percent_float - stock.percent_float

				cond_one_pc = key_stock.percent_float_buy_one - stock.percent_float_sell_one
				if cond_one_pc >= stock.weight_1 and stock.price_limit >= stock.zuoshou:
					# 实际比例
					cond_one_pc_str = str(round(cond_one_pc * 100, 3))+"%"
					# 提醒序号 +1
					self.snum_text_1 += 1
					# log_line 20行
					if self.log_line_text_1 > 18:
						self.condition_text_1.delete(1.0, 5.0)

					amount_to_sell = int((key_stock.key_amount * stock.stock_weight * stock.day_percent) / 100) * 100
					amount_to_buy = int((amount_to_sell * key_stock.buy_one_pr / stock.sell_one_pr) / 100) * 100
					amt_max = max(amount_to_buy, amount_to_sell)
					print(amount_to_sell)
					print(amount_to_buy)
					print(key_stock.buy_one_amt)
					print(stock.sell_one_amt)

					# 实际同时可买卖股数
					same_time_bs_amt = int(min(key_stock.buy_one_amt, stock.sell_one_amt))
					print(same_time_bs_amt)
					if same_time_bs_amt > (amt_max + 800):
						signal_one_text = "条件1触发__" + str(self.snum_text_1) + " " + key_stock.time + " " \
						                  + stock.name + " 触发： " + cond_one_pc_str + " 同时买卖：" + str(same_time_bs_amt) + "\n" \
						                  + key_stock.name + " 买一： " + str(key_stock.buy_one_pr) + "可卖数量： " + str(amount_to_sell) + "\n" \
						                  + stock.name + " 卖一： " + str(stock.sell_one_pr) + "可买数量: " + str(amount_to_buy) + "\n\n"
						self.condition_text_1.insert(tk.END, signal_one_text)
						self.log_line_text_1 += 4
						# send_msg_dingding

						if not stock.deal_cond_1:
							# sell stock
							node = '上海' if key_stock.ticker[0:2] == 'sh' else '深圳'
							sell_stock = [node, key_stock.ticker[2:], key_stock.buy_one_pr, amount_to_sell]
							# buy stock
							node_2 = '上海' if stock.ticker[0:2] == 'sh' else '深圳'
							buy_stock = [node_2, stock.ticker[2:], stock.sell_one_pr, amount_to_buy]
							self.run_stock_program(buy_stock, sell_stock)
							stock.deal_cond_1 = True  # 已完成条件1交易
							print("已完成条件1交易： " + signal_one_text)
							time.sleep(2)



	def update_condition_text_2(self):
		key_stock = self.data_manager.key_stock
		for stock in self.data_manager.stock_list:
			if stock != key_stock and stock.if_track_2:
				# cond_one_pc = key_stock.percent_float - stock.percent_float

				cond_two_pc = stock.buy_one_pr / stock.buy_in - key_stock.sell_one_pr / stock.sell_out
				if cond_two_pc >= stock.weight_2:
					# 实际比例
					cond_two_pc_str = str(round(cond_two_pc * 100, 3)) + "%"
					# 提醒序号 +1
					self.snum_text_2 += 1
					# log_line 20行
					if self.log_line_text_2 > 18:
						self.condition_text_2.delete(1.0, 5.0)
					amt_to_sell = stock.own_amount
					amt_to_buy = stock.sell_amount
					amt_max_2 = max(amt_to_buy, amt_to_sell)

					# 实际同时可买卖股数
					same_time_bs_amt_2 = int(min(key_stock.sell_one_amt, stock.buy_one_amt))
					if same_time_bs_amt_2 >(amt_max_2 + 800):
						signal_two_text = "条件2触发__" + str(self.snum_text_2) + " " + key_stock.time + " " +\
						                  stock.name + " 触发： " + cond_two_pc_str + \
						                  "\n" + stock.name + " 买一： " + str(stock.buy_one_pr) + " 应卖数量： "\
						                  + str(amt_to_sell) + \
						                  "\n" + key_stock.name + " 卖一： " + str(key_stock.sell_one_pr) + " 应买数量: "\
						                  + str(amt_to_buy) + "\n\n"
						self.condition_text_2.insert(tk.END, signal_two_text)
						self.log_line_text_2 += 4
						# send_msg_dingding(signal_two_text)


						if not stock.deal_cond_2:
							# sell stock
							node_2 = '上海' if stock.ticker[0:2] == 'sh' else '深圳'
							sell_stock = [node_2, stock.ticker[2:], stock.buy_one_pr, amt_to_sell]
							# buy stock
							node = '上海' if key_stock.ticker[0:2] == 'sh' else '深圳'
							buy_stock = [node, key_stock.ticker[2:], key_stock.sell_one_pr, amt_to_buy]
							self.run_stock_program(buy_stock, sell_stock)
							stock.deal_cond_2 = True
							print("已完成交易： " + signal_two_text)
							# stock.if_track_1 = False
							time.sleep(2)


		return

	def set_cell_value(self, event):
		column = self.bcd_tree.identify_column(event.x)
		cn = int(str(column).replace('#', ''))
		# print(cn)
		row = self.bcd_tree.identify_row(event.y)  # 行
		rn = int(str(row).replace('I', ''))
		# print(rn)
		item = self.bcd_tree.selection()[0]
		if cn > 2 and cn < 12:
			entryedit = Entry(self.bcd_tree, width=8)
			entryedit.place(x=event.x-20, y=event.y-10)
			def saveedit():
				en = entryedit.get()
				# print(en)
				# print(len(en))

				def isfloat(en):
					try:
						float(en)
						return True
					except ValueError:
						return False
				if not isfloat(en):
					en = "双击输入值"
					self.bcd_tree.set(row, column=column, value=en)
				else:
					self.bcd_tree.set(row, column=column, value=en)
					values = self.bcd_tree.item(item, "values")
					print(values)
					key_change = values[0]
					print(values[0])
					values_list = []
					for i in range(2, 11):
						values_list.append(float(values[i]))
						print(values_list)
					for key in self.data_manager.stock_list:
						if key.ticker == key_change:
							key.init_attrs(values_list) # 更新Stock attrs
							print(key.sell_amount)
				entryedit.destroy()
				okb.destroy()
			okb = tk.Button(self.bcd_tree, text='OK', width=4, command=saveedit)
			okb.place(x=event.x+42, y=event.y-14)
		elif cn >= 12:
			values = self.bcd_tree.item(item, "values")
			key_change = values[0]
			for key in self.data_manager.stock_list:
				if key.ticker == key_change:
					if cn == 12:
						key.if_track_1 = not key.if_track_1  # 更新Stock attrs
						self.bcd_tree.set(row, column=column, value=str(key.if_track_1))
						print(key.if_track_1)
					elif cn == 13:
						key.if_track_2 = not key.if_track_2  # 更新Stock attrs
						self.bcd_tree.set(row, column=column, value=str(key.if_track_2))
						print(key.if_track_2)

	def run_stock_program(self, buy_stock, sell_stock):
		exe_path = r"C:\中信证券至胜独立下单版\jtxd\xiadan.exe"
		app = pywinauto.Application().connect(path=exe_path, timepout=10)
		app.top_window().set_focus()

		if r"中信" in app.top_window().window_text():
			print("yes!")
		dlg_spec = app['中信证券至胜全能版']
		time.sleep(1)
		buy_sh_sz = dlg_spec.child_window(class_name='ComboBox', found_index=0).select(buy_stock[0])
		buy_code = dlg_spec.child_window(class_name='Edit', found_index=0).set_text(str(buy_stock[1]))
		buy_prc = dlg_spec.child_window(class_name='Edit', found_index=1).set_text(str(buy_stock[2]))
		buy_amt = dlg_spec.child_window(class_name='Edit', found_index=2).set_text(str(buy_stock[3]))
		sell_sh_sz = dlg_spec.child_window(class_name='ComboBox', found_index=3).select(sell_stock[0])
		sell_code = dlg_spec.child_window(class_name='Edit', found_index=3).set_text(str(sell_stock[1]))
		sell_prc = dlg_spec.child_window(class_name='Edit', found_index=4).set_text(str(sell_stock[2]))
		sell_amt = dlg_spec.child_window(class_name='Edit', found_index=5).set_text(str(sell_stock[3]))
		time.sleep(0.1)
		dlg_spec['同时买卖'].click()
		time.sleep(0.1)
		keyboard.send_keys('{VK_F5}')








	
	
w = WindowMnager()

'''
d = DataManager()
d.add_stock("sz000001")
d.add_stock("sz002142")
d.update()
'''
