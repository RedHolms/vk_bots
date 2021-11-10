def remove_char_by_index(string: str, index: int):
    return string[:index] + string[index+1:]

def split_msg_to_params(msg: str, paramsSpliter: str = ' ', stringMark: str = '"') -> list:
    msg, paramsSpliter, stringMark = str(msg), str(paramsSpliter), str(stringMark)

    final_list = []
    
    isInString = False
    lastSpliterI = 0
    i = 0
    for char in msg:
        if char == stringMark:
            isInString = not isInString
            msg = remove_char_by_index(msg, i)
            i -= 1
        elif char == paramsSpliter:
            if not isInString:
                final_list.append(msg[lastSpliterI:i])
                lastSpliterI = i + 1
        if i == msg.__len__() - 1:
            final_list.append(msg[lastSpliterI:])
        i += 1
    del i

    return final_list

def check_params(expectedParams: list, receivedParams: list):
    i = 0
    for i in range(0, expectedParams.__len__()):
        expectedParam = expectedParams[i]
        if len(receivedParams) - 1 < i:
            if expectedParam['optimal']:
                receivedParams.insert(i, expectedParam['default'])
            else:
                return receivedParams, False, i
        i += 1
        continue
    del i

    return receivedParams, True, -1