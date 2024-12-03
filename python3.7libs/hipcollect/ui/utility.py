
def get_human_readable(size):
    suffixes = ["bytes", "KB", "MB", "GB", "TB", "PB"]
    idx = 0
    while size >= 1024:
        size /= 1024
        idx += 1
    if idx == 0:
        return "{:.0f} {}".format(size, suffixes[idx])
    return "{:.2f} {}".format(size, suffixes[idx])


def clean_dirname(dirname):
    dirname = dirname.replace(":", "")
    if dirname[0] == '/':  # remove leading slash for os.path.join to work properly
        dirname = dirname[1:]
    return dirname
    
def return_connected_refs(tree_list,tree_list_parms,item,indexes):
    index_of_first_parent_parm = indexes[0] #here we get a first found parameter as a start for recursive selection
    item_parm_from_index = tree_list_parms.itemFromIndex(index_of_first_parent_parm)
    parm_stored_ref_indexes = item_parm_from_index.data(5,0)
    '''finally we get a list of all refs this parameter points to, these refs are
    considered to be connected refs, like sequences or udims'''
    
    childs = set()
    all_parm_indexes = set()
    all_parm_indexes.update(indexes)
    for index in parm_stored_ref_indexes: #select all refs linked with current selected ref
        child = tree_list.itemFromIndex(index)
        childs.add(child)
        all_parm_indexes.update(child.data(4,0)) #update parm indexes list from newly selected refs
    
    parm_items = set()
    parm_items.add(item_parm_from_index)
    all_refs = set()
    all_refs.update(parm_stored_ref_indexes)
    tree_list_parms.clearSelection()
    for index in all_parm_indexes: #select all parms from an updated list
        parm_item = tree_list_parms.itemFromIndex(index)
        tree_list_parms.scrollToItem(parm_item)
        parm_items.add(parm_item)
        all_refs.update(parm_item.data(5,0))
        
    for index in all_refs: #select all refs from an updated parm list again. Loop ends (I hope this is enough)
        child = tree_list.itemFromIndex(index)
        childs.add(child)
    return childs,parm_items
    
def return_connected_parms(tree_list,tree_list_parms,item):
    indexes = item.data(5,0) #each parameter stores a list of refs it points to, here we read this list
    index_of_first_child_ref = indexes[0] #here we get a first found ref as a start for recursive selection
    item_ref_from_index = tree_list_parms.itemFromIndex(index_of_first_child_ref)
    ref_stored_parm_indexes = item_ref_from_index.data(4,0)
    '''finally we get a list of all parms pointing to this ref, these parms are
    considered to be connected parms, as they point to the same refs'''
    
    parm_items = set()
    parm_items.add(item)
    all_ref_indexes = set()
    all_ref_indexes.update(indexes)
    for index in ref_stored_parm_indexes: #select all parms linked with current selected parm
        item_from_index = tree_list_parms.itemFromIndex(index)
        parm_items.add(item_from_index)
        all_ref_indexes.update(item_from_index.data(5,0)) #update ref list from newly selected parms

    childs = set()
    childs.add(item_ref_from_index)
    all_parms = set()
    all_parms.update(ref_stored_parm_indexes)
    tree_list.clearSelection()
    for index in all_ref_indexes: #select all refs from an updated list
        list_item = tree_list.itemFromIndex(index)
        tree_list.scrollToItem(list_item)
        childs.add(list_item)
        all_parms.update(list_item.data(4,0))
        
    for index in all_parms: #select all parms from an updated ref list again. Loop ends (I hope this is enough)
        item_from_index = tree_list_parms.itemFromIndex(index)
        parm_items.add(item_from_index)
    return parm_items,childs