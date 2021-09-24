# coding=utf-8
import os

addr_list = []

class err_process:
    m_err_list = []
    m_err_cnt = 0
    m_station = ''
    m_frist_line = 0
    m_machine_counts = 0

    def __init__(self, err_type: str, frist_line: int, station: str):
        self.m_err_list = {}.copy()
        self.m_err_list.clear()
        self.m_station = station
        self.add_err(err_type, frist_line)
        self.m_machine_counts = 3

    def add_err(self, err_type: str, cur_line: int):
        if 'OK' in err_type:
            self.clear()
            return '', {}
        if self.m_err_cnt == 0:
            self.m_frist_line = cur_line
        if err_type in self.m_err_list:
            self.m_err_list[err_type] += 1
        else:
            self.m_err_list[err_type] = 1
        self.m_err_cnt += 1
        if self.m_err_cnt == self.m_machine_counts:
            temp_str = '        {\"failed info\": %s,\"first line\": %d, \"station num\": \"%s\"},\n' % ( \
                str(self.m_err_list).replace('\'', '\"'), self.m_frist_line, self.m_station.replace('\n', ''))
            err_list = self.m_err_list.copy()
            self.clear()
            return temp_str, err_list
        else:
            return '', {}

    def __len__(self):
        return self.m_err_cnt

    def clear(self):
        self.m_frist_line = 0
        self.m_err_list.clear()
        self.m_err_cnt = 0


def indent_process(src_str: str, n: int = 0):
    dst_str = ''
    last_index = 0
    src_str = src_str.replace(', ', ',')
    for index in range(len(src_str)):
        if src_str[index] == '{':
            if len(src_str[last_index: index]):
                dst_str += ('\n' + ('    ' * n) + src_str[last_index: index])
            dst_str += ('\n' + ('    ' * n) + '{')
            n += 1
            last_index = index + 1
        elif src_str[index] == '}':
            if len(src_str[last_index: index]):
                dst_str += ('\n' + ('    ' * n) + src_str[last_index: index])
            n -= 1
            dst_str += ('\n' + ('    ' * n) + '}')
            last_index = index + 1
        elif src_str[index] == ',':
            if len(src_str[last_index: index + 1]):
                dst_str += ('\n' + ('    ' * n) + src_str[last_index: index + 1])
            last_index = index + 1

    return dst_str


def addr_duplicate_checking(addr: str):
    global addr_list
    if addr != "\'000000000000" and addr in addr_list:
        print(addr)
    else:
        addr_list.append(addr)
        if len(addr_list) > 100:
            addr_list.pop(0)


def product_file_process(file: str):
    with open(file, '+r') as fp:
        line_cnt = 0
        err_list = []
        STATS_info = {'total': 0, 'success cnt': 0, 'failed cnt': 0, "type STATS": {}, "00000000 address cnt": 0}
        list_str = '\n    \"err_list\": [\n'

        while True:
            line = fp.readline()  # .encode('utf8')
            line_cnt += 1
            if not line:
                print('file end, line cnt' + str(line_cnt))
                break
            info_list = line.split(',')

            if len(info_list) > 8:
                if 'OK' in info_list[3]:
                    # addr_duplicate_checking(info_list[2])
                    STATS_info['success cnt'] += 1
                    if "000000000000" in info_list[2]:   # and info_list[2] != "\'000000000000"
                        STATS_info["00000000 address cnt"] += 1
                        print(info_list[2])
                for item in err_list:
                    if item.m_station == info_list[4]:
                        temp_str, t_list = item.add_err(info_list[3], line_cnt)
                        if len(temp_str):
                            list_str += temp_str
                            STATS_info['failed cnt'] += 1
                            for i in t_list:
                                if i in STATS_info['type STATS']:
                                    STATS_info['type STATS'][i] += 1
                                else:
                                    STATS_info['type STATS'][i] = 1
                        break
                else:
                    err_list.append(err_process(info_list[3], line_cnt, info_list[4]))
        list_str = list_str[:-2]
        list_str += '\n    ]\n}'
        with open(file.replace('.csv', '_result.json'), 'wb') as dst_fp:
            STATS_info['total'] = STATS_info['failed cnt'] + STATS_info['success cnt']
            STATS_info['failed cnt'] = str(STATS_info['failed cnt']) + '(' + str(round(STATS_info['failed cnt'] \
                                                                                       * 100 / STATS_info['total'],
                                                                                       3)) + '%)'
            STATS_info['success cnt'] = str(STATS_info['success cnt']) + '(' + str(round(STATS_info['success cnt'] \
                                                                                         * 100 / STATS_info['total'],
                                                                                         3)) + '%)'
            for key in STATS_info['type STATS']:
                temp_int = STATS_info['type STATS'][key]
                STATS_info['type STATS'][key] = '%s(%s%%)' % (
                str(temp_int), str(round(temp_int * 100 / STATS_info['total'], 3)))
            dst_fp.write('{\n    \"STATS\" : '.encode())
            dst_fp.write((indent_process(str(STATS_info).replace('\'', '\"'), 1) + ',').encode())
            dst_fp.write(list_str.encode())
            dst_fp.close()
        print(STATS_info)
        fp.close()


def main():
    cur_path = os.path.abspath('.')

    file_list = os.listdir(cur_path)

    for i in file_list:
        if i.find('.csv') != -1:
            print('file name:' + i)
            product_file_process(i)


if __name__ == "__main__":
    main()
