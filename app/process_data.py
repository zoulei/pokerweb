import os

from Constant import *
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def read_header(step=0):
    fname = get_train_data_schema_file(step)
    header = list()
    header_map = dict()
    with open(fname) as f:
        for line in f:
            line = line.strip()
            if len(line) == 0:
                continue
            header_map[line] = len(header)
            header.append(line)
    return header, header_map

def check_odds():
    header, header_map = read_header()
    odds_idx = header_map["odds_is_10000"]
    with open(TRAINDATAFILE) as f:
        for line in f:
            line = line.strip()
            data = line.split(SPACE)
            if data[odds_idx] != "0":
                print("check_odds failed! data[odds_idx]:", data[odds_idx], "\tdata[odds_idx + 1]:", data[odds_idx + 1])
                return
    print("check_odds success!")

def get_data_range():
    import copy
    header, header_map = read_header()
    with open(NORMALIZEDTRAINDATAFILE) as f:
        line = f.readline()
        line = line.strip()
        data = [float(v) for v in line.split(SPACE)]
        max_value = copy.deepcopy(data)
        min_value = copy.deepcopy(data)
        for line in f:
            line = line.strip()
            data = line.split(SPACE)
            for idx, v in enumerate(data):
                v = float(v)
                max_value[idx] = max(v, max_value[idx])
                min_value[idx] = min(v, min_value[idx])
    for name, cur_min, cur_max in zip(header, min_value, max_value):
        print(name, "\t", cur_min, "\t", cur_max)
    return min_value, max_value

def get_percentage(pcg, fname, step):
    header, header_map = read_header(step)
    pcg_value = list()
    min_value = list()
    all_data = list()
    with open(fname) as f:
        idx = 0
        for line in f:
            # idx += 1
            # if idx == 10000:
            #     break
            data = line.strip().split(SPACE)
            all_data.append([float(v) for v in data])
    for idx in range(len(header)):
        all_data.sort(key=lambda v: v[idx])
        pcg_idx = min(int(len(all_data) * pcg), len(all_data))
        pcg_idx = max(pcg_idx, 1)
        pcg_value.append(all_data[pcg_idx - 1][idx])
        min_value.append(all_data[0][idx])

    for name, cur_min, cur_pcg_data in zip(header, min_value, pcg_value):
        print(name, "\t", cur_min, "\t", cur_pcg_data)
    return min_value, pcg_value

def save_pcg_bound_value(min_value, pcg_value, upper_bound_value):
    with open("data/normalize_info", "w") as f:
        f.write(" ".join([str(v) for v in min_value]) + " ")
        f.write(" ".join([str(v) for v in pcg_value]) + " ")
        f.write(" ".join([str(v) for v in upper_bound_value]) + "\n")

def normalize_data(step):
    min_value, pcg_value = get_percentage(0.999, get_combined_train_data_file(step), step)
    min_value, upper_bound_value = get_percentage(0.9999, get_combined_train_data_file(step), step)
    save_pcg_bound_value(min_value, pcg_value, upper_bound_value)
    for ifile_name, ofile_name in [[get_combined_train_data_file(step), get_normalized_train_data_file(step)], [get_combined_test_data_file(step), get_normalized_test_data_file(step)]]:
    # for ifile_name, ofile_name in [[TESTDATAFILE, NORMALIZEDTESTDATAFILE], ]:
        ifile = open(ifile_name)
        with open(ofile_name, "w") as f:
            for line in ifile:
                line = line.strip()
                data = [float(v) for v in line.split(SPACE)]
                new_data = list()
                for v, cur_min, cur_max, upper_bound in zip(data[:-1], min_value[:-1], pcg_value[:-1], upper_bound_value[:-1]):
                # for v, cur_min, cur_max in zip(data, min_value, pcg_value):
                    if v > upper_bound:
                        v = upper_bound
                    if cur_max - cur_min < 1.2:
                        new_data.append(max(v - cur_min, 0.0))
                    else:
                        new_data.append(max((v - cur_min) / (cur_max - cur_min), 0.0))
                    # if cur_max - cur_min < 1.2:
                    #     new_data.append(max(v, 0.0))
                    # elif v > cur_max:
                    #     new_data.append(1.0)
                    # else:
                    #     new_data.append(max((v - cur_min) / (cur_max - cur_min), 0.0))
                if data[-1] > upper_bound_value[-1]:
                    new_data.append(upper_bound_value[-1])
                else:
                    new_data.append(data[-1])
                f.write(SPACE.join([str(v) for v in new_data])+"\n")
        ifile.close()

def draw_point_pic():
    header, header_map = read_header()
    for idx in range(len(header) - 1):
        all_idx_data = list()
        all_target_data = list()
        with open(TRAINDATAFILE) as f:
            ttt = 0
            for line in f:
                # ttt += 1
                # if ttt > 10000:
                #     break
                line = line.strip()
                data = line.split(SPACE)
                all_idx_data.append(float(data[idx]))
                all_target_data.append(float(data[-1]))
        # print (all_idx_data)
        # print (all_target_data)
        plt.plot(all_idx_data, all_target_data, 'ro', label='Original data')
        plt.title(header[idx])
        # plt.legend()
        plt.savefig("/home/zoul15/pcshareddir/gnuresult/point_pic_{}.png".format(header[idx]))
        print ("plot figure : {}", "/home/zoul15/pcshareddir/gnuresult/point_pic_{}.png".format(header[idx]))
        plt.clf()

def combine_data(step):
    header, header_map = read_header()
    prefix = "next_turn_winrate_"
    start_idx = header_map[prefix + "0"]
    end_idx = len(header) - 1
    STEP = step
    for ifile_name, ofile_name in [[TRAINDATAFILE, get_combined_train_data_file(step)], [TESTDATAFILE, get_combined_test_data_file(step)]]:
        ifile = open(ifile_name)
        with open(ofile_name, "w") as f:
            idx = 0
            for line in ifile:
                # idx += 1
                # print (idx)
                # if idx == 10000:
                #     break
                data = line.strip().split(SPACE)
                write_list = data[:start_idx]
                for i in range(start_idx, end_idx):
                    if (i - start_idx) % STEP == 0:
                        tmp_total = float(data[i])
                        for j in range(1, min(STEP, end_idx - i)):
                            tmp_total += float(data[i + j])
                        write_list.append(str(tmp_total))
                write_list.append(data[-1])
                f.write(SPACE.join(write_list) + "\n")
        ifile.close()

def write_schema(step):
    header, header_map = read_header()
    with open(get_train_data_schema_file(step), "w") as f:
        prefix = "next_turn_winrate_"
        start_idx = header_map[prefix + "0"]
        end_idx = len(header) - 1
        target_header = list()
        for i in range(start_idx):
            target_header.append(header[i])
        for i in range(start_idx, end_idx):
            if (i - start_idx) % step == 0:
                target_header.append(header[i])
        target_header.append(header[-1])
        f.write("\n".join(target_header)+"\n")

if __name__=="__main__":
    # check_odds()
    # get_data_range()
    # normalize_data()
    # draw_point_pic()
    step = 1
    write_schema(step)
    combine_data(step)
    normalize_data(step)
