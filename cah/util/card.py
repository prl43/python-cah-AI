def from_str(c):
    fc = []

    section_idx = 0
    idx = 0
    while idx < len(c):
        last_flag = False
        if idx > len(c)-2:
            last_flag = True
            idx += 1

        if last_flag or c[idx] == "<" and c[idx+1] == ">":
            fc.append(c[section_idx:idx])
            idx += 1
            section_idx = idx+1
        idx += 1

    return fc
