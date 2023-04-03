import json
def json_to_list(filename):
    assert filename.endswith('.json'), "Not json file given {}".format()

    with open(filename,'r',encoding='utf-8') as f:
        a_list  =  json.loads(f.read())

    return a_list



def list_to_json(a_list, filename):
    assert filename.endswith('.json'), "Not json file given {}".format()

   
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(a_list, f,ensure_ascii=False, indent=4 )




if __name__ =="__main__":
    a = ["abc.xa", 1 ,2 ]

    filename = 'images_data.json'
    list_to_json(a, filename)

    b = json_to_list(filename)

    print("Retrieved list: ", b,type(b))

    

    a = [ ]

    filename = 'image_names.json'
    list_to_json(a, filename)

    b = json_to_list(filename)

    print("Retrieved list: ", b,type(b))







