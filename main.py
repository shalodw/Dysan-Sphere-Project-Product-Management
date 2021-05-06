import re
import pprint
import logging
import json
logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')
logging.disable(logging.CRITICAL)

def data_import() :
    data_dict = {}
    # dysanRegex is for data like '[A1] 铁块 60A1 60A'
    # basicRegex is for data like '[A1] 铁块'
    dysanRegex = re.compile(r'(\[.+\]) (.+) (.+) (.+)')
    basicRegex = re.compile(r'(\[.+\]) (.+)')
    # singleRegex is for data like '[A]'
    # firstRegex is for data in level 1
    # secondRegex, thirdRegex... is the same
    singleRegex = re.compile(r'\[[A-W]0\]')
    firstRegex = re.compile(r'\[[A-W]1\]|\[Fc\]')
    secondRegex = re.compile(r'\[[A-W]2\]')
    thirdRegex = re.compile(r'\[[A-W]3\]')
    fourthRegex = re.compile(r'\[[A-W]4\]')
    fifthRegex = re.compile(r'\[[A-W]5\]')
    matrixRegex = re.compile(r'\[Z.\]')
    buildingRegex = re.compile(r'\[[A-Z][A-Z]\]')
    Level = [(singleRegex, 0), (firstRegex, 1), (secondRegex, 2), (thirdRegex, 3), (fourthRegex, 4), (fifthRegex, 5), (matrixRegex, 'z'), (buildingRegex, 'x')]

    data = open('database.txt', encoding='utf-8', errors='ignore')
    # For each line, extract the data and store them in a dict
    for line in data :
        line = line.rstrip()
        converted_line = dysanRegex.search(line)
        if converted_line == None :
            converted_line = basicRegex.search(line)
            # Use regex to determine the level of the unit
            for regex in Level :
                if regex[0].search(line) != None :
                    data_dict[converted_line.group(1)] = {'name': converted_line.group(2), 'level': regex[1]}
                    break
            continue

        for regex in Level :
            if regex[0].search(line) != None :
                data_dict[converted_line.group(1)] = {'name': converted_line.group(2), 'level': regex[1],
                                                      'output': converted_line.group(3), 'demand': converted_line.group(4)}
                break

    logging.debug(f'data_dict: {pprint.pformat(data_dict)}')
    # Further process the data from 'output': '6Z4', 'demand': '12I3;6B5' to 'output': [('20', 'C3')], 'demand': [('20', 'J1'), ('100', 'G1')]
    for key, value in data_dict.items() :
        # Use regex to detect and separate patterns like 12I3, 8B5
        unitRegex = re.compile(r'(\d+\.\d|\d+)([A-Z][0-9]|[A-Z][A-Z])')
        if len(value) == 4 :
            pr_output = unitRegex.findall(value['output'])
            pr_demand = unitRegex.findall(value['demand'])
            data_dict[key]['output'] = pr_output
            data_dict[key]['demand'] = pr_demand

    logging.debug(f'data_dict_converted: {pprint.pformat(data_dict)}')

    return data_dict


def display(current_data, ref_data) :
    logging.debug(f'current_data: {current_data}')
    ''' current_data is like : {'Z1': 3, 'A1': 4, 'A2': 2}

        ref_data is like :  {'[D2]': {'demand': [('90', 'E1')],
          'level': 2,
          'name': '棱镜',
          'output': [('60', 'D2')]},
          '[D3]': {'demand': [('10', 'E'), ('10', 'H1'), ('20', 'F2')],
          'level': 3,
          'name': '有机晶体',
          'output': [('10', 'D3')]}}'''

    shown_data = {}
    # shown_data should be in {'[A1]': {'demand': 100, 'output': 280}} format
    for key, value in current_data.items() :
        for tup in ref_data[key]['demand'] :
            logging.debug(f"demand: {ref_data[key]['demand']}")
            logging.debug(f'tup: {tup}')
            # ref_data[key]['demand'] is like  [('10', 'E'), ('10', 'H1'), ('20', 'F2')]
            # tup is like ('10', 'E')
            tem_k = f'[{tup[1]}]'
            if tem_k not in shown_data.keys() :
                shown_data[tem_k] = {'demand': 0, 'output': 0}
                shown_data[tem_k]['demand'] = float(tup[0]) * value
            else :
                shown_data[tem_k]['demand'] += float(tup[0]) * value

        for tup in ref_data[key]['output'] :
            logging.debug(f"ouput: {ref_data[key]['output']}")
            logging.debug(f'tup: {tup}')
            tem_k = f'[{tup[1]}]'
            if tem_k not in shown_data.keys() :
                shown_data[tem_k] = {'demand': 0, 'output': 0}
                shown_data[tem_k]['output'] = float(tup[0]) * value
            else :
                shown_data[tem_k]['output'] += float(tup[0]) * value

    # pprint.pprint(shown_data)

    print('\n============ 原材料 ============')
    for key, value in shown_data.items() :
        if ref_data[key]['level'] == 0 :
            print(f"{key} {ref_data[key]['name']} 产出: {value['output']} 消耗: {value['demand']}")

    print('\n============ 一级组件 ============')
    for key, value in shown_data.items() :
        if ref_data[key]['level'] == 1 :
            print(f"{key} {ref_data[key]['name']} 产出: {value['output']} 消耗: {value['demand']}")

    print('\n============ 二级组件 ============')
    for key, value in shown_data.items() :
        if ref_data[key]['level'] == 2 :
            print(f"{key} {ref_data[key]['name']} 产出: {value['output']} 消耗: {value['demand']}")

    print('\n============ 三级组件 ============')
    for key, value in shown_data.items() :
        if ref_data[key]['level'] == 3 :
            print(f"{key} {ref_data[key]['name']} 产出: {value['output']} 消耗: {value['demand']}")

    print('\n============ 四级组件 ============')
    for key, value in shown_data.items() :
        if ref_data[key]['level'] == 4 :
            print(f"{key} {ref_data[key]['name']} 产出: {value['output']} 消耗: {value['demand']}")

    print('\n============ 五级组件 ============')
    for key, value in shown_data.items() :
        if ref_data[key]['level'] == 5 :
            print(f"{key} {ref_data[key]['name']} 产出: {value['output']} 消耗: {value['demand']}")

    print('\n============ 六级组件 ============')
    for key, value in shown_data.items() :
        if ref_data[key]['level'] == 6 :
            print(f"{key} {ref_data[key]['name']} 产出: {value['output']} 消耗: {value['demand']}")

    print('\n============ 矩阵 ============')
    for key, value in shown_data.items() :
        if ref_data[key]['level'] == 'z' :
            print(f"{key} {ref_data[key]['name']} 产出: {value['output']} 消耗: {value['demand']}")

    print('\n============ 建筑 ============')
    for key, value in shown_data.items() :
        if ref_data[key]['level'] == 'x' :
            print(f"{key} {ref_data[key]['name']} 产出: {value['output']} 消耗: {value['demand']}")


def new(my_data) :
    '''Let the user input the stock information, how much output/demand
       my_data is the current dictionary conatining such information'''
    u_input = ''
    print()
    print('输入 Exit 以退出')
    while True :
        try :
            u_input = input('请以 \'产线代码 数量\' 的形式输入数据: ')
            if u_input == 'Exit' :
                break
            u_list = u_input.split()
            # make data like [A2] to A2 in the temporary list in order to filter
            tem_filter = map(lambda x: x.strip('[').strip(']'), my_data.keys())
            if u_list[0] in tem_filter :
                the_key = f'[{u_list[0]}]'
                print(f'\n您确定要替换该数据吗？现有数据为 {the_key}: {my_data[the_key]}')
                choice = input('确定请输入\'Y\': ')
                print()
                if choice == 'Y' :
                    my_data[the_key] = float(u_list[1])
                else :
                    pass
            else :
                the_key = f'[{u_list[0]}]'
                my_data[the_key] = float(u_list[1])
        except :
            continue

    return my_data


def option_board(ref_data) :
    # Write a json reading block
    try :
        with open('previous.json', 'r') as f :
            current_data = json.load(f)
    except FileNotFoundError :
        current_data = {}
    choice = ''
    while choice != 'C' :
        # json saving part
        with open('previous.json', 'w') as f :
            json.dump(current_data, f)
        # Formal Block
        print('\n============ 戴森球计划自动计算程序 ============\nA. 输入新数据\nB. 展示当前产出/消耗\nC. 退出')
        choice = input('\n请选择(A/B/C): ')
        if choice == 'A' :
            tem = new(current_data)
            current_data = tem
        elif choice == 'B' :
            display(current_data, ref_data)
        elif choice == 'C' :
            print('\n谢谢使用！')
            break

def main() :
    option_board(data_import())

if __name__ == '__main__' :
    logging.info('Start of program')
    main()
    logging.info('End of program')
