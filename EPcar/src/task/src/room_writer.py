import xlwt
import xlrd
import xlwt
from xlutils.copy import copy

class Room_writer:
    def __init__(self):
        self.row = 0
    
    def write_header(self):
        self.row = 0
        self.wb = xlwt.Workbook()
        self.sheet = self.wb.add_sheet("sheet1")
        # write the first line
        label = ["房间", "好人", "坏人"]
        for i in label:
            self.sheet.write(0, label.index(i), i)
        self.row += 1

    # 写入一行信息 good:好人数量 bad:坏人数量
    def write_room(self, row, index, good=0, bad=0):
        if row > 2:
            pass
        col = 0
        self.sheet.write(self.row, col, f"{row}-{index}")
        col += 1
        self.sheet.write(self.row, col, good)
        col += 1
        self.sheet.write(self.row, col, bad)
        self.row += 1

    # car_data格式： [[房间1好人,房间1坏人],[房间2好人,房间2坏人],...]
    def write_car_data(self,filepath,car_data):
        rb = xlrd.open_workbook(filepath, formatting_info=True)
        self.wb = copy(rb)
        self.sheet = self.wb.get_sheet(0)
        self.row = rb.sheet_by_index(0).nrows
        index = 9
        for idn in range(0, 4):
            self.write_room(1, index + idn, car_data[idn][0], car_data[idn][1])
        index = 12
        for idn in range(0, 4):
            self.write_room(2, index - idn , car_data[idn+4][0], car_data[idn+4][1])

    # air_data格式同上 ; 比赛类别cls, "pre":预选赛 , "fin":决赛
    def write_air_data(self,filepath,air_data, cls="pre"):
        rb = xlrd.open_workbook(filepath, formatting_info=True)
        self.wb = copy(rb)
        self.sheet = self.wb.get_sheet(0)
        self.row = rb.sheet_by_index(0).nrows
        if cls == "pre":
            index = 1
            for idn in range(0, 4):
                self.write_room(1, index + idn, air_data[idn][0], air_data[idn][1])
            index = 4
            for idn in range(0, 4):
                self.write_room(2, index - idn, air_data[idn+4][0], air_data[idn+4][1])
        if cls == "fin":
            index = 1
            for idn in range(0, 4):
                self.write_room(1, index + idn, air_data[idn][0], air_data[idn][1])
            index = 5
            for idn in range(0, 4):
                self.write_room(1, index + idn, air_data[idn][2], air_data[idn][3])
            index = 4
            for idn in range(0, 4):
                self.write_room(2, index - idn, air_data[idn+4][0], air_data[idn+4][1])
            index = 8
            for idn in range(0, 4):
                self.write_room(2, index - idn, air_data[idn+4][2], air_data[idn+4][3])

    def data_save(self,filename):
        self.wb.save(filename + ".xls")

if __name__ == "__main__":
    # 测试
    Room_Writer1 = Room_writer()
    Room_Writer1.write_header()
    Room_Writer1.data_save("/home/tta/tta/list_of_goods_1")
    task_result_end = [[1, 0, 0, 0], [1, 1, 0, 3], [0, 1, 1, 2], [2, 3, 0, 0], [0, 1, 0, 0], [1, 1, 0, 0], [1, 1, 1, 0], [2, 1, 1, 1]]
    Room_Writer1.write_air_data("/home/tta/tta/list_of_goods_1.xls",task_result_end,cls="fin")
    Room_Writer1.data_save("/home/tta/tta/list_of_goods_1")
    # task_result_end = [[1, 2], [1, 2], [1, 2], [1, 2], [1, 2], [1, 2], [1, 2], [1, 2]]
    # Room_Writer1.write_air_data("/home/tta/list_of_goods_1.xls",task_result_end,cls="pre")
    # Room_Writer1.data_save("/home/tta/list_of_goods_1")
    Room_Writer1.write_car_data("/home/tta/tta/list_of_goods_1.xls",[[0, 1], [1, 0], [0, 1], [1, 0], [0, 1], [1, 0], [0, 1], [1, 0]])
    Room_Writer1.data_save("/home/tta/tta/list_of_goods_1")