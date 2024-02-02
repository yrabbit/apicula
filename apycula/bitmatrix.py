
def fliplr(bmp):
    """
    Flips the entries in each row in the left/right direction.
    Returns a new matrix.
    """
    return [row[::-1] for row in bmp]

def flipud(bmp):
    """
    Reverse the order of elements in each column (up/down).
    Returns a refence.
    """
    return bmp[::-1]

def vstack(bmp_0, bmp_1):
    """
    Stack matrices in sequence vertically (row wise).
    Returns a reference.
    """
    return [*bmp_0, *bmp_1]

def hstack(bmp_0, bmp_1):
    """
    Stack matrices in sequence horizontally (column wise).
    Returns a new matrix.
    """
    return [bmp[0] + bmp[1] for bmp in zip(bmp_0, bmp_1)]

def shape(bmp):
    """
    Return the shape of a matrix.
    """
    return [len(bmp), len(bmp[0])]

def ones(rows, cols):
    """
    Returns a new matrix of given shape, filled with ones.
    """
    return [[1] * cols for i in range(rows)]

def zeros(rows, cols):
    """
    Returns a new matrix of given shape, filled with zeros.
    """
    return [[0] * cols for i in range(rows)]

def packbits(bmp, axis = None):
    """
    Packs the elements of a bitmap into bytes.
    [1, 1, 0, 0, 0] -> [24]  # [5'b11000]
    Returns a list of bytes.
    """
    byte_list = []
    if not axis:
        for bmp_r in bmp:
            for col in range(shape(bmp)[1] // 8):
                bcol = col << 3
                byte_list.append((bmp_r[bcol] << 7) + (bmp_r[bcol + 1] << 6) + (bmp_r[bcol + 2] << 5) +
                    (bmp_r[bcol + 3] << 4) + (bmp_r[bcol + 4] << 3) + (bmp_r[bcol + 5] << 2) +
                    (bmp_r[bcol + 6] << 1) + bmp_r[bcol + 7])
    else:
        for bmp_r in bmp:
            byte_list.append([])
            byte_list_r = byte_list[-1]
            for col in range(shape(bmp)[1] // 8):
                bcol = col << 3
                byte_list_r.append((bmp_r[bcol] << 7) + (bmp_r[bcol + 1] << 6) + (bmp_r[bcol + 2] << 5) +
                    (bmp_r[bcol + 3] << 4) + (bmp_r[bcol + 4] << 3) + (bmp_r[bcol + 5] << 2) +
                    (bmp_r[bcol + 6] << 1) + bmp_r[bcol + 7])
    return byte_list

def xor(bmp_0, bmp_1):
    """
    Bitwise XOR
    Returns a new matrix
    """
    return [[ vals[0] ^ vals[1]for vals in zip(row[0], row[1])] for row in zip(bmp_0, bmp_1)]

def histogram(lst, bins):
    """
    Compute the histogram of a list.
    Returns a list of counters.
    """
    l_bins = len(bins) - 1
    r_lst = [0] * l_bins
    for val in lst:
        for i in range(l_bins):
            if val in range(bins[i], bins[i + 1]) or (i == l_bins - 1 and val == bins[-1]):
                r_lst[i] += 1
    return r_lst

def any(bmp):
    """
    Test whether any matrix element evaluates to True.
    """
    for row in bmp:
        for val in row:
            if val:
                return True
    return False

def nonzero(bmp):
    """
    Return the indices of the elements that are non-zero.
    """
    res = ([], [])
    for ri, row in enumerate(bmp):
        for ci, val in enumerate(row):
            if val:
                res[0].append(ri)
                res[1].append(ci)
    return res
