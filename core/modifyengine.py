class ModifyEngine:
    def diff_diff_dict(originaldict:dict[str,dict[str,tuple]],editeddict:dict[str,dict[str,str]])->dict[str,dict[str,tuple]]: #想要对文件做什么改动
        #dict[section][key]=(value,type)
        logger.debug("start diff_diff_dict")
        logger.debug(f"original={originaldict}")
        logger.debug(f"edited={editeddict}")
        result={}
        for section,keys in editeddict.items():
            result[section]={}
            if section in originaldict:
                for key,value in keys.items():
                    if key in originaldict[section]:
                        if originaldict[section][key][1]==enumtypes.DiffType.REMOVED:
                            result[section][key]=(value,enumtypes.DiffType.ADD)
                            logger.debug(f"current modi: section:{section}, key={key}, newvalue={value}, type={result[section][key][1]}")
                        elif originaldict[section][key][0]!=editeddict[section][key]:
                            result[section][key]=(value,enumtypes.DiffType.MODIFIED)
                            logger.debug(f"current modi: section:{section}, key={key}, newvalue={value}, type={result[section][key][1]}")
                        del originaldict[section][key]
                    else:
                        result[section][key]=(value,enumtypes.DiffType.ADDED)
                        logger.debug(f"current modi: section:{section}, key={key}, newvalue={value}, type={result[section][key][1]}")
                        
                for key,status in originaldict[section].items():
                    value,state=status
                    if state==enumtypes.DiffType.REMOVED:
                        continue
                    result[section][key]=(value,enumtypes.DiffType.REMOVED)
                    logger.debug(f"current modi: section:{section}, key={key}, newvalue={value}, type={result[section][key][1]}")
                del originaldict[section]
            else:
                #new section and new config
                for key , value in keys.items():
                    result[section][key]=(value,enumtypes.DiffType.ADDED)
                    logger.debug(f"current modi: section:{section}, key={key}, newvalue={value}, type={result[section][key][1]}")
        for section,keys in originaldict.items():
            result[section]={}
            for key,status in keys.items():
                value,_=status
                result[section][key]=(value,enumtypes.DiffType.REMOVED)
                logger.debug(f"current modi: section:{section}, key={key}, newvalue={value}, type={result[section][key][1]}")
        logger.debug(f"this should be empty:{originaldict}")
        return result
             

    def modify_string_by_diff(content,modifydict:dict[str,dict[str]])->str:
        result=[]
        lines=content.splitlines()
        current_section=None
        logger.debug(f"start to sync file, modification needed to be made:{modifydict}")
        for line in lines:
            line=line.strip()
            logger.debug(f"line has {line}")
            if line.startswith('[') and line.endswith(']'):
                if current_section in modifydict:
                    for key,status in modifydict[current_section].items():
                        newvalue,state=status
                        logger.debug(f"adding new config section:{current_section},key:{key},value:{newvalue}")
                        result.append(f"{key} = {newvalue}")
                    del modifydict[current_section]            
                current_section=line[1:-1]
                logger.debug(f"new section:{current_section}")
                result.append(f"{line}")
            elif '=' in line:             
                key,value =line.split('=',1)
                key=key.strip()
                value=value.strip()
                if current_section in modifydict and key in modifydict[current_section]:
                    newvalue,state= modifydict[current_section][key]
                    if state==enumtypes.DiffType.ADDED:
                        logger.error(f"unexpected add:section={current_section},key={key},value={newvalue}")
                    elif state==enumtypes.DiffType.REMOVED:
                        logger.debug(f"removed :section={current_section},key={key},value={newvalue}")
                        pass
                    elif state==enumtypes.DiffType.MODIFIED:
                        result.append(f"{key} = {newvalue}")
                        logger.debug(f"modified :section={current_section},key={key},value={newvalue}")
                    else:
                        logger.critical(f"unexpacted type")
                    del modifydict[current_section][key]
                else:
                    result.append(line)
        if current_section in modifydict:
            for key,status in modifydict[current_section].items():
                newvalue,state=status
                logger.debug(f"adding new config section:{current_section},key:{key},value:{newvalue}")
                result.append(f"{key} = {newvalue}")
            del modifydict[current_section]             
        current_section = None
        
        for missing_section,status in modifydict.items():
            result.append(f"[{missing_section}]")
            logger.debug(f"currrent missing section:[{missing_section}]")
            for key, status in status.items():
                newvalue,state=status
                result.append(f"{key} = {newvalue}")
                
        return "\n".join(result)
            

    def compare_diff_dict_2comparedto1(file1_data:dict, file2_data:dict):
        result = {}
        logger.info("start compare diff by dict")
        # Compare sections and keys
        for section in set(file1_data.keys()).union(file2_data.keys()):
            result[section] = {}
            if section in file1_data and section in file2_data:
                for key in set(file1_data[section].keys()).union(file2_data[section].keys()):
                    if key in file1_data[section] and key in file2_data[section]:
                        if file1_data[section][key] == file2_data[section][key]:
                            pass
                            #result[section][key] = (enumerate.DiffType.SAME, file1_data[section][key])
                        else:
                            result[section][key] = (enumtypes.DiffType.MODIFIED, file1_data[section][key], file2_data[section][key])
                    elif key in file1_data[section]:
                        result[section][key] = (enumtypes.DiffType.REMOVED, file1_data[section][key])
                    elif key in file2_data[section]:
                        result[section][key] = (enumtypes.DiffType.ADDED, file2_data[section][key])
            elif section in file1_data:
                for key in file1_data[section]:
                    result[section][key] = (enumtypes.DiffType.REMOVED, file1_data[section][key])
            elif section in file2_data:
                for key in file2_data[section]:
                    result[section][key] = (enumtypes.DiffType.ADDED, file2_data[section][key])
        #logger.debug(result)
        return result


