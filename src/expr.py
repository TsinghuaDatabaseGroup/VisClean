from src.entity_matching import EntityMatching



if __name__ == '__main__':
    '''
    :Run EM model first to get the predict data
    :return: 返回EM预测的数据
    '''
    print("Set variable")
    path = '/Users/yuyu/Project/VisClean/dataset/DBConf/expr_tmp'
    ltable_path = path + '/DBPublications-input_id.csv'
    rtable_path = path + '/DBPublications-input_id.csv'
    output_path = path
    key_attr = 'Title'
    l_output_attrs = r_output_attrs = ['Title', 'Authors', 'Venue', 'Year']
    attrs_from_table = []
    for var in l_output_attrs:
        attrs_from_table.append('ltable_' + var)
    for var in r_output_attrs:
        attrs_from_table.append('rtable_' + var)

    print("Left Table & Right Table Path = ", ltable_path)
    myEm = EntityMatching(ltable_path, rtable_path, output_path, key_attr,
                    l_output_attrs, r_output_attrs, attrs_from_table,
                    is_blocking=True, is_save_candidate_feature = True, is_need_label = False)

    myEm.entity_matching()